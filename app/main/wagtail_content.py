import logging

from app.lib.api import JSONAPIClient
from django.conf import settings
from django.core.cache import cache

from .constants import (
    LANDING_PAGE_CACHE_KEY,
    NOTIFICATIONS_CACHE_KEY,
    WAGTAIL_API_CACHE_TIMEOUT,
)

logger = logging.getLogger(__name__)


def fetch_notifications_data() -> dict | None:
    """Fetch and cache notifications data from the Wagtail API.

    Returns data including:
    - global_alert
    - mourning_notice

    Use this for all pages except the catalogue landing page.
    """

    data = cache.get(NOTIFICATIONS_CACHE_KEY)

    if data is None:
        client = JSONAPIClient(settings.WAGTAIL_API_URL)
        try:
            data = client.get("/globals/notifications/")
            cache.set(
                NOTIFICATIONS_CACHE_KEY,
                data,
                timeout=WAGTAIL_API_CACHE_TIMEOUT,
            )
        except Exception as e:
            logger.error(f"Failed to fetch Wagtail notifications: {e}")
            data = None

    return data


def fetch_landing_page_data() -> dict | None:
    """Fetch and cache landing page data from the Wagtail API.

    Returns data including:
    - global_alert
    - mourning_notice
    - explore_the_collection.top_pages
    - explore_the_collection.latest_articles

    Use this only for the catalogue landing page.
    """

    data = cache.get(LANDING_PAGE_CACHE_KEY)

    if data is None:
        client = JSONAPIClient(settings.WAGTAIL_API_URL)
        try:
            data = client.get("/catalogue/landing/")
            cache.set(
                LANDING_PAGE_CACHE_KEY,
                data,
                timeout=WAGTAIL_API_CACHE_TIMEOUT,
            )
        except Exception as e:
            logger.error(f"Failed to fetch Wagtail landing page data: {e}")
            data = None

    return data


# Notification getters (for most pages)


def get_global_alert() -> dict | None:
    """Get global alert from cached notifications data."""
    data = fetch_notifications_data()
    if data is None:
        return None
    return data.get("global_alert")


def get_mourning_notice() -> dict | None:
    """Get mourning notice from cached notifications data."""
    data = fetch_notifications_data()
    if data is None:
        return None
    return data.get("mourning_notice")


# Landing page getters (for catalogue landing page only)


def get_top_pages() -> list:
    """Get top pages from cached landing page data."""
    data = fetch_landing_page_data()
    if data is None:
        return []
    explore_data = data.get("explore_the_collection", {})
    return explore_data.get("top_pages", [])


def get_latest_articles() -> list:
    """Get latest articles from cached landing page data."""
    data = fetch_landing_page_data()
    if data is None:
        return []
    explore_data = data.get("explore_the_collection", {})
    return explore_data.get("latest_articles", [])


def get_landing_page_global_alert() -> dict | None:
    """Get global alert from cached landing page data."""
    data = fetch_landing_page_data()
    if data is None:
        return None
    return data.get("global_alert")


def get_landing_page_mourning_notice() -> dict | None:
    """Get mourning notice from cached landing page data."""
    data = fetch_landing_page_data()
    if data is None:
        return None
    return data.get("mourning_notice")
