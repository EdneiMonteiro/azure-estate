"""Upload generated reports to an Azure File Share using Microsoft Entra ID.

Authentication uses the signed-in user's identity (OAuth over REST) — no
storage account keys or connection strings. This requires:

* Data-plane RBAC on the storage account, e.g. the built-in role
  **Storage File Data Privileged Contributor** (matches ``token_intent="backup"``).
* The account allowing OAuth (Microsoft Entra) authentication for file shares.

The target is ``\\\\<account>.file.core.windows.net\\<share>\\<path>``.
"""
from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
from datetime import datetime, timezone
from typing import Any, Iterable

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError, ResourceExistsError
from azure.identity import (
    AzureCliCredential,
    AzurePowerShellCredential,
    ChainedTokenCredential,
)
from azure.storage.fileshare import ShareClient, ShareDirectoryClient


# Directories where `az` / `pwsh` typically live. In Azure Cloud Shell the
# Python subprocess spawned by azure-identity does not always inherit a PATH
# that includes these, causing "Failed to invoke the Azure CLI / PowerShell".
# Appending them (non-destructively) lets the credential locate the tools.
_COMMON_TOOL_DIRS: tuple[str, ...] = (
    "/usr/bin",
    "/usr/local/bin",
    "/bin",
    "/opt/az/bin",
    "/opt/microsoft/powershell/7",
    "/usr/local/microsoft/powershell/7",
)


def _ensure_tools_on_path() -> None:
    """Append common Azure tool directories to PATH if they are missing.

    Safe no-op on platforms where these directories don't exist (e.g. Windows).
    """
    existing = os.environ.get("PATH", "")
    parts = existing.split(os.pathsep) if existing else []
    changed = False
    for directory in _COMMON_TOOL_DIRS:
        if directory not in parts and os.path.isdir(directory):
            parts.append(directory)
            changed = True
    if changed:
        os.environ["PATH"] = os.pathsep.join(parts)


def _scope_to_resource(scope: str) -> str:
    """Convert an OAuth scope (…/.default) to an Azure CLI --resource value."""
    resource = scope
    if resource.endswith("/.default"):
        resource = resource[: -len("/.default")]
    return resource.rstrip("/")


class _DirectAzureCliCredential:
    """Reuses the session's ``az`` token by invoking the CLI binary directly.

    ``azure-identity``'s ``AzureCliCredential`` spawns ``/bin/sh -c "az …"`` and
    has been observed to fail with "Failed to invoke the Azure CLI" in some
    Azure Cloud Shell sessions even though ``az`` is installed and on PATH.
    This credential calls the resolved ``az`` binary directly (no shell wrapper)
    and returns the token it already holds — which, unlike an interactive or
    device-code sign-in, satisfies Conditional Access because it is the token
    the compliant Cloud Shell session already obtained.
    """

    def __init__(self) -> None:
        self._az = shutil.which("az") or (
            "/usr/bin/az" if os.path.isfile("/usr/bin/az") else "az"
        )

    def get_token(self, *scopes: str, **kwargs: Any) -> AccessToken:
        if not scopes:
            raise ClientAuthenticationError(message="No scope provided for token.")
        resource = _scope_to_resource(scopes[0])
        cmd = [
            self._az,
            "account",
            "get-access-token",
            "--resource",
            resource,
            "--output",
            "json",
        ]
        tenant = kwargs.get("tenant_id")
        if tenant:
            cmd += ["--tenant", tenant]

        # Cloud Shell's token broker can be slow for non-ARM audiences; allow a
        # generous, overridable timeout.
        try:
            timeout = int(os.environ.get("ARI_AZ_TOKEN_TIMEOUT", "120"))
        except ValueError:
            timeout = 120

        try:
            completed = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=True,
            )
        except FileNotFoundError as exc:
            raise ClientAuthenticationError(
                message=f"Azure CLI not found at '{self._az}'."
            ) from exc
        except subprocess.TimeoutExpired as exc:
            raise ClientAuthenticationError(
                message=(
                    f"Timed out ({timeout}s) invoking the Azure CLI for resource "
                    f"'{resource}'. In Cloud Shell this usually means the token "
                    "broker cannot mint a data-plane token for this audience "
                    "(often a Conditional Access challenge)."
                )
            ) from exc
        except subprocess.CalledProcessError as exc:
            raise ClientAuthenticationError(
                message=f"Azure CLI returned an error: {exc.stderr or exc.stdout}"
            ) from exc

        data = json.loads(completed.stdout)
        token = data["accessToken"]

        # Prefer the epoch field when present; otherwise parse the local string.
        expires_on = data.get("expires_on")
        if expires_on is None:
            raw = data.get("expiresOn", "")
            try:
                expires_on = int(
                    datetime.strptime(raw, "%Y-%m-%d %H:%M:%S.%f").timestamp()
                )
            except ValueError:
                expires_on = int(datetime.now(timezone.utc).timestamp()) + 3600
        return AccessToken(token, int(expires_on))


def _signed_in_user_credential() -> ChainedTokenCredential:
    """Credential for the signed-in user, resilient to broken shells and CA.

    A plain ``DefaultAzureCredential`` is deliberately avoided: inside Azure
    Cloud Shell it blocks on ``ManagedIdentityCredential`` ("Timeout waiting for
    token from portal"), aborting the chain before the signed-in identity is
    tried. Interactive / device-code fallbacks are also avoided because
    Conditional Access policies block them.

    The chain tries, in order:
      1. ``AzureCliCredential`` — azure-identity's shell-based CLI credential.
      2. ``AzurePowerShellCredential`` — azure-identity's PowerShell credential.
      3. ``_DirectAzureCliCredential`` — calls the ``az`` binary directly,
         reusing the compliant session token (works when 1./2. can't spawn a
         subprocess and when CA blocks interactive sign-in).
    """
    _ensure_tools_on_path()
    return ChainedTokenCredential(
        AzureCliCredential(),
        AzurePowerShellCredential(),
        _DirectAzureCliCredential(),
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
