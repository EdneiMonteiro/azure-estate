"""Upload generated reports to an Azure Blob Storage container.

Authentication uses Microsoft Entra ID (OAuth) — no account keys, no connection
strings. On an Azure VM this is the VM's managed identity (``AZE_AUTH_MODE=
managed-identity``); locally it is the signed-in Azure CLI user.

The identity needs the **Storage Blob Data Contributor** role on the container
(or on the storage account). Note this is a *different* role from the one the
file-share uploader requires.

The target is ``https://<account>.blob.core.windows.net/<container>/<prefix>``.
"""
from __future__ import annotations

import pathlib
from typing import Iterable

from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient


class BlobUploader:
    """Uploads local files as block blobs into a container.

    Unlike the file-share uploader there is no ``key`` auth mode: managed
    identity is the intended path and account keys are a liability on an
    unattended VM.
    """

    def __init__(
        self,
        account_name: str,
        container: str,
        prefix: str = "",
        credential=None,
        create_container: bool = False,
    ) -> None:
        self._account_name = account_name
        self._container = container
        # Normalize to forward slashes; blob names never use backslashes.
        self._prefix = prefix.replace("\\", "/").strip("/")
        self._explicit_credential = credential
        self._create_container = create_container

    # -- internal helpers ---------------------------------------------------
    def _credential(self):
        if self._explicit_credential is not None:
            return self._explicit_credential
        # Reuse the same identity selection as the rest of the tool, so that
        # AZE_AUTH_MODE=managed-identity applies to the upload as well.
        from azure_estate.exporters.file_share import _upload_credential

        return _upload_credential()

    def _container_client(self):
        account_url = f"https://{self._account_name}.blob.core.windows.net"
        service = BlobServiceClient(
            account_url=account_url, credential=self._credential()
        )
        container = service.get_container_client(self._container)
        if self._create_container:
            try:
                container.create_container()
            except ResourceExistsError:
                pass
        return container

    def _blob_name(self, file_name: str) -> str:
        return f"{self._prefix}/{file_name}" if self._prefix else file_name

    # -- public API ---------------------------------------------------------
    @property
    def target_uri(self) -> str:
        base = f"https://{self._account_name}.blob.core.windows.net/{self._container}"
        return f"{base}/{self._prefix}" if self._prefix else base

    def upload_files(self, files: Iterable[pathlib.Path]) -> list[str]:
        """Upload each file, overwriting existing blobs. Returns blob names."""
        files = [f for f in files if f.is_file()]
        if not files:
            return []

        container = self._container_client()

        uploaded: list[str] = []
        for file_path in files:
            blob_name = self._blob_name(file_path.name)
            with file_path.open("rb") as handle:
                container.upload_blob(name=blob_name, data=handle, overwrite=True)
            uploaded.append(blob_name)
        return uploaded

    def upload_directory(
        self, local_dir: str | pathlib.Path, pattern: str = "*.xlsx"
    ) -> list[str]:
        """Upload every file matching *pattern* in *local_dir* (non-recursive)."""
        local_path = pathlib.Path(local_dir)
        if not local_path.is_dir():
            return []
        return self.upload_files(sorted(local_path.glob(pattern)))
