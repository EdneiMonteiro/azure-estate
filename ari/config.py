"""Configuração do AzureEstate.

O TENANT_ID é lido da variável de ambiente ``AZURE_TENANT_ID``.
Copie ``.env.example`` para ``.env`` e preencha, ou exporte a variável no shell.
"""
from __future__ import annotations

import os
from pathlib import Path


def _load_dotenv() -> None:
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv()

TENANT_ID = os.environ.get("AZURE_TENANT_ID", "")

# ---------------------------------------------------------------------------
# Azure File Share upload target (used by `main.py --upload`).
# The reports are uploaded to \\<account>.file.core.windows.net\<share>\<path>
# using the signed-in user's Microsoft Entra identity (OAuth over REST).
# ---------------------------------------------------------------------------
STORAGE_ACCOUNT = os.environ.get("ARI_STORAGE_ACCOUNT", "stgtestelogdiag")
FILE_SHARE = os.environ.get("ARI_FILE_SHARE", "ari-bridge")
SHARE_PATH = os.environ.get("ARI_SHARE_PATH", "AzureResourceInventory")
