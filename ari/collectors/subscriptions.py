from __future__ import annotations

from typing import Any

from azure.identity import AzureCliCredential
from azure.mgmt.subscription import SubscriptionClient
from azure.mgmt.resourcegraph import ResourceGraphClient
from azure.mgmt.resourcegraph.models import QueryRequest

# ---------------------------------------------------------------------------
# Offer ID → human-readable Offer name mapping (most common Azure offer types)
# ---------------------------------------------------------------------------
OFFER_NAMES: dict[str, str] = {
    "MS-AZR-0003P": "Pay-As-You-Go",
    "MS-AZR-0017P": "Enterprise Agreement",
    "MS-AZR-0022P": "Enterprise Agreement Dev/Test",
    "MS-AZR-0023P": "Pay-As-You-Go Dev/Test",
    "MS-AZR-0025P": "MSDN Platforms",
    "MS-AZR-0029P": "Visual Studio Enterprise",
    "MS-AZR-0036P": "Azure in Open Licensing",
    "MS-AZR-0044P": "Free Trial",
    "MS-AZR-0059P": "Visual Studio Professional",
    "MS-AZR-0060P": "Visual Studio Test Professional",
    "MS-AZR-0062P": "MSDN Platforms",
    "MS-AZR-0063P": "Visual Studio Enterprise",
    "MS-AZR-0064P": "Visual Studio Enterprise (BizSpark)",
    "MS-AZR-0067P": "Visual Studio Professional",
    "MS-AZR-0111P": "Azure Plan",
    "MS-AZR-0120P": "Azure Pass",
    "MS-AZR-0122P": "Azure Pass",
    "MS-AZR-0125P": "Azure Pass",
    "MS-AZR-0128P": "Microsoft Azure Sponsorship",
    "MS-AZR-0130P": "Azure Pass",
    "MS-AZR-0144P": "Azure Student",
    "MS-AZR-0148P": "Visual Studio Enterprise (MPN)",
    "MS-AZR-0149P": "Azure Plan Dev/Test",
    "MS-AZR-0159P": "Azure Internal",
}


def _resolve_offer_name(quota_id: str | None) -> str:
    """Return the human-readable offer name for a given quota_id."""
    if not quota_id:
        return "Unknown"
    # quota_id may be a full path like "EnterpriseAgreement_2014-09-01"
    # or a raw offer code like "MS-AZR-0017P". Try direct lookup first.
    if quota_id in OFFER_NAMES:
        return OFFER_NAMES[quota_id]
    # Some tenants expose a descriptive string without a standard code
    return quota_id


def list_active_subscriptions(
    credential: AzureCliCredential,
    tenant_id: str,
) -> list[dict[str, Any]]:
    """Return a list of enabled subscriptions for *tenant_id*.

    Each item contains:
        subscription_id, name, offer, offer_id
    """
    client = SubscriptionClient(credential)
    results: list[dict[str, Any]] = []

    for sub in client.subscriptions.list():
        if sub.state and sub.state.lower() != "enabled":
            continue

        quota_id: str | None = None
        if sub.subscription_policies:
            quota_id = sub.subscription_policies.quota_id

        results.append(
            {
                "subscription_id": sub.subscription_id,
                "name": sub.display_name,
                "offer": _resolve_offer_name(quota_id),
                "offer_id": quota_id or "N/A",
            }
        )

    return results


def count_resources(
    credential: AzureCliCredential,
    subscription_ids: list[str],
) -> dict[str, int]:
    """Return a mapping of subscription_id → resource count using Resource Graph.

    Uses a single KQL batch query, which is far more efficient than iterating
    over each subscription individually.
    """
    if not subscription_ids:
        return {}

    client = ResourceGraphClient(credential)

    # KQL: group all resources by subscriptionId and count them
    kql = (
        "Resources"
        " | summarize resource_count = count() by subscriptionId"
    )

    # Resource Graph accepts up to 1000 subscriptions per query; chunk if needed
    CHUNK = 1000
    counts: dict[str, int] = {}

    for i in range(0, len(subscription_ids), CHUNK):
        chunk = subscription_ids[i : i + CHUNK]
        request = QueryRequest(query=kql, subscriptions=chunk)
        response = client.resources(request)

        for row in response.data:
            counts[row["subscriptionId"]] = row["resource_count"]

    # Subscriptions with 0 resources won't appear in the result set
    for sub_id in subscription_ids:
        counts.setdefault(sub_id, 0)

    return counts
