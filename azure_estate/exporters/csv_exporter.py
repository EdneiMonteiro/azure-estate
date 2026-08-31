"""Save reports as CSV files.

One CSV per table: unlike a workbook, a CSV holds a single sheet, so a
multi-sheet report becomes ``<prefix>_<table>_<YYYYMMDD>.csv``.

The default encoding is ``utf-8-sig`` because Excel on Windows reads plain
UTF-8 CSV as Latin-1 and mangles every accent.
"""
from __future__ import annotations

import pathlib
import re
from datetime import date

import pandas as pd

_UNSAFE = re.compile(r"[^A-Za-z0-9._-]+")


def _slug(name: str) -> str:
    """Turn a sheet/report name into a filesystem-safe fragment."""
    return _UNSAFE.sub("_", str(name).strip()).strip("._-") or "report"


class CsvExporter:
    """Writes DataFrames as CSV files inside *output_dir*."""

    def __init__(
        self,
        output_dir: str = "output",
        delimiter: str = ",",
        encoding: str = "utf-8-sig",
    ) -> None:
        self._output_dir = pathlib.Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._delimiter = delimiter or ","
        self._encoding = encoding

    def save(
        self,
        df: pd.DataFrame,
        name: str = "report",
        filename: str | None = None,
    ) -> pathlib.Path:
        """Write *df* to a CSV file and return its path.

        Parameters
        ----------
        df:
            DataFrame to export.
        name:
            Base name used when *filename* is omitted.
        filename:
            Explicit file name (without directory).  Defaults to
            ``<name>_YYYYMMDD.csv``.
        """
        if filename is None:
            today = date.today().strftime("%Y%m%d")
            filename = f"{_slug(name)}_{today}.csv"

        path = self._output_dir / filename
        df.to_csv(
            path,
            index=False,
            sep=self._delimiter,
            encoding=self._encoding,
            lineterminator="\r\n",
        )
        return path

    def save_tables(
        self,
        tables: list[tuple[str, pd.DataFrame]],
        prefix: str,
    ) -> list[pathlib.Path]:
        """Write one CSV per table. Empty DataFrames are skipped."""
        today = date.today().strftime("%Y%m%d")
        paths: list[pathlib.Path] = []
        for table_name, df in tables:
            if df is None or df.empty:
                continue
            filename = f"{_slug(prefix)}_{_slug(table_name)}_{today}.csv"
            paths.append(self.save(df, filename=filename))
        return paths
