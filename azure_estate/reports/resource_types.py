from __future__ import annotations

import pandas as pd

from azure_estate.auth import get_credential
from azure_estate.collectors.resource_types import list_resource_types
from azure_estate.config import TENANT_ID
from azure_estate.exporters.excel import ExcelExporter
from azure_estate.reports.base import BaseReport
from azure_estate.resource_type_configs import friendly_resource_name


class ResourceTypeReport(BaseReport):
    """Lists all resource types across active subscriptions with their total count."""

    name = "resource_types"

    def run(self) -> pd.DataFrame:
        credential = get_credential()

        print("  Fetching resource types…")
        data = list_resource_types(credential, TENANT_ID)

        if not data:
            print("  No resources found.")
            return pd.DataFrame(columns=["Recurso", "Tipo de Recurso", "Qtd. Recursos"])

        print(f"  Found {len(data)} distinct resource type(s).")

        df = pd.DataFrame(
            [
                {
                    "Recurso": friendly_resource_name(d["type"]),
                    "Tipo de Recurso": d["type"],
                    "Qtd. Recursos": d["resource_count"],
                }
                for d in data
            ]
        )
        df.sort_values("Qtd. Recursos", ascending=False, inplace=True, ignore_index=True)
        return df

    def export(self, df: pd.DataFrame, output_dir: str = "output") -> None:
        """Override export to include a pie chart sheet."""
        exporter = ExcelExporter(output_dir=output_dir)
        path = exporter.save_with_pie_chart(
            df=df,
            label_col="Recurso",
            value_col="Qtd. Recursos",
            sheet_name=self.name,
            chart_sheet_name="Gráfico",
            chart_title="Distribuição por Tipo de Recurso",
            top_n=15,
        )
        print(f"[AzEstate] Done. File saved to: {path.resolve()}")
        print(f"      Rows exported: {len(df)}")
