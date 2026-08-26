"""Credential used to read Azure.

The credential is selected by ``AZE_AUTH_MODE`` (see ``config``):

* ``cli`` (default) — the signed-in Azure CLI user; for interactive/local runs.
* ``managed-identity`` — the host's managed identity (IMDS). This is the mode
  for unattended runs on an Azure VM: no ``az login``, no secrets. With
  ``AZE_CLIENT_ID`` empty it uses the VM's *system-assigned* identity; set it to
  a client ID to select a *user-assigned* one (required when the VM has more
  than one identity, since IMDS cannot tell which to use).
* ``default`` — ``DefaultAzureCredential``: environment variables, then managed
  identity, then the CLI. Convenient, but it hides which identity was used.
"""
from __future__ import annotations

from azure.core.credentials import TokenCredential
from azure.identity import (
    AzureCliCredential,
    DefaultAzureCredential,
    ManagedIdentityCredential,
)

from azure_estate.config import AUTH_MODE, CLIENT_ID, TENANT_ID

_VALID_MODES = ("cli", "managed-identity", "default")
_MI_ALIASES = ("managed-identity", "managed_identity", "msi", "mi")


def is_managed_identity() -> bool:
    """True when the configured mode resolves to the host's managed identity."""
    return (AUTH_MODE or "cli").strip().lower() in _MI_ALIASES


def _client_id() -> str:
    """Client ID of the *user-assigned* identity, or "" for system-assigned.

    ``.env.example`` ships placeholders such as ``<client-id-da-identidade>``;
    left in place they would make IMDS look for an identity that does not exist
    and fail with an opaque error at 3 a.m. Treat them as unset, loudly.
    """
    value = (CLIENT_ID or "").strip()
    if not value:
        return ""
    if value.startswith("<") and value.endswith(">"):
        print(
            f"[AVISO] AZE_CLIENT_ID contém o placeholder '{value}' e será "
            "ignorado; usando a identidade gerenciada atribuída pelo sistema. "
            "Preencha-o apenas para identidade atribuída pelo usuário."
        )
        return ""
    return value


def get_credential() -> TokenCredential:
    """Return the credential configured by ``AZE_AUTH_MODE``."""
    mode = (AUTH_MODE or "cli").strip().lower()

    if mode in _MI_ALIASES:
        # A managed identity is bound to its own tenant; tenant_id is not a
        # valid argument here.
        client_id = _client_id()
        if client_id:
            return ManagedIdentityCredential(client_id=client_id)
        # System-assigned: IMDS resolves the VM's own identity.
        return ManagedIdentityCredential()

    if mode == "default":
        return DefaultAzureCredential(
            managed_identity_client_id=_client_id() or None,
            exclude_interactive_browser_credential=True,
        )

    if mode != "cli":
        raise ValueError(
            f"AZE_AUTH_MODE inválido: '{AUTH_MODE}'. Use um de: "
            f"{', '.join(_VALID_MODES)}."
        )

    return AzureCliCredential(tenant_id=TENANT_ID)
