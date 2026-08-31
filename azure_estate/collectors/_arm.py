"""Minimal Azure Resource Manager REST helper.

A few ARI columns come from provider APIs that Resource Graph does not expose
(the Compute SKU catalogue, Compute usage quotas).  Calling ARM directly with
the token we already hold avoids pulling in a management SDK per provider.
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from azure.identity import AzureCliCredential

ARM = "https://management.azure.com"
_SCOPE = "https://management.azure.com/.default"

# ARM throttles (429) and drops connections under a wide fan-out. Without a
# retry the caller sees an exception, treats it as "provider unavailable for
# this subscription" and silently ships a report with empty columns.
_ATTEMPTS = 3
_RETRY_STATUS = frozenset({429, 500, 502, 503, 504})


def _is_transient(exc: Exception) -> bool:
    if isinstance(exc, urllib.error.HTTPError):
        return exc.code in _RETRY_STATUS
    return isinstance(exc, (urllib.error.URLError, TimeoutError, ConnectionError))


def _backoff(exc: Exception, attempt: int) -> float:
    """Honour Retry-After when ARM sends one; otherwise exponential."""
    if isinstance(exc, urllib.error.HTTPError) and exc.headers:
        try:
            return min(float(exc.headers.get("Retry-After")), 60.0)
        except (TypeError, ValueError):
            pass
    return float(2**attempt)


def _get_with_retry(request: urllib.request.Request) -> dict[str, Any]:
    """Perform one GET, retrying throttling and dropped connections."""
    for attempt in range(_ATTEMPTS):
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                return json.load(response)
        except Exception as exc:  # noqa: BLE001 — re-raised unless transient
            if attempt + 1 >= _ATTEMPTS or not _is_transient(exc):
                raise
            time.sleep(_backoff(exc, attempt))
    raise AssertionError("unreachable")  # pragma: no cover


def arm_get(
    credential: AzureCliCredential,
    path: str,
    api_version: str,
    params: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    """GET an ARM collection endpoint, following nextLink pagination.

    Returns the concatenated `value` arrays.  Throttling and dropped
    connections are retried; other errors are raised to the caller, which
    decides whether a provider is simply unavailable for a subscription.
    """
    query = {"api-version": api_version, **(params or {})}
    url = f"{ARM}{path}?{urllib.parse.urlencode(query)}"
    token = credential.get_token(_SCOPE).token
    out: list[dict[str, Any]] = []

    while url:
        request = urllib.request.Request(
            url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"}
        )
        payload = _get_with_retry(request)
        out.extend(payload.get("value", []))
        url = payload.get("nextLink")

    return out
