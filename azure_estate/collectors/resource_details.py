from __future__ import annotations

from typing import Any

import pandas as pd
from azure.identity import AzureCliCredential
from azure.mgmt.resourcegraph import ResourceGraphClient

from azure_estate.collectors._graph import run_graph_query
from azure_estate.resource_type_configs import ResourceTypeConfig

# Base display-name → KQL field name mapping (injected by the query itself)
_BASE_COLUMNS = [
    ("Subscription",    "_subName"),
    ("Resource Group",  "resourceGroup"),
    ("Nome",            "name"),
    ("Região",          "location"),
]


def _build_kql(config: ResourceTypeConfig) -> str:
    """Build the KQL query for a given resource type config."""
    # Build extend clause for each specific column
    extend_parts = ", ".join(
        f"_c{i} = {expr}"
        for i, (_, expr) in enumerate(config.columns)
    )

    # Specific projected fields
    specific_fields = ", ".join(f"_c{i}" for i in range(len(config.columns)))

    kql = (
        f"Resources\n"
        f"| where type == '{config.resource_type}'\n"
        f"| extend {extend_parts}\n"
        f"| join kind=leftouter (\n"
        f"    ResourceContainers\n"
        f"    | where type == 'microsoft.resources/subscriptions'\n"
        f"    | project subscriptionId, _subName = name\n"
        f") on subscriptionId\n"
        f"| project _subName, resourceGroup, name, location"
        + (f", {specific_fields}" if specific_fields else "")
    )

    return kql


def _rename_row(row: dict[str, Any], config: ResourceTypeConfig) -> dict[str, Any]:
    """Rename raw KQL output keys to display names."""
    result: dict[str, Any] = {
        "Subscription":   row.get("_subName", ""),
        "Resource Group": row.get("resourceGroup", ""),
        "Nome":           row.get("name", ""),
        "Região":         row.get("location", ""),
    }
    for i, (col_name, _) in enumerate(config.columns):
        result[col_name] = row.get(f"_c{i}", "")
    return result


def query_resource_type(
    credential: AzureCliCredential,
    subscription_ids: list[str],
    config: ResourceTypeConfig,
) -> pd.DataFrame:
    """Return a DataFrame with all resources of the given type across all subscriptions.

    Returns an empty DataFrame if no resources are found.
    """
    if not subscription_ids:
        return pd.DataFrame()

    client = ResourceGraphClient(credential)
    kql = _build_kql(config)

    raw = run_graph_query(client, subscription_ids, kql)

    if not raw:
        return pd.DataFrame()

    rows = [_rename_row(r, config) for r in raw]
    df = pd.DataFrame(rows)

    # Ensure column order: base cols first, then specific cols
    ordered_cols = (
        ["Subscription", "Resource Group", "Nome", "Região"]
        + [col_name for col_name, _ in config.columns]
    )
    # Only keep columns that actually exist in the DataFrame
    df = df[[c for c in ordered_cols if c in df.columns]]
    df.sort_values(["Subscription", "Resource Group", "Nome"], inplace=True, ignore_index=True)

    return df
