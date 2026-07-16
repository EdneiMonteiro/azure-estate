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
    parser.add_argument(
        "--upload",
        action="store_true",
        help=(
            "Upload the generated .xlsx reports from the output directory to an "
            "Azure File Share using the signed-in user's Microsoft Entra identity."
        ),
    )
    parser.add_argument(
        "--storage-account",
        metavar="NAME",
        help="Storage account for --upload (default: ARI_STORAGE_ACCOUNT env).",
    )
    parser.add_argument(
        "--share",
        metavar="NAME",
        help="File share name for --upload (default: ARI_FILE_SHARE env).",
    )
    parser.add_argument(
        "--share-path",
        metavar="PATH",
        help="Directory inside the share for --upload (default: ARI_SHARE_PATH env).",
    )
    return parser, parser.parse_args(argv)


def _upload_reports(args: argparse.Namespace) -> int:
    from ari.config import FILE_SHARE, SHARE_PATH, STORAGE_ACCOUNT

    try:
        from azure.core.exceptions import ClientAuthenticationError
        from ari.exporters.file_share import FileShareUploader
    except ModuleNotFoundError as exc:
        print(
            f"[ERROR] Missing dependency for --upload: {exc.name}.\n"
            "       Install requirements first:  pip install -r requirements.txt\n"
            '       (or: pip install "azure-storage-file-share>=12.16.0")'
        )
        return 1

    account = args.storage_account or STORAGE_ACCOUNT
    share = args.share or FILE_SHARE
    share_path = args.share_path if args.share_path is not None else SHARE_PATH

    if not account or not share:
        print(
            "[ERROR] Upload requires a storage account and share. Set "
            "ARI_STORAGE_ACCOUNT / ARI_FILE_SHARE or use --storage-account / --share."
        )
        return 1

    uploader = FileShareUploader(account, share, share_path)
    print(f"[ARI] Uploading reports from '{args.output}' to {uploader.target_uri} …")
    try:
        uploaded = uploader.upload_directory(args.output)
    except ClientAuthenticationError as exc:
        print(f"[ERROR] Authentication failed: {exc}")
        print(
            "       Sign in with the Azure CLI first:  az login\n"
            "       (or Connect-AzAccount for Azure PowerShell)."
        )
        return 1
    except Exception as exc:  # noqa: BLE001 — surface a clear, actionable message
        print(f"[ERROR] Upload failed: {exc}")
        print(
            "       Ensure the signed-in user has the 'Storage File Data Privileged "
            "Contributor' role on the storage account and that the account allows "
            "Microsoft Entra (OAuth) authentication for file shares."
        )
        return 1

    if not uploaded:
        print(f"[ARI] No .xlsx files found in '{args.output}'. Nothing uploaded.")
        return 0

    print(f"[ARI] Uploaded {len(uploaded)} file(s):")
    for name in uploaded:
        print(f"      - {name}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser, args = parse_args(argv)

    if args.list:
        print("Available reports:")
        for name in sorted(REPORT_REGISTRY):
            print(f"  {name}")
        return 0

    if not args.report and not args.upload:
        parser.print_help()
        return 0

    if args.report:
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

    if args.upload:
        return _upload_reports(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
