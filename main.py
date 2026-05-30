"""ARI — Azure Resource Inventory

Usage examples
--------------
# List all available reports
python main.py --list

# Run a specific report (output goes to ./output/ by default)
python main.py --report subscriptions

# Specify a custom output directory
python main.py --report subscriptions --output /tmp/ari
"""

from __future__ import annotations

import argparse
import sys

from ari.exporters.excel import ExcelExporter
from ari.reports import REPORT_REGISTRY


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="ari",
        description="Azure Resource Inventory — generate Excel reports from Azure.",
    )
    parser.add_argument(
        "--report",
        metavar="NAME",
        help="Name of the report to run (see --list).",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available reports and exit.",
    )
    parser.add_argument(
        "--output",
        metavar="DIR",
        default="output",
        help="Directory where the Excel file will be saved (default: ./output/).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.list:
        print("Available reports:")
        for name in sorted(REPORT_REGISTRY):
            print(f"  {name}")
        return 0

    if not args.report:
        parser.print_help()
        return 0

    report_name = args.report.lower()
    if report_name not in REPORT_REGISTRY:
        print(
            f"[ERROR] Unknown report '{report_name}'. "
            f"Use --list to see available reports."
        )
        return 1

    report_cls = REPORT_REGISTRY[report_name]
    report = report_cls()

    print(f"[ARI] Running report: {report_name}")
    df = report.run()

    # Reports may override export() to produce richer workbooks (e.g. with charts)
    if hasattr(report, "export"):
        report.export(df, output_dir=args.output)
    else:
        exporter = ExcelExporter(output_dir=args.output)
        path = exporter.save(df, sheet_name=report.name)
        print(f"[ARI] Done. File saved to: {path.resolve()}")
        print(f"      Rows exported: {len(df)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
