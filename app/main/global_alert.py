import logging

from app.lib.api import JSONAPIClient
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

GLOBAL_ALERT_CACHE_TIMEOUT = 60 * 15  # 15 minutes


# TODO: temporary implementation to fetch global alert data with caching
def fetch_global_alert_api_data():
    global_alert = cache.get("global_alert_api_data")
    if global_alert is None:
        global_alerts_client = JSONAPIClient(
            settings.WAGTAIL_API_URL, timeout=settings.WAGTAIL_API_TIMEOUT
        )
        global_alerts_client.add_parameters(
            {"fields": "_,global_alert,mourning_notice"}
        )
        try:
            global_alert = global_alerts_client.get(
                f"/pages/{settings.WAGTAIL_HOME_PAGE_ID}/"
            )

            # cache the result
            cache.set(
                "global_alert_api_data",
                global_alert,
                timeout=GLOBAL_ALERT_CACHE_TIMEOUT,
            )
        except Exception as e:
            logger.error(f"Failed to fetch global alerts: {e}")
            global_alert = None

    return global_alert
