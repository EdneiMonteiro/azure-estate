"""Compute SKU catalogue and quota usage.

Resource Graph reports the *name* of a VM size but nothing about the hardware
behind it.  ARI resolves vCPUs, memory, disk and network limits from the
`Microsoft.Compute/skus` provider endpoint, and remaining quota from
`Microsoft.Compute/usages`; both are reproduced here.
"""
from __future__ import annotations

from typing import Any

from azure.identity import AzureCliCredential

from azure_estate.collectors._arm import arm_get
from azure_estate.parallel import map_resiliente

# ARI's per-size columns, mapped to the capability names the provider returns.
SKU_COLUMNS: list[tuple[str, str]] = [
    ("vCPUs",                            "vCPUs"),
    ("vCPUs Available",                  "vCPUsAvailable"),
    ("vCPUs Per Core",                   "vCPUsPerCore"),
    ("RAM (GiB)",                        "MemoryGB"),
    ("Max Data Disks",                   "MaxDataDiskCount"),
    ("Max Network Interfaces",           "MaxNetworkInterfaces"),
    ("Uncached Disk IOPS Limit",         "UncachedDiskIOPS"),
    ("Uncached Disk Throughput (MBps)",  "UncachedDiskBytesPerSecond"),
    ("Premium IO",                       "PremiumIO"),
    ("Accelerated Networking",           "AcceleratedNetworkingEnabled"),
    ("CPU Architecture",                 "CpuArchitectureType"),
    ("Ephemeral OS Disk Supported",      "EphemeralOSDiskSupported"),
]
# Columns that come from the SKU record itself rather than its capabilities.
SKU_META_COLUMNS: list[str] = ["VM Family", "Zones Available in the Region"]

ALL_SKU_COLUMNS: list[str] = [name for name, _ in SKU_COLUMNS] + SKU_META_COLUMNS

_MB = 1024 * 1024


def _capabilities(sku: dict[str, Any]) -> dict[str, str]:
    return {c["name"]: c["value"] for c in sku.get("capabilities", []) if "name" in c}


def _zones(sku: dict[str, Any], region: str) -> str:
    for info in sku.get("locationInfo", []):
        if str(info.get("location", "")).lower() == region:
            return ", ".join(sorted(info.get("zones", []) or []))
    return ""


def fetch_sku_catalog(
    credential: AzureCliCredential,
    subscription_id: str,
    regions: list[str],
    workers: int = 8,
) -> dict[tuple[str, str], dict[str, str]]:
    """Return {(region, vm_size_lower): column_name -> value}.

    The catalogue is subscription-independent in practice, so a single
    subscription is queried per region.
    """

    def one(region: str) -> tuple[str, list[dict[str, Any]]]:
        try:
            return region, arm_get(
                credential,
                f"/subscriptions/{subscription_id}/providers/Microsoft.Compute/skus",
                "2021-07-01",
                {"$filter": f"location eq '{region}'"},
            )
        except Exception:  # noqa: BLE001 — a region may be unavailable to the tenant
            return region, []

    catalog: dict[tuple[str, str], dict[str, str]] = {}
    falhas: list[str] = []
    for region, skus in map_resiliente(one, regions, workers, "catálogo de SKUs"):
        if not skus:
            falhas.append(region)
        for sku in skus:
            if sku.get("resourceType") != "virtualMachines":
                continue
            caps = _capabilities(sku)
            row = {name: caps.get(key, "") for name, key in SKU_COLUMNS}
            # The provider reports throughput in bytes/s; ARI reports MBps.
            raw = row.get("Uncached Disk Throughput (MBps)")
            if raw:
                row["Uncached Disk Throughput (MBps)"] = str(round(float(raw) / _MB))
            row["VM Family"] = sku.get("family", "")
            row["Zones Available in the Region"] = _zones(sku, region)
            catalog[(region, str(sku.get("name", "")).lower())] = row
    if falhas:
        # Without this the SKU columns come back empty and look like a data gap
        # rather than a failed lookup.
        print(
            f"\n  [AVISO] catálogo de SKUs vazio em {len(falhas)} região(ões): "
            f"{', '.join(sorted(falhas)[:5])}"
            f"{' …' if len(falhas) > 5 else ''}",
            end="",
        )
    return catalog


def fetch_quota(
    credential: AzureCliCredential,
    pairs: list[tuple[str, str]],
    workers: int = 16,
) -> dict[tuple[str, str, str], str]:
    """Return {(subscription_id, region, family_lower): remaining} for *pairs*.

    *pairs* are the (subscription_id, region) combinations actually in use, so
    idle regions are never queried.
    """

    def one(pair: tuple[str, str]) -> tuple[tuple[str, str], list[dict[str, Any]]]:
        sub, region = pair
        try:
            return pair, arm_get(
                credential,
                f"/subscriptions/{sub}/providers/Microsoft.Compute/locations/{region}/usages",
                "2021-07-01",
            )
        except Exception:  # noqa: BLE001 — provider not registered in this subscription
            return pair, []

    quota: dict[tuple[str, str, str], str] = {}
    vazios = 0
    for (sub, region), usages in map_resiliente(one, pairs, workers, "cotas de vCPU"):
        if not usages:
            vazios += 1
        for usage in usages:
            family = str(usage.get("name", {}).get("value", "")).lower()
            limit, current = usage.get("limit"), usage.get("currentValue")
            if family and limit is not None and current is not None:
                quota[(sub, region, family)] = str(limit - current)
    if vazios:
        # Some subscriptions genuinely have no Compute provider registered, so
        # this is a warning, not an error — but a silent zero would hide a
        # throttled or failed run behind an empty column.
        print(
            f"\n  [AVISO] cota indisponível em {vazios} de {len(pairs)} par(es) "
            "assinatura/região (provider não registrado ou consulta falhou)",
            end="",
        )
    return quota
