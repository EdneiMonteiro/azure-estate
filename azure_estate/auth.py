from azure.identity import AzureCliCredential

from azure_estate.config import TENANT_ID


def get_credential() -> AzureCliCredential:
    """Return an AzureCliCredential scoped to the configured tenant."""
    return AzureCliCredential(tenant_id=TENANT_ID)
