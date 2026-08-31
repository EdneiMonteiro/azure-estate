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

import threading
import time

from azure.core.credentials import AccessToken, AccessTokenInfo, TokenCredential
from azure.identity import (
    AzureCliCredential,
    DefaultAzureCredential,
    ManagedIdentityCredential,
)

from azure_estate.config import AUTH_MODE, CLIENT_ID, TENANT_ID

_VALID_MODES = ("cli", "managed-identity", "default")
_MI_ALIASES = ("managed-identity", "managed_identity", "msi", "mi")

# Renew this long before expiry, so a long collection never runs out mid-flight.
_REFRESH_MARGIN = 300  # seconds
# The CLI can still fail once (a cold start, a busy machine); retry before
# giving up on a token that hundreds of pending requests depend on.
_ATTEMPTS = 3


class CachingCredential:
    """Cache tokens and serialise acquisition across threads.

    ``AzureCliCredential`` holds no cache: every ``get_token`` spawns
    ``az account get-access-token`` and waits up to 10 s for it. The enrichment
    step fans out over hundreds of subscription/region pairs (16 threads), and
    each ARM call asks for a token, so the inventory used to spawn hundreds of
    CLI processes at once and drown in ``Failed to invoke the Azure CLI``.

    One token per scope serves them all. Acquisition happens under the lock on
    purpose: on a cold cache the whole fan-out waits for a single CLI call
    instead of racing to start its own.
    """

    def __init__(self, inner: TokenCredential) -> None:
        self._inner = inner
        self._lock = threading.Lock()
        self._cache: dict[tuple, AccessToken | AccessTokenInfo] = {}

    # -- internals ----------------------------------------------------------
    @staticmethod
    def _key(kind: str, scopes: tuple[str, ...], options: dict | None) -> tuple:
        options = options or {}
        return (
            kind,
            scopes,
            options.get("tenant_id") or "",
            options.get("claims") or "",
            bool(options.get("enable_cae")),
        )

    def _acquire(self, key: tuple, call):
        now = time.time()
        with self._lock:
            cached = self._cache.get(key)
            if cached is not None and cached.expires_on - now > _REFRESH_MARGIN:
                return cached

            last: Exception | None = None
            for attempt in range(_ATTEMPTS):
                try:
                    token = call()
                except Exception as exc:  # noqa: BLE001 — retried, then re-raised
                    last = exc
                    if attempt + 1 < _ATTEMPTS:
                        time.sleep(1 + attempt)
                else:
                    self._cache[key] = token
                    return token

            assert last is not None
            raise last

    # -- TokenCredential protocol -------------------------------------------
    def get_token(self, *scopes: str, **kwargs) -> AccessToken:
        key = self._key("token", scopes, kwargs)
        return self._acquire(key, lambda: self._inner.get_token(*scopes, **kwargs))

    def get_token_info(self, *scopes: str, options=None) -> AccessTokenInfo:
        inner = getattr(self._inner, "get_token_info", None)
        if inner is None:
            token = self.get_token(*scopes, **(options or {}))
            return AccessTokenInfo(token.token, token.expires_on)
        key = self._key("info", scopes, options)
        return self._acquire(key, lambda: inner(*scopes, options=options))

    def close(self) -> None:
        close = getattr(self._inner, "close", None)
        if close is not None:
            close()

    def __enter__(self) -> "CachingCredential":
        return self

    def __exit__(self, *args) -> None:
        self.close()



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
    """Return the credential configured by ``AZE_AUTH_MODE``.

    The credential is wrapped in :class:`CachingCredential`: the collectors call
    ``get_token`` once per ARM request, from many threads, and an uncached
    credential turns that into one subprocess (CLI) or one IMDS round-trip each.
    """
    return CachingCredential(_build_credential())


def _build_credential() -> TokenCredential:
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
