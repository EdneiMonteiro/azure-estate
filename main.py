"""Azure Estate — Azure Resource Inventory

Usage examples
--------------
# List all available reports
python main.py --list

# Run a specific report (output goes to ./output/ by default)
python main.py --report subscriptions

# Run every report at once
python main.py --report all

# Specify a custom output directory
python main.py --report subscriptions --output /tmp/azure-estate
"""

from __future__ import annotations

import argparse
import sys

from azure_estate.exporters.excel import ExcelExporter
from azure_estate.reports import REPORT_REGISTRY


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="azure-estate",
        description="Azure Resource Inventory — generate Excel reports from Azure.",
    )
    parser.add_argument(
        "--report",
        metavar="NAME",
        help="Name of the report to run, or 'all' to run every report (see --list).",
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
        help="Storage account for --upload (default: AZE_STORAGE_ACCOUNT env).",
    )
    parser.add_argument(
        "--share",
        metavar="NAME",
        help="File share name for --upload (default: AZE_FILE_SHARE env).",
    )
    parser.add_argument(
        "--share-path",
        metavar="PATH",
        help="Directory inside the share for --upload (default: AZE_SHARE_PATH env).",
    )
    parser.add_argument(
        "--auth-mode",
        choices=["login", "key"],
        help=(
            "Authentication for --upload: 'login' uses the signed-in Entra "
            "identity (OAuth); 'key' uses an account key obtained via ARM "
            "(works in Azure Cloud Shell). Default: AZE_UPLOAD_AUTH_MODE or login."
        ),
    )
    parser.add_argument(
        "--resource-group",
        metavar="NAME",
        help=(
            "Resource group of the storage account, used by --auth-mode key "
            "(default: AZE_RESOURCE_GROUP env; the CLI can auto-resolve it)."
        ),
    )
    parser.add_argument(
        "--subscription",
        metavar="ID",
        help=(
            "Subscription of the storage account, used by --auth-mode key "
            "(default: AZE_SUBSCRIPTION env or the CLI's active subscription)."
        ),
    )
    return parser, parser.parse_args(argv)


def _upload_reports(args: argparse.Namespace) -> int:
    from azure_estate.config import (
        FILE_SHARE,
        RESOURCE_GROUP,
        SHARE_PATH,
        STORAGE_ACCOUNT,
        SUBSCRIPTION,
        UPLOAD_AUTH_MODE,
    )

    try:
        from azure.core.exceptions import ClientAuthenticationError
        from azure_estate.exporters.file_share import FileShareUploader
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
    auth_mode = args.auth_mode or UPLOAD_AUTH_MODE or "login"
    resource_group = args.resource_group or RESOURCE_GROUP or None
    subscription = args.subscription or SUBSCRIPTION or None

    if not account or not share:
        print(
            "[ERROR] Upload requires a storage account and share. Set "
            "AZE_STORAGE_ACCOUNT / AZE_FILE_SHARE or use --storage-account / --share."
        )
        return 1

    uploader = FileShareUploader(
        account,
        share,
        share_path,
        auth_mode=auth_mode,
        resource_group=resource_group,
        subscription=subscription,
    )
    print(
        f"[AzEstate] Uploading reports from '{args.output}' to {uploader.target_uri} "
        f"(auth-mode: {auth_mode}) …"
    )
    try:
        uploaded = uploader.upload_directory(args.output)
    except ClientAuthenticationError as exc:
        print(f"[ERROR] Authentication failed: {exc}")
        if auth_mode == "login":
            print(
                "       Could not acquire a data-plane token for the signed-in "
                "identity.\n"
                "       - Local dev: run 'az login' (or Connect-AzAccount).\n"
                "       - Azure Cloud Shell: the token broker cannot mint "
                "storage.azure.com tokens; retry with '--auth-mode key'."
            )
        else:
            print(
                "       Could not list the account key via ARM. Ensure the "
                "signed-in user can list keys (Contributor or Storage Account "
                "Contributor) and pass --resource-group if auto-resolution fails."
            )
        return 1
    except Exception as exc:  # noqa: BLE001 — surface a clear, actionable message
        print(f"[ERROR] Upload failed: {exc}")
        print(
            "       Ensure the signed-in user has the 'Storage File Data Privileged "
            "Contributor' role on the storage account (for --auth-mode login) and "
            "that the account allows Microsoft Entra (OAuth) authentication for "
            "file shares."
        )
        return 1

    if not uploaded:
        print(f"[AzEstate] No .xlsx files found in '{args.output}'. Nothing uploaded.")
        return 0

    print(f"[AzEstate] Uploaded {len(uploaded)} file(s):")
    for name in uploaded:
        print(f"      - {name}")
    return 0


def _run_report(report_name: str, output_dir: str) -> None:
    """Run a single report by name and write its Excel output."""
    report_cls = REPORT_REGISTRY[report_name]
    report = report_cls()

    print(f"[AzEstate] Running report: {report_name}")
    df = report.run()

    # Reports may override export() to produce richer workbooks (e.g. with charts)
    if hasattr(report, "export"):
        report.export(df, output_dir=output_dir)
    else:
        exporter = ExcelExporter(output_dir=output_dir)
        path = exporter.save(df, sheet_name=report.name)
        print(f"[AzEstate] Done. File saved to: {path.resolve()}")
        print(f"      Rows exported: {len(df)}")


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

        if report_name == "all":
            for name in REPORT_REGISTRY:
                _run_report(name, args.output)
        elif report_name not in REPORT_REGISTRY:
            print(
                f"[ERROR] Unknown report '{report_name}'. "
                f"Use --list to see available reports."
            )
            return 1
        else:
            _run_report(report_name, args.output)

    if args.upload:
        return _upload_reports(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
