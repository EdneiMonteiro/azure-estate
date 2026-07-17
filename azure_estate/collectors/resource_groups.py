from __future__ import annotations

from typing import Any

from azure.identity import AzureCliCredential
from azure.mgmt.resourcegraph import ResourceGraphClient

from azure_estate.collectors._graph import run_graph_query
from azure_estate.collectors.subscriptions import list_active_subscriptions


def list_resource_groups(
    credential: AzureCliCredential,
    tenant_id: str,
) -> list[dict[str, Any]]:
    """Return all resource groups with their subscription name, location and resource count.

    Uses two Resource Graph queries (RG list + resource count per RG) merged in Python,
    which avoids iterating per subscription and handles any tenant size efficiently.
    """
    subs = list_active_subscriptions(credential, tenant_id)
    if not subs:
        return []

    sub_name_map: dict[str, str] = {s["subscription_id"]: s["name"] for s in subs}
    sub_ids = list(sub_name_map.keys())

    client = ResourceGraphClient(credential)

    # Query 1: all resource groups (name + location)
    kql_rgs = (
        "ResourceContainers"
        " | where type == 'microsoft.resources/subscriptions/resourcegroups'"
        " | project subscriptionId, rgName = name, location"
    )

    # Query 2: resource count per RG (resourceGroup field is always lowercase in Resources)
    kql_counts = (
        "Resources"
        " | summarize resource_count = count() by subscriptionId, rgNameLower = tolower(resourceGroup)"
    )

    rg_rows = run_graph_query(client, sub_ids, kql_rgs)
    count_rows = run_graph_query(client, sub_ids, kql_counts)

    # Build count lookup: (subscription_id, rg_name_lower) → count
    count_map: dict[tuple[str, str], int] = {
        (r["subscriptionId"], r["rgNameLower"]): r["resource_count"]
        for r in count_rows
    }

    results: list[dict[str, Any]] = []
    for rg in rg_rows:
        sub_id = rg["subscriptionId"]
        rg_name = rg["rgName"]
        results.append(
            {
                "subscription_name": sub_name_map.get(sub_id, sub_id),
                "rg_name": rg_name,
                "location": rg["location"],
                "resource_count": count_map.get((sub_id, rg_name.lower()), 0),
            }
        )

    return results
