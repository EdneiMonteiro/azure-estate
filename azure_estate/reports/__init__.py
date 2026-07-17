from azure_estate.reports.subscriptions import SubscriptionReport
from azure_estate.reports.resource_groups import ResourceGroupReport
from azure_estate.reports.resource_types import ResourceTypeReport
from azure_estate.reports.resource_details import ResourceDetailReport

REPORT_REGISTRY: dict = {
    "subscriptions": SubscriptionReport,
    "resource_groups": ResourceGroupReport,
    "resource_types": ResourceTypeReport,
    "resource_details": ResourceDetailReport,
}
