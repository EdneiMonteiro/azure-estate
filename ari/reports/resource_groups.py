from __future__ import annotations

import pandas as pd

from ari.auth import get_credential
from ari.collectors.resource_groups import list_resource_groups
from ari.config import TENANT_ID
from ari.reports.base import BaseReport


class ResourceGroupReport(BaseReport):
    """Lists all resource groups across active subscriptions with their resource counts."""

    name = "resource_groups"

    def run(self) -> pd.DataFrame:
        credential = get_credential()

        print("  Fetching resource groups…")
        data = list_resource_groups(credential, TENANT_ID)

        if not data:
            print("  No resource groups found.")
            return pd.DataFrame(
                columns=["Subscription", "Resource Group", "Localização", "Qtd. Recursos"]
            )

        print(f"  Found {len(data)} resource group(s).")

        rows = [
            {
                "Subscription": d["subscription_name"],
                "Resource Group": d["rg_name"],
                "Localização": d["location"],
                "Qtd. Recursos": d["resource_count"],
            }
            for d in data
        ]

        df = pd.DataFrame(rows)
        df.sort_values("Qtd. Recursos", ascending=False, inplace=True, ignore_index=True)
        return df
