from __future__ import annotations

import abc
import pathlib

import pandas as pd

#: Accepted values for the ``--format`` flag.
FORMATS = ("xlsx", "csv", "both")


def wants_excel(fmt: str) -> bool:
    return fmt in ("xlsx", "both")


def wants_csv(fmt: str) -> bool:
    return fmt in ("csv", "both")


def print_saved(paths: list[pathlib.Path], summary: str) -> None:
    """Print the files produced by a report, plus a one-line summary."""
    if not paths:
        print("[AzEstate] Nothing exported.")
        return
    print("[AzEstate] Done. File(s) saved:")
    for path in paths:
        print(f"      - {path.resolve()}")
    print(f"      {summary}")


class BaseReport(abc.ABC):
    """Contract that every Azure Estate report must satisfy.

    Subclasses implement `run()` and return a tidy DataFrame whose columns
    are ready to be exported directly to Excel or CSV.
    """

    #: Short, filesystem-safe name used as the default Excel sheet name.
    name: str = ""

    @abc.abstractmethod
    def run(self) -> pd.DataFrame:
        """Collect data and return it as a pandas DataFrame."""

    def export(
        self,
        df: pd.DataFrame,
        output_dir: str = "output",
        fmt: str = "both",
        csv_delimiter: str = ",",
    ) -> None:
        """Write the report in the requested format(s).

        Subclasses may override this to produce richer output (charts,
        multiple sheets), but must honour *fmt* and *csv_delimiter*.
        """
        from azure_estate.exporters.csv_exporter import CsvExporter
        from azure_estate.exporters.excel import ExcelExporter

        paths: list[pathlib.Path] = []
        if wants_excel(fmt):
            exporter = ExcelExporter(output_dir=output_dir)
            paths.append(exporter.save(df, sheet_name=self.name))
        if wants_csv(fmt):
            csv_exporter = CsvExporter(output_dir=output_dir, delimiter=csv_delimiter)
            paths.append(csv_exporter.save(df, name=self.name))

        print_saved(paths, f"Rows exported: {len(df)}")
