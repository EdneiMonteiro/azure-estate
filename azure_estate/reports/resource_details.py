from __future__ import annotations

import pathlib

import pandas as pd

from azure_estate.auth import get_credential
from azure_estate.collectors._graph import run_graph_query
from azure_estate.collectors.resource_details import query_resource_type
from azure_estate.collectors.subscriptions import list_active_subscriptions
from azure_estate.config import TENANT_ID
from azure_estate.enrich import Enricher
from azure_estate.exporters.csv_exporter import CsvExporter
from azure_estate.exporters.excel import ExcelExporter
from azure_estate.naming import run_stamp
from azure_estate.reports.base import BaseReport, wants_csv, wants_excel
from azure_estate.resource_type_configs import RESOURCE_CONFIGS

# Only regions where compute actually exists are worth a SKU/quota round-trip.
_FOOTPRINT_KQL = (
    "Resources"
    " | where type in ('microsoft.compute/virtualmachines',"
    " 'microsoft.compute/virtualmachinescalesets',"
    " 'microsoft.containerservice/managedclusters')"
    " | summarize by subscriptionId, location"
)


def _compute_footprint(credential, sub_ids: list[str]) -> tuple[list[str], list[tuple[str, str]]]:
    """Return the regions with compute, and the (subscription, region) pairs."""
    from azure.mgmt.resourcegraph import ResourceGraphClient

    try:
        rows = run_graph_query(ResourceGraphClient(credential), sub_ids, _FOOTPRINT_KQL)
    except Exception:  # noqa: BLE001 — enrichment is best effort
        return [], []
    pairs = [
        (r["subscriptionId"], str(r["location"]).lower())
        for r in rows
        if r.get("subscriptionId") and r.get("location")
    ]
    return sorted({region for _sub, region in pairs}), pairs


class ResourceDetailReport(BaseReport):
    """One Excel sheet per curated resource type with type-specific properties."""

    name = "resource_details"

    def run(self) -> pd.DataFrame:
        # run() is not used for this report — export() drives everything
        return pd.DataFrame()

    def export(
        self,
        df: pd.DataFrame,
        output_dir: str = "output",
        fmt: str = "both",
        csv_delimiter: str = ",",
    ) -> None:
        credential = get_credential()

        print("  Fetching active subscriptions…")
        subs = list_active_subscriptions(credential, TENANT_ID)
        if not subs:
            print("  No active subscriptions found.")
            return

        sub_ids = [s["subscription_id"] for s in subs]
        print(f"  {len(sub_ids)} subscription(s) found. Querying {len(RESOURCE_CONFIGS)} resource types…\n")

        print("  Loading SKU catalogue, quotas, retirements and network map…", end=" ", flush=True)
        enricher = Enricher(credential, sub_ids)
        regions, sub_regions = _compute_footprint(credential, sub_ids)
        enricher.load(regions, sub_regions)
        print(f"{len(regions)} region(s)\n")

        sheets: list[tuple[str, pd.DataFrame]] = []

        for config in RESOURCE_CONFIGS:
            print(f"  [{config.sheet_name}] querying…", end=" ", flush=True)
            try:
                result_df = query_resource_type(credential, sub_ids, config)
                if result_df.empty:
                    print("0 resources — skipped")
                else:
                    result_df = enricher.apply(result_df, config.resource_type)
                    print(f"{len(result_df)} resource(s)")
                    sheets.append((config.sheet_name, result_df))
            except Exception as exc:
                print(f"ERROR — {exc}")

        if not sheets:
            print("\n  No resources found across all configured types.")
            return

        paths: list[pathlib.Path] = []

        if wants_excel(fmt):
            exporter = ExcelExporter(output_dir=output_dir)
            paths.append(
                exporter.save_multi_sheet(
                    sheets, f"resource_details_{run_stamp()}.xlsx"
                )
            )

        if wants_csv(fmt):
            # A CSV holds a single table: one file per sheet.
            csv_exporter = CsvExporter(output_dir=output_dir, delimiter=csv_delimiter)
            paths.extend(csv_exporter.save_tables(sheets, prefix=self.name))

        total_rows = sum(len(sheet_df) for _, sheet_df in sheets)
        print("\n[AzEstate] Done. File(s) saved:")
        for path in paths:
            print(f"      - {path.resolve()}")
        print(f"      Sheets: {len(sheets)}  |  Total rows: {total_rows}")
