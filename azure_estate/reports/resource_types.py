from __future__ import annotations

import pathlib

import pandas as pd

from azure_estate.auth import get_credential
from azure_estate.collectors.resource_types import list_resource_types
from azure_estate.config import TENANT_ID
from azure_estate.exporters.csv_exporter import CsvExporter
from azure_estate.exporters.excel import ExcelExporter
from azure_estate.reports.base import BaseReport, print_saved, wants_csv, wants_excel
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

    def export(
        self,
        df: pd.DataFrame,
        output_dir: str = "output",
        fmt: str = "both",
        csv_delimiter: str = ",",
    ) -> None:
        """Override export so the workbook also carries a pie chart sheet."""
        paths: list[pathlib.Path] = []

        if wants_excel(fmt):
            exporter = ExcelExporter(output_dir=output_dir)
            paths.append(
                exporter.save_with_pie_chart(
                    df=df,
                    label_col="Recurso",
                    value_col="Qtd. Recursos",
                    sheet_name=self.name,
                    chart_sheet_name="Gráfico",
                    chart_title="Distribuição por Tipo de Recurso",
                    top_n=15,
                )
            )

        if wants_csv(fmt):
            # A CSV holds no chart — the tabular data is exported as-is.
            csv_exporter = CsvExporter(output_dir=output_dir, delimiter=csv_delimiter)
            paths.append(csv_exporter.save(df, name=self.name))

        print_saved(paths, f"Rows exported: {len(df)}")
