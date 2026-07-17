from __future__ import annotations

import pandas as pd

from azure_estate.auth import get_credential
from azure_estate.collectors.subscriptions import count_resources, list_active_subscriptions
from azure_estate.config import TENANT_ID
from azure_estate.reports.base import BaseReport


class SubscriptionReport(BaseReport):
    """Lists all enabled subscriptions in the tenant with their resource counts."""

    name = "subscriptions"

    def run(self) -> pd.DataFrame:
        credential = get_credential()

        print("  Fetching active subscriptions…")
        subs = list_active_subscriptions(credential, TENANT_ID)

        if not subs:
            print("  No enabled subscriptions found.")
            return pd.DataFrame(
                columns=["ID", "Nome", "Offer", "Offer ID", "Qtd. Recursos"]
            )

        print(f"  Found {len(subs)} subscription(s). Counting resources…")
        sub_ids = [s["subscription_id"] for s in subs]
        resource_counts = count_resources(credential, sub_ids)

        rows = [
            {
                "ID": s["subscription_id"],
                "Nome": s["name"],
                "Offer": s["offer"],
                "Offer ID": s["offer_id"],
                "Qtd. Recursos": resource_counts.get(s["subscription_id"], 0),
            }
            for s in subs
        ]

        df = pd.DataFrame(rows)
        df.sort_values("Qtd. Recursos", ascending=False, inplace=True, ignore_index=True)
        return df
