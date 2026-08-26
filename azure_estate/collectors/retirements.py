"""Service retirements affecting each resource.

ARI adds two columns to every sheet — the retiring feature and its date —
sourced from Advisor: `advisorresources` says *which* resources are flagged,
and the Advisor metadata catalogue translates the recommendation id into the
feature name and retirement date.
"""
from __future__ import annotations

from typing import Any

from azure.identity import AzureCliCredential
from azure.mgmt.resourcegraph import ResourceGraphClient

from azure_estate.collectors._arm import arm_get
from azure_estate.collectors._graph import run_graph_query

RETIREMENT_COLUMNS: list[str] = ["Retiring Feature", "Retirement Date"]

_FLAGGED_KQL = (
    "advisorresources"
    " | where properties.extendedProperties.recommendationSubCategory == 'ServiceUpgradeAndRetirement'"
    " | where tostring(properties.category) has 'HighAvailability'"
    " | where isempty(properties.tracked)"
    " | where properties.platformState == 'New'"
    " | extend rid = tolower(tostring(properties.resourceMetadata.resourceId))"
    " | project rid, serviceId = tostring(properties.recommendationTypeId)"
)

_METADATA_FILTER = (
    "recommendationCategory eq 'HighAvailability'"
    " and recommendationSubCategory eq 'ServiceUpgradeAndRetirement'"
    " and retirementDate ge '2024-01-01'"
)


def _catalog(credential: AzureCliCredential) -> dict[str, tuple[str, str]]:
    """Map recommendation type id -> (retiring feature, retirement date)."""
    try:
        metadata = arm_get(
            credential,
            "/providers/Microsoft.Advisor/metadata",
            "2025-01-01",
            {"$filter": _METADATA_FILTER, "$expand": "ibiza"},
        )
    except Exception:  # noqa: BLE001 — Advisor metadata is best effort
        return {}

    out: dict[str, tuple[str, str]] = {}
    for entry in metadata:
        for value in entry.get("properties", {}).get("supportedValues", []) or []:
            retirement = (value.get("sourceProperties") or {}).get("serviceRetirement") or {}
            key = str(value.get("id", "")).lower()
            if key:
                out[key] = (
                    retirement.get("retirementFeatureName", ""),
                    retirement.get("retirementDate", ""),
                )
    return out


def fetch_retirements(
    credential: AzureCliCredential,
    subscription_ids: list[str],
) -> dict[str, dict[str, str]]:
    """Return {lowercase resource id: {column: value}} for flagged resources.

    A resource can be flagged by more than one recommendation, so values are
    joined the way ARI concatenates them.
    """
    catalog = _catalog(credential)
    if not catalog:
        return {}

    client = ResourceGraphClient(credential)
    try:
        flagged: list[dict[str, Any]] = run_graph_query(client, subscription_ids, _FLAGGED_KQL)
    except Exception:  # noqa: BLE001
        return {}

    grouped: dict[str, tuple[list[str], list[str]]] = {}
    for row in flagged:
        entry = catalog.get(str(row.get("serviceId", "")).lower())
        if not entry:
            continue
        feature, date = entry
        features, dates = grouped.setdefault(row.get("rid", ""), ([], []))
        if feature and feature not in features:
            features.append(feature)
        if date and date not in dates:
            dates.append(date)

    return {
        rid: {"Retiring Feature": ", ".join(features), "Retirement Date": ", ".join(dates)}
        for rid, (features, dates) in grouped.items()
        if rid
    }
