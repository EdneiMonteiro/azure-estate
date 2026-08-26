from __future__ import annotations

import pathlib
from datetime import date

import pandas as pd
from openpyxl.chart import PieChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.chart.series import DataPoint

# Excel refuses any cell longer than this; openpyxl would silently truncate it.
_MAX_CELL = 32767
_ELLIPSIS = "… (truncado)"


def _clip_cells(df: pd.DataFrame) -> pd.DataFrame:
    """Shorten oversized text cells, flagging that content was cut.

    Flattened arrays (a firewall's address list, a cluster's labels) can run to
    hundreds of thousands of characters.
    """
    out = df.copy()
    for column in out.columns:
        values = out[column]
        if pd.api.types.is_numeric_dtype(values) or pd.api.types.is_bool_dtype(values):
            continue
        text = values.astype(str)
        if not (text.str.len() > _MAX_CELL).any():
            continue
        out[column] = text.mask(
            text.str.len() > _MAX_CELL,
            text.str.slice(0, _MAX_CELL - len(_ELLIPSIS)) + _ELLIPSIS,
        )
    return out


class ExcelExporter:
    """Saves one or more DataFrames as sheets in an Excel workbook."""

    def __init__(self, output_dir: str = "output") -> None:
        self._output_dir = pathlib.Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        df: pd.DataFrame,
        sheet_name: str = "Sheet1",
        filename: str | None = None,
    ) -> pathlib.Path:
        """Write *df* to an Excel file and return the resolved path.

        Parameters
        ----------
        df:
            DataFrame to export.
        sheet_name:
            Name of the Excel worksheet.
        filename:
            Base filename (without directory).  Defaults to
            ``<sheet_name>_YYYYMMDD.xlsx``.
        """
        if filename is None:
            today = date.today().strftime("%Y%m%d")
            filename = f"{sheet_name}_{today}.xlsx"

        path = self._output_dir / filename

        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name=sheet_name[:31])
            self._auto_fit(writer.sheets[sheet_name[:31]])

        return path

    @staticmethod
    def _auto_fit(worksheet) -> None:
        """Auto-fit column widths for a worksheet (max 80 chars)."""
        for col_cells in worksheet.columns:
            max_len = max(
                len(str(cell.value)) if cell.value is not None else 0
                for cell in col_cells
            )
            worksheet.column_dimensions[col_cells[0].column_letter].width = (
                min(max_len + 4, 80)
            )

    def save_multi_sheet(
        self,
        sheets: list[tuple[str, "pd.DataFrame"]],
        filename: str,
    ) -> pathlib.Path:
        """Write multiple DataFrames as separate sheets in one Excel workbook.

        Parameters
        ----------
        sheets:
            Ordered list of (sheet_name, DataFrame). Empty DataFrames are skipped.
        filename:
            Base filename (without directory).
        """
        path = self._output_dir / filename

        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            for sheet_name, df in sheets:
                if df is None or df.empty:
                    continue
                safe_name = sheet_name[:31]
                _clip_cells(df).to_excel(writer, index=False, sheet_name=safe_name)
                self._auto_fit(writer.sheets[safe_name])

        return path

    def save_with_pie_chart(
        self,
        df: "pd.DataFrame",
        label_col: str,
        value_col: str,
        sheet_name: str = "Sheet1",
        chart_sheet_name: str = "Gráfico",
        chart_title: str = "Distribuição",
        top_n: int = 15,
        filename: str | None = None,
    ) -> pathlib.Path:
        """Write *df* to Excel with a pie chart on a second sheet.

        Parameters
        ----------
        df:
            Full DataFrame (already sorted as desired).
        label_col:
            Column to use as pie slice labels.
        value_col:
            Column to use as pie slice values.
        top_n:
            Keep the top N rows in the chart; remaining rows are grouped as
            'Outros' to keep the chart readable.
        """
        if filename is None:
            today = date.today().strftime("%Y%m%d")
            filename = f"{sheet_name}_{today}.xlsx"

        path = self._output_dir / filename

        # --- Build chart DataFrame (top N + Outros) ---
        chart_df = df[[label_col, value_col]].copy()
        if len(chart_df) > top_n:
            top = chart_df.head(top_n).copy()
            outros_total = chart_df.iloc[top_n:][value_col].sum()
            outros_row = pd.DataFrame([{label_col: "Outros", value_col: outros_total}])
            chart_df = pd.concat([top, outros_row], ignore_index=True)

        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            # Sheet 1: full data
            df.to_excel(writer, index=False, sheet_name=sheet_name[:31])
            self._auto_fit(writer.sheets[sheet_name[:31]])

            # Sheet 2: chart source data (hidden helper sheet) + chart
            chart_df.to_excel(writer, index=False, sheet_name="_chart_data")
            ws_chart_data = writer.sheets["_chart_data"]
            ws_chart_data.sheet_state = "hidden"

            # Build the pie chart referencing the hidden sheet
            n_rows = len(chart_df) + 1  # +1 for header
            labels = Reference(ws_chart_data, min_col=1, min_row=2, max_row=n_rows)
            data = Reference(ws_chart_data, min_col=2, min_row=1, max_row=n_rows)

            pie = PieChart()
            pie.add_data(data, titles_from_data=True)
            pie.set_categories(labels)
            pie.title = chart_title
            pie.style = 10
            pie.dataLabels = DataLabelList()
            pie.dataLabels.showPercent = True
            pie.dataLabels.showCatName = False
            pie.dataLabels.showVal = False
            pie.dataLabels.showSerName = False
            pie.width = 22
            pie.height = 16

            # Create chart sheet
            wb = writer.book
            ws_chart = wb.create_sheet(title=chart_sheet_name[:31])
            ws_chart.add_chart(pie, "B2")

        return path
