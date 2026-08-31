"""Azure Estate — Azure Resource Inventory

Usage examples
--------------
# List all available reports
python main.py --list

# Run a specific report (output goes to ./output/ by default, as .xlsx + .csv)
python main.py --report subscriptions

# Run every report at once
python main.py --report all

# Pick the output format: xlsx, csv or both (default)
python main.py --report all --format csv

# Specify a custom output directory
python main.py --report subscriptions --output /tmp/azure-estate
"""

from __future__ import annotations

import argparse
import sys

from azure_estate.reports import REPORT_REGISTRY
from azure_estate.reports.base import FORMATS


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    from azure_estate.config import CSV_DELIMITER, OUTPUT_FORMAT

    parser = argparse.ArgumentParser(
        prog="azure-estate",
        description="Azure Resource Inventory — generate Excel/CSV reports from Azure.",
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
        help="Directory where the report files will be saved (default: ./output/).",
    )
    parser.add_argument(
        "--format",
        dest="format",
        choices=list(FORMATS),
        default=(OUTPUT_FORMAT if OUTPUT_FORMAT in FORMATS else "both"),
        help=(
            "Output format: 'xlsx' (Excel only), 'csv' (CSV only) or 'both' "
            "(default: AZE_OUTPUT_FORMAT or both). Multi-sheet reports produce "
            "one CSV per sheet."
        ),
    )
    parser.add_argument(
        "--csv-delimiter",
        metavar="CHAR",
        default=CSV_DELIMITER,
        help=(
            "Field separator for CSV output (default: AZE_CSV_DELIMITER or ','). "
            "Use ';' for Excel in pt-BR locales."
        ),
    )
    parser.add_argument(
        "--upload",
        action="store_true",
        help=(
            "Upload the generated reports (.xlsx and .csv) from the output "
            "directory to Azure Storage (File Share or Blob container) using a "
            "Microsoft Entra identity."
        ),
    )
    parser.add_argument(
        "--upload-target",
        choices=["share", "blob"],
        help=(
            "Destination for --upload: 'share' (Azure File Share) or 'blob' "
            "(Blob container). Default: AZE_UPLOAD_TARGET or share."
        ),
    )
    parser.add_argument(
        "--storage-account",
        metavar="NAME",
        help="Storage account for --upload (default: AZE_STORAGE_ACCOUNT env).",
    )
    parser.add_argument(
        "--container",
        metavar="NAME",
        help=(
            "Blob container for --upload-target blob "
            "(default: AZE_BLOB_CONTAINER env)."
        ),
    )
    parser.add_argument(
        "--blob-prefix",
        metavar="PATH",
        help=(
            "Prefix (virtual folder) inside the container for --upload-target "
            "blob (default: AZE_BLOB_PREFIX env)."
        ),
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


def _upload_to_blob(args: argparse.Namespace, account: str) -> int:
    from azure_estate.config import BLOB_CONTAINER, BLOB_PREFIX

    try:
        from azure.core.exceptions import ClientAuthenticationError
        from azure_estate.exporters.blob import BlobUploader
    except ModuleNotFoundError as exc:
        print(
            f"[ERROR] Missing dependency for --upload-target blob: {exc.name}.\n"
            "       Install requirements first:  pip install -r requirements.txt\n"
            '       (or: pip install "azure-storage-blob>=12.19.0")'
        )
        return 1

    container = args.container or BLOB_CONTAINER
    prefix = args.blob_prefix if args.blob_prefix is not None else BLOB_PREFIX

    if not container:
        print(
            "[ERROR] Blob upload requires a container. Set AZE_BLOB_CONTAINER "
            "or use --container."
        )
        return 1

    # Account keys are never used for blob: managed identity is the point.
    if args.auth_mode == "key":
        print(
            "[ERROR] --auth-mode key is not supported for --upload-target blob. "
            "Blob upload always uses a Microsoft Entra identity; grant it the "
            "'Storage Blob Data Contributor' role on the container."
        )
        return 1

    uploader = BlobUploader(account, container, prefix)
    print(
        f"[AzEstate] Uploading reports from '{args.output}' to "
        f"{uploader.target_uri} …"
    )
    try:
        uploaded = uploader.upload_directory(args.output)
    except ClientAuthenticationError as exc:
        print(f"[ERROR] Authentication failed: {exc}")
        print(
            "       - Local dev: run 'az login' (or Connect-AzAccount).\n"
            "       - Azure VM (unattended): set AZE_AUTH_MODE=managed-identity "
            "(leave AZE_CLIENT_ID empty for the system-assigned identity)."
        )
        return 1
    except Exception as exc:  # noqa: BLE001 — surface a clear, actionable message
        print(f"[ERROR] Upload failed: {exc}")
        print(
            "       Ensure the identity has the 'Storage Blob Data Contributor' "
            f"role on container '{container}' (this is a different role from "
            "the one used for file shares) and that the container exists."
        )
        return 1

    if not uploaded:
        print(
            f"[AzEstate] No .xlsx/.csv files found in '{args.output}'. "
            "Nothing uploaded."
        )
        return 0

    print(f"[AzEstate] Uploaded {len(uploaded)} blob(s):")
    for name in uploaded:
        print(f"      - {name}")
    return 0


def _upload_reports(args: argparse.Namespace) -> int:
    from azure_estate.config import (
        FILE_SHARE,
        RESOURCE_GROUP,
        SHARE_PATH,
        STORAGE_ACCOUNT,
        SUBSCRIPTION,
        UPLOAD_AUTH_MODE,
        UPLOAD_TARGET,
    )

    account = args.storage_account or STORAGE_ACCOUNT
    target = (args.upload_target or UPLOAD_TARGET or "share").strip().lower()

    if not account:
        print(
            "[ERROR] Upload requires a storage account. Set AZE_STORAGE_ACCOUNT "
            "or use --storage-account."
        )
        return 1

    if target == "blob":
        return _upload_to_blob(args, account)

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

    share = args.share or FILE_SHARE
    share_path = args.share_path if args.share_path is not None else SHARE_PATH
    auth_mode = args.auth_mode or UPLOAD_AUTH_MODE or "login"
    resource_group = args.resource_group or RESOURCE_GROUP or None
    subscription = args.subscription or SUBSCRIPTION or None

    if not share:
        print(
            "[ERROR] File share upload requires a share. Set AZE_FILE_SHARE "
            "or use --share (or choose --upload-target blob)."
        )
        return 1

    from azure_estate.auth import is_managed_identity

    if auth_mode == "key" and is_managed_identity():
        # 'key' lists the account key through the Azure CLI, which needs a
        # signed-in user; on an unattended VM there is none.
        print(
            "[ERROR] --auth-mode key is incompatible with AZE_AUTH_MODE="
            "managed-identity: listing the account key requires a signed-in "
            "Azure CLI user.\n"
            "       Use --auth-mode login and grant the managed identity the "
            "'Storage File Data Privileged Contributor' role on the account."
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
                "       - Azure VM (unattended): set AZE_AUTH_MODE="
                "managed-identity (and AZE_CLIENT_ID for a user-assigned "
                "identity) and grant it 'Storage File Data Privileged "
                "Contributor' on the account.\n"
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
        print(
            f"[AzEstate] No .xlsx/.csv files found in '{args.output}'. "
            "Nothing uploaded."
        )
        return 0

    print(f"[AzEstate] Uploaded {len(uploaded)} file(s):")
    for name in uploaded:
        print(f"      - {name}")
    return 0


def _run_report(
    report_name: str,
    output_dir: str,
    fmt: str = "both",
    csv_delimiter: str = ",",
) -> None:
    """Run a single report by name and write its output file(s)."""
    report_cls = REPORT_REGISTRY[report_name]
    report = report_cls()

    print(f"[AzEstate] Running report: {report_name}")
    df = report.run()

    # Reports may override export() to produce richer output (charts, sheets)
    report.export(
        df, output_dir=output_dir, fmt=fmt, csv_delimiter=csv_delimiter
    )


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
                _run_report(name, args.output, args.format, args.csv_delimiter)
        elif report_name not in REPORT_REGISTRY:
            print(
                f"[ERROR] Unknown report '{report_name}'. "
                f"Use --list to see available reports."
            )
            return 1
        else:
            _run_report(report_name, args.output, args.format, args.csv_delimiter)

    if args.upload:
        return _upload_reports(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
