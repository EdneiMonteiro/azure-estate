"""Minimal Azure Resource Manager REST helper.

A few ARI columns come from provider APIs that Resource Graph does not expose
(the Compute SKU catalogue, Compute usage quotas).  Calling ARM directly with
the token we already hold avoids pulling in a management SDK per provider.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from azure.identity import AzureCliCredential

ARM = "https://management.azure.com"
_SCOPE = "https://management.azure.com/.default"


def arm_get(
    credential: AzureCliCredential,
    path: str,
    api_version: str,
    params: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    """GET an ARM collection endpoint, following nextLink pagination.

    Returns the concatenated `value` arrays.  Errors are raised to the caller,
    which decides whether a provider is simply unavailable for a subscription.
    """
    query = {"api-version": api_version, **(params or {})}
    url = f"{ARM}{path}?{urllib.parse.urlencode(query)}"
    token = credential.get_token(_SCOPE).token
    out: list[dict[str, Any]] = []

    while url:
        request = urllib.request.Request(
            url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"}
        )
        with urllib.request.urlopen(request, timeout=120) as response:
            payload = json.load(response)
        out.extend(payload.get("value", []))
        url = payload.get("nextLink")

    return out
