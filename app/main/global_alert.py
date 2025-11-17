import logging

from app.lib.api import JSONAPIClient
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


# TODO: temporary implementation to fetch global alert data with caching
def fetch_global_alert_api_data():
    global_alert = cache.get("global_alert_api_data") or {}
    if not global_alert:
        global_alerts_client = JSONAPIClient(settings.WAGTAIL_API_URL)
        global_alerts_client.add_parameters(
            {"fields": "_,global_alert,mourning_notice"}
        )
        try:
            global_alert = global_alerts_client.get(
                f"/pages/{settings.WAGTAIL_HOME_PAGE_ID}/"
            )
        except Exception as e:
            logger.error(e)
            global_alert = {}

        # 15 minutes
        cache.set("global_alert_api_data", global_alert, timeout=60 * 15)

    return global_alert
