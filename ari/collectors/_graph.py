from __future__ import annotations

from typing import Any

from azure.mgmt.resourcegraph import ResourceGraphClient
from azure.mgmt.resourcegraph.models import QueryRequest

CHUNK = 1000


def run_graph_query(
    client: ResourceGraphClient,
    subscription_ids: list[str],
    kql: str,
) -> list[dict[str, Any]]:
    """Execute a Resource Graph KQL query with chunking and full pagination.

    Splits *subscription_ids* into batches of up to 1 000 (API limit) and
    follows skip_token pagination so the full result set is always returned.
    """
    results: list[dict[str, Any]] = []

    for i in range(0, len(subscription_ids), CHUNK):
        chunk = subscription_ids[i : i + CHUNK]
        skip_token: str | None = None

        while True:
            request = QueryRequest(
                query=kql,
                subscriptions=chunk,
                **({"options": {"$skipToken": skip_token}} if skip_token else {}),
            )
            response = client.resources(request)
            results.extend(response.data)
            skip_token = getattr(response, "skip_token", None)
            if not skip_token:
                break

    return results
