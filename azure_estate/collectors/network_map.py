"""Cross-resource network relationships.

Several ARI columns are not properties of the resource at all: a VM's private
IP, subnet, VNet and NSG live on its network interfaces, and the public IP
address lives on yet another resource.  This module resolves those links once
and hands back lookup tables keyed by resource id.
"""
from __future__ import annotations

from typing import Any

from azure.identity import AzureCliCredential
from azure.mgmt.resourcegraph import ResourceGraphClient

from azure_estate.collectors._graph import run_graph_query

NIC_COLUMNS: list[str] = [
    "NIC Name",
    "NIC Type",
    "Private IP Address",
    "Private IP Allocation",
    "Public IP",
    "NSG",
    "Subnet",
    "Virtual Network",
    "Accelerated Networking",
]

_NIC_KQL = (
    "Resources | where type == 'microsoft.network/networkinterfaces'"
    " | project id, name,"
    " vm = tolower(tostring(properties['virtualMachine']['id'])),"
    " nsg = tostring(properties['networkSecurityGroup']['id']),"
    " accel = tostring(properties['enableAcceleratedNetworking']),"
    " ipconfigs = properties['ipConfigurations']"
)

_PIP_KQL = (
    "Resources | where type == 'microsoft.network/publicipaddresses'"
    " | project id = tolower(id), addr = tostring(properties['ipAddress'])"
)


def _name_of(resource_id: Any) -> str:
    text = str(resource_id or "")
    return text.rsplit("/", 1)[-1] if "/" in text else ""


def _vnet_of(subnet_id: Any) -> str:
    """A subnet id ends in .../virtualNetworks/<vnet>/subnets/<subnet>."""
    parts = str(subnet_id or "").split("/")
    return parts[-3] if len(parts) >= 3 else ""


def _join(values: list[str]) -> str:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            out.append(value)
    return ", ".join(out)


def fetch_network_map(
    credential: AzureCliCredential,
    subscription_ids: list[str],
) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    """Return (by_nic_id, by_vm_id) lookup tables of NIC-derived columns.

    A VM with several interfaces gets the values of all of them joined, rather
    than one row per NIC, so the sheet keeps one line per virtual machine.
    """
    client = ResourceGraphClient(credential)
    try:
        nics: list[dict[str, Any]] = run_graph_query(client, subscription_ids, _NIC_KQL)
        pips: list[dict[str, Any]] = run_graph_query(client, subscription_ids, _PIP_KQL)
    except Exception:  # noqa: BLE001 — the report still works without the joins
        return {}, {}

    pip_by_id = {row["id"]: row.get("addr", "") for row in pips if row.get("id")}

    by_nic: dict[str, dict[str, str]] = {}
    grouped: dict[str, list[dict[str, str]]] = {}
    for nic in nics:
        configs = nic.get("ipconfigs") or []
        if isinstance(configs, dict):
            configs = [configs]
        props = [c.get("properties", {}) for c in configs if isinstance(c, dict)]
        row = {
            "NIC Name": nic.get("name", ""),
            "NIC Type": _join([str(p.get("privateIPAddressVersion", "")) for p in props]),
            "Private IP Address": _join([str(p.get("privateIPAddress", "")) for p in props]),
            "Private IP Allocation": _join([str(p.get("privateIPAllocationMethod", "")) for p in props]),
            "Public IP": _join(
                [pip_by_id.get(str((p.get("publicIPAddress") or {}).get("id", "")).lower(), "") for p in props]
            ),
            "NSG": _name_of(nic.get("nsg")),
            "Subnet": _join([_name_of((p.get("subnet") or {}).get("id")) for p in props]),
            "Virtual Network": _join([_vnet_of((p.get("subnet") or {}).get("id")) for p in props]),
            "Accelerated Networking": nic.get("accel", ""),
        }
        by_nic[str(nic.get("id", "")).lower()] = row
        if nic.get("vm"):
            grouped.setdefault(nic["vm"], []).append(row)

    by_vm = {
        vm_id: {column: _join([r[column] for r in rows]) for column in NIC_COLUMNS}
        for vm_id, rows in grouped.items()
    }
    return by_nic, by_vm
