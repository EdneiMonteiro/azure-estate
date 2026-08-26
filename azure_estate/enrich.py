"""Enrichment of the inventory with data Resource Graph cannot provide.

Resource Graph knows a VM is a `Standard_D4ds_v5`, that it has a network
interface, and nothing else: the hardware behind the size name, the quota left
in that family, the interface's private IP and the retirements announced for
the resource all live in other APIs.  ARI reports those columns, so they are
collected once here and joined onto every sheet.
"""
from __future__ import annotations

import pandas as pd
from azure.identity import AzureCliCredential

from azure_estate.collectors.compute_skus import (
    ALL_SKU_COLUMNS,
    fetch_quota,
    fetch_sku_catalog,
)
from azure_estate.collectors.network_map import NIC_COLUMNS, fetch_network_map
from azure_estate.collectors.resource_details import INTERNAL_COLUMNS, _ID, _SUB_ID
from azure_estate.collectors.retirements import RETIREMENT_COLUMNS, fetch_retirements

QUOTA_COLUMN = "Remaining Quota (vCPUs)"

# Where each sheet keeps the VM size to look up in the SKU catalogue.  AKS
# carries it per node pool row, which is exactly ARI's granularity.
_SIZE_COLUMN: dict[str, str] = {
    "microsoft.compute/virtualmachines": "Tamanho",
    "microsoft.compute/virtualmachinescalesets": "Tamanho",
    "microsoft.containerservice/managedclusters": "Node Pool Size",
}


class Enricher:
    """Holds the cross-resource lookups and applies them to each sheet."""

    def __init__(self, credential: AzureCliCredential, subscription_ids: list[str]) -> None:
        self._credential = credential
        self._subscription_ids = subscription_ids
        self._skus: dict[tuple[str, str], dict[str, str]] = {}
        self._quota: dict[tuple[str, str, str], str] = {}
        self._retirements: dict[str, dict[str, str]] = {}
        self._by_nic: dict[str, dict[str, str]] = {}
        self._by_vm: dict[str, dict[str, str]] = {}

    def load(self, regions: list[str], sub_regions: list[tuple[str, str]]) -> None:
        """Fetch every external source once, for the regions actually in use."""
        self._retirements = fetch_retirements(self._credential, self._subscription_ids)
        self._by_nic, self._by_vm = fetch_network_map(self._credential, self._subscription_ids)
        if regions and self._subscription_ids:
            self._skus = fetch_sku_catalog(self._credential, self._subscription_ids[0], regions)
        if sub_regions:
            self._quota = fetch_quota(self._credential, sub_regions)

    def apply(self, df: pd.DataFrame, resource_type: str) -> pd.DataFrame:
        if df.empty:
            return df
        df = self._add_sku(df, resource_type)
        df = self._add_network(df, resource_type)
        df = self._add_retirements(df)
        return df.drop(columns=[c for c in INTERNAL_COLUMNS if c in df.columns])

    # -- individual sources -------------------------------------------------
    def _add_sku(self, df: pd.DataFrame, resource_type: str) -> pd.DataFrame:
        column = _SIZE_COLUMN.get(resource_type)
        if not column or column not in df.columns or not self._skus:
            return df

        def one(row: pd.Series) -> pd.Series:
            key = (str(row.get("Região", "")).lower(), str(row.get(column, "")).lower())
            found = self._skus.get(key, {})
            values = {name: found.get(name, "") for name in ALL_SKU_COLUMNS}
            values[QUOTA_COLUMN] = self._quota.get(
                (
                    str(row.get(_SUB_ID, "")),
                    str(row.get("Região", "")).lower(),
                    str(found.get("VM Family", "")).lower(),
                ),
                "",
            )
            return pd.Series(values)

        return df.join(df.apply(one, axis=1))

    def _add_network(self, df: pd.DataFrame, resource_type: str) -> pd.DataFrame:
        # Only the VM sheet needs the join: the NIC sheet already reports these
        # fields from its own properties, one row per IP configuration.
        if resource_type != "microsoft.compute/virtualmachines":
            return df
        if not self._by_vm or _ID not in df.columns:
            return df
        found = df[_ID].map(lambda rid: self._by_vm.get(str(rid), {}))
        for column in NIC_COLUMNS:
            resolved = found.map(lambda values, c=column: values.get(c, ""))
            if column in df.columns:
                # The resolved value is the friendly one (a name or an address),
                # where the raw property only holds a resource id.
                df[column] = resolved.where(resolved.astype(str) != "", df[column])
            else:
                df[column] = resolved
        return df

    def _add_retirements(self, df: pd.DataFrame) -> pd.DataFrame:
        if _ID not in df.columns:
            return df
        found = df[_ID].map(lambda rid: self._retirements.get(str(rid), {}))
        for column in RETIREMENT_COLUMNS:
            df[column] = found.map(lambda values, c=column: values.get(c, ""))
        return df
