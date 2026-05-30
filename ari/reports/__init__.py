from ari.reports.subscriptions import SubscriptionReport
from ari.reports.resource_groups import ResourceGroupReport
from ari.reports.resource_types import ResourceTypeReport
from ari.reports.resource_details import ResourceDetailReport

REPORT_REGISTRY: dict = {
    "subscriptions": SubscriptionReport,
    "resource_groups": ResourceGroupReport,
    "resource_types": ResourceTypeReport,
    "resource_details": ResourceDetailReport,
}
