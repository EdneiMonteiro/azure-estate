from __future__ import annotations

from typing import Any

from azure.identity import AzureCliCredential
from azure.mgmt.resourcegraph import ResourceGraphClient

from azure_estate.collectors._graph import run_graph_query
from azure_estate.collectors.subscriptions import list_active_subscriptions


def list_resource_types(
    credential: AzureCliCredential,
    tenant_id: str,
) -> list[dict[str, Any]]:
    """Return all resource types aggregated across all active subscriptions.

    Uses a single Resource Graph KQL query with pagination.
    """
    subs = list_active_subscriptions(credential, tenant_id)
    if not subs:
        return []

    sub_ids = [s["subscription_id"] for s in subs]
    client = ResourceGraphClient(credential)

    kql = (
        "Resources"
        " | summarize resource_count = count() by type"
        " | order by resource_count desc"
    )

    results: list[dict[str, Any]] = run_graph_query(client, sub_ids, kql)

    # Merge counts across chunks (different subscription batches may return the same type)
    merged: dict[str, int] = {}
    for row in results:
        merged[row["type"]] = merged.get(row["type"], 0) + row["resource_count"]

    return [{"type": t, "resource_count": c} for t, c in merged.items()]
