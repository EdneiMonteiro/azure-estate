"""Upload generated reports to an Azure File Share using Microsoft Entra ID.

Authentication uses the signed-in user's identity (OAuth over REST) — no
storage account keys or connection strings. This requires:

* Data-plane RBAC on the storage account, e.g. the built-in role
  **Storage File Data Privileged Contributor** (matches ``token_intent="backup"``).
* The account allowing OAuth (Microsoft Entra) authentication for file shares.

The target is ``\\\\<account>.file.core.windows.net\\<share>\\<path>``.
"""
from __future__ import annotations

import pathlib
from typing import Iterable

from azure.core.exceptions import ClientAuthenticationError, ResourceExistsError
from azure.identity import (
    AzureCliCredential,
    AzurePowerShellCredential,
    ChainedTokenCredential,
)
from azure.storage.fileshare import ShareClient, ShareDirectoryClient


def _signed_in_user_credential() -> ChainedTokenCredential:
    """Credential for the signed-in user (Azure CLI or Azure PowerShell).

    A plain ``DefaultAzureCredential`` is deliberately avoided here: inside
    Azure Cloud Shell it detects the managed-identity endpoint and blocks on
    ``ManagedIdentityCredential`` ("Timeout waiting for token from portal"),
    which aborts the chain before the already-signed-in CLI/PowerShell
    identity is ever tried. Chaining those two directly uses the logged-in
    user and works in Cloud Shell (bash and PowerShell) and local dev alike.
    """
    return ChainedTokenCredential(
        AzureCliCredential(),
        AzurePowerShellCredential(),
    )


class FileShareUploader:
    """Uploads local files to a directory inside an Azure File Share via Entra ID."""

    def __init__(
        self,
        account_name: str,
        share_name: str,
        share_path: str = "",
        credential=None,
    ) -> None:
        self._account_name = account_name
        self._share_name = share_name
        # Normalize to forward slashes and strip leading/trailing separators.
        self._share_path = share_path.replace("\\", "/").strip("/")
        # Use the signed-in user's identity (CLI/PowerShell), not managed identity.
        self._credential = credential or _signed_in_user_credential()

    # -- internal helpers ---------------------------------------------------
    def _share_client(self) -> ShareClient:
        return ShareClient(
            account_url=f"https://{self._account_name}.file.core.windows.net",
            share_name=self._share_name,
            credential=self._credential,
            # Required for OAuth (Microsoft Entra ID) access to Azure file shares.
            token_intent="backup",
        )

    def _ensure_directory(self, share: ShareClient) -> ShareDirectoryClient:
        """Create the (possibly nested) target directory and return its client."""
        if not self._share_path:
            return share.get_directory_client("")

        current = ""
        for segment in self._share_path.split("/"):
            current = f"{current}/{segment}" if current else segment
            directory = share.get_directory_client(current)
            try:
                directory.create_directory()
            except ResourceExistsError:
                pass
        return share.get_directory_client(self._share_path)

    # -- public API ---------------------------------------------------------
    @property
    def target_uri(self) -> str:
        base = f"https://{self._account_name}.file.core.windows.net/{self._share_name}"
        return f"{base}/{self._share_path}" if self._share_path else base

    def upload_files(self, files: Iterable[pathlib.Path]) -> list[str]:
        """Upload each file, overwriting existing ones. Returns uploaded names."""
        files = [f for f in files if f.is_file()]
        if not files:
            return []

        share = self._share_client()
        directory = self._ensure_directory(share)

        uploaded: list[str] = []
        for file_path in files:
            with file_path.open("rb") as handle:
                directory.upload_file(
                    file_name=file_path.name,
                    data=handle,
                )
            uploaded.append(file_path.name)
        return uploaded

    def upload_directory(
        self, local_dir: str | pathlib.Path, pattern: str = "*.xlsx"
    ) -> list[str]:
        """Upload every file matching *pattern* in *local_dir* (non-recursive)."""
        local_path = pathlib.Path(local_dir)
        if not local_path.is_dir():
            return []
        return self.upload_files(sorted(local_path.glob(pattern)))
