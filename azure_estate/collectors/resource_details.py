from __future__ import annotations

from typing import Any

import pandas as pd
from azure.identity import AzureCliCredential
from azure.mgmt.resourcegraph import ResourceGraphClient

from azure_estate.cell_format import flatten_cell
from azure_estate.collectors._graph import run_graph_query
from azure_estate.resource_type_configs import ResourceTypeConfig

# Base display-name → KQL field name mapping (injected by the query itself)
_BASE_COLUMNS = [
    ("Subscription",    "_subName"),
    ("Resource Group",  "resourceGroup"),
    ("Nome",            "name"),
    ("Região",          "location"),
]

# Working columns kept on the DataFrame for the enrichment step; they are
# dropped before export.
_ID = "_resource_id"
_SUB_ID = "_subscription_id"
INTERNAL_COLUMNS = (_ID, _SUB_ID)


def _build_kql(config: ResourceTypeConfig) -> str:
    """Build the KQL query for a given resource type config."""
    # Build extend clause for each specific column
    extend_parts = ", ".join(
        [f"_c{i} = {expr}" for i, (_, expr) in enumerate(config.columns)]
        + [f"_r{i} = {expr}" for i, (_, expr) in enumerate(config.raw_columns)]
    )

    # Specific projected fields
    specific_fields = ", ".join(
        [f"_c{i}" for i in range(len(config.columns))]
        + [f"_r{i}" for i in range(len(config.raw_columns))]
    )

    kql = (
        f"Resources\n"
        f"| where type == '{config.resource_type}'\n"
        f"| extend {extend_parts}\n"
        f"| join kind=leftouter (\n"
        f"    ResourceContainers\n"
        f"    | where type == 'microsoft.resources/subscriptions'\n"
        f"    | project subscriptionId, _subName = name\n"
        f") on subscriptionId\n"
        f"| project _subName, subscriptionId, _id = tolower(id), resourceGroup, name, location"
        + (f", {specific_fields}" if specific_fields else "")
    )

    return kql


def _rename_row(row: dict[str, Any], config: ResourceTypeConfig) -> list[dict[str, Any]]:
    """Rename raw KQL output keys to display names.

    Returns one dict per output row: `derive` may expand a single resource
    into several rows (one per node pool, security rule, …).
    """
    base: dict[str, Any] = {
        "Subscription":   row.get("_subName", ""),
        "Resource Group": row.get("resourceGroup", ""),
        "Nome":           row.get("name", ""),
        "Região":         row.get("location", ""),
        _ID:              row.get("_id", ""),
        _SUB_ID:          row.get("subscriptionId", ""),
    }
    for i, (col_name, _) in enumerate(config.columns):
        base[col_name] = flatten_cell(row.get(f"_c{i}", ""))

    if config.derive is None:
        return [base]

    raw = {key: row.get(f"_r{i}") for i, (key, _) in enumerate(config.raw_columns)}
    derived = config.derive(raw)
    if isinstance(derived, dict):
        derived = [derived]
    if not derived:
        derived = [{}]

    return [
        {**base, **{k: flatten_cell(v) for k, v in extra.items()}} for extra in derived
    ]


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

    rows = [r for raw_row in raw for r in _rename_row(raw_row, config)]
    df = pd.DataFrame(rows)

    # Ensure column order: base cols first, then specific cols
    ordered_cols = (
        ["Subscription", "Resource Group", "Nome", "Região"]
        + [col_name for col_name, _ in config.columns]
        + list(config.derived)
        + list(INTERNAL_COLUMNS)
    )
    # Only keep columns that actually exist in the DataFrame
    df = df[[c for c in ordered_cols if c in df.columns]]
    df.sort_values(["Subscription", "Resource Group", "Nome"], inplace=True, ignore_index=True)

    return df
