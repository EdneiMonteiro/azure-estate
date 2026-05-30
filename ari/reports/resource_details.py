from __future__ import annotations

from datetime import date

import pandas as pd

from ari.auth import get_credential
from ari.collectors.resource_details import query_resource_type
from ari.collectors.subscriptions import list_active_subscriptions
from ari.config import TENANT_ID
from ari.exporters.excel import ExcelExporter
from ari.reports.base import BaseReport
from ari.resource_type_configs import RESOURCE_CONFIGS


class ResourceDetailReport(BaseReport):
    """One Excel sheet per curated resource type with type-specific properties."""

    name = "resource_details"

    def run(self) -> pd.DataFrame:
        # run() is not used for this report — export() drives everything
        return pd.DataFrame()

    def export(self, df: pd.DataFrame, output_dir: str = "output") -> None:
        credential = get_credential()

        print("  Fetching active subscriptions…")
        subs = list_active_subscriptions(credential, TENANT_ID)
        if not subs:
            print("  No active subscriptions found.")
            return

        sub_ids = [s["subscription_id"] for s in subs]
        print(f"  {len(sub_ids)} subscription(s) found. Querying {len(RESOURCE_CONFIGS)} resource types…\n")

        sheets: list[tuple[str, pd.DataFrame]] = []

        for config in RESOURCE_CONFIGS:
            print(f"  [{config.sheet_name}] querying…", end=" ", flush=True)
            try:
                result_df = query_resource_type(credential, sub_ids, config)
                if result_df.empty:
                    print("0 resources — skipped")
                else:
                    print(f"{len(result_df)} resource(s)")
                    sheets.append((config.sheet_name, result_df))
            except Exception as exc:
                print(f"ERROR — {exc}")

        if not sheets:
            print("\n  No resources found across all configured types.")
            return

        today = date.today().strftime("%Y%m%d")
        filename = f"resource_details_{today}.xlsx"

        exporter = ExcelExporter(output_dir=output_dir)
        path = exporter.save_multi_sheet(sheets, filename)

        total_rows = sum(len(df) for _, df in sheets)
        print(f"\n[ARI] Done. File saved to: {path.resolve()}")
        print(f"      Sheets: {len(sheets)}  |  Total rows: {total_rows}")
