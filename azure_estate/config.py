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


def _env(name: str, default: str = "") -> str:
    """Read env var *name* (``AZE_*``), falling back to the legacy ``ARI_*`` name.

    The ``ARI_`` prefix was renamed to ``AZE_`` (Azure Estate); the fallback keeps
    existing ``.env`` files working. Remove the fallback once they are migrated.
    """
    legacy = "ARI_" + name[len("AZE_"):] if name.startswith("AZE_") else name
    return os.environ.get(name) or os.environ.get(legacy) or default


# ---------------------------------------------------------------------------
# Azure File Share upload target (used by `main.py --upload`).
# The reports are uploaded to \\<account>.file.core.windows.net\<share>\<path>
# using the signed-in user's Microsoft Entra identity (OAuth over REST).
#
# These are intentionally empty by default so no real resource names are
# committed. Set them in your local .env (git-ignored) or via CLI flags.
# ---------------------------------------------------------------------------
STORAGE_ACCOUNT = _env("AZE_STORAGE_ACCOUNT", "")
FILE_SHARE = _env("AZE_FILE_SHARE", "")
SHARE_PATH = _env("AZE_SHARE_PATH", "")
# Resource group of the storage account (used only by --auth-mode key to list
# keys via ARM). Optional: the Azure CLI can resolve it from the account name.
RESOURCE_GROUP = _env("AZE_RESOURCE_GROUP", "")
# Subscription of the storage account (used only by --auth-mode key). Optional:
# defaults to the Azure CLI's active subscription.
SUBSCRIPTION = _env("AZE_SUBSCRIPTION", "")
# Default upload auth mode: "login" (Entra OAuth) or "key" (account key via ARM).
UPLOAD_AUTH_MODE = _env("AZE_UPLOAD_AUTH_MODE", "login")
