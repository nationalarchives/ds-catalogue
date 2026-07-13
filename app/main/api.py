import logging

from django.core.cache import cache

from app.records.api import wagtail_request_handler
from app.search.api import search_records
from app.search.constants import (
    LONG_FILTER_RESULTS_PER_PAGE,
    LONG_FILTER_SUBJECT_PARAMS,
)

from .constants import (
    GLOBAL_NOTIFICATIONS_CACHE_KEY,
    LANDING_PAGE_CACHE_KEY,
    WAGTAIL_API_CACHE_TIMEOUT,
)

logger = logging.getLogger(__name__)


# TODO: refactor to move to cache.py and remove from api.py,
# since this is not an API call but a cache getter
def fetch_global_notifications() -> dict | None:
    """Fetch and cache global notification data shared across all pages.

    Returns data including:
    - global_alert
    - mourning_notice

    This cache is populated by either the notifications API or the landing
    page API — whichever is called first — and is shared between them to
    avoid duplicate API calls.
    """
    data = cache.get(GLOBAL_NOTIFICATIONS_CACHE_KEY)

    if data is None:
        try:
            response = wagtail_request_handler("/globals/notifications/")
            data = {
                "global_alert": response.get("global_alert"),
                "mourning_notice": response.get("mourning_notice"),
            }
            cache.set(
                GLOBAL_NOTIFICATIONS_CACHE_KEY,
                data,
                timeout=WAGTAIL_API_CACHE_TIMEOUT,
            )
        except Exception as e:
            logger.error(f"Failed to fetch Wagtail notifications: {e}")
            data = None

    return data


# TODO: refactor to move to cache.py and remove from api.py,
# since this is not an API call but a cache getter
def fetch_landing_page_data() -> dict | None:
    """Fetch and cache landing page data from the Wagtail API.

    Returns data including:
    - explore_the_collection.top_pages
    - explore_the_collection.latest_articles

    Global notification data (global_alert, mourning_notice) is stored
    separately under GLOBAL_NOTIFICATIONS_CACHE_KEY and shared with
    fetch_global_notifications().

    Use this only for the catalogue landing page.
    """
    data = cache.get(LANDING_PAGE_CACHE_KEY)

    if data is None:
        try:
            response = wagtail_request_handler("/catalogue/landing/")

            # Populate the shared notifications cache if not already warm,
            # since the landing page response contains the same data.
            if cache.get(GLOBAL_NOTIFICATIONS_CACHE_KEY) is None:
                notifications = {
                    "global_alert": response.get("global_alert"),
                    "mourning_notice": response.get("mourning_notice"),
                }
                cache.set(
                    GLOBAL_NOTIFICATIONS_CACHE_KEY,
                    notifications,
                    timeout=WAGTAIL_API_CACHE_TIMEOUT,
                )

            data = {
                "explore_the_collection": response.get(
                    "explore_the_collection",
                    {},
                ),
            }
            cache.set(
                LANDING_PAGE_CACHE_KEY,
                data,
                timeout=WAGTAIL_API_CACHE_TIMEOUT,
            )
        except Exception as e:
            logger.error(f"Failed to fetch Wagtail landing page data: {e}")
            data = None

    return data


# Landing page getters (for catalogue landing page only)


# TODO: refactor to move to cache.py and remove from api.py,
# since this is not an API call but a cache getter
def get_explore_the_collection() -> dict:
    """Get explore the collection data (top_pages and latest_articles) from cached landing page data."""
    data = fetch_landing_page_data()
    if data is None:
        return {}
    return data.get("explore_the_collection", {})


def fetch_all_subjects() -> list[dict[str, str]]:
    """Fetch all subjects from the search API using longSubject aggregation."""

    api_result = search_records(
        query="",
        results_per_page=LONG_FILTER_RESULTS_PER_PAGE,
        params=LONG_FILTER_SUBJECT_PARAMS,
    )
    # Note:
    # It is expected that the search API will always return the longSubject aggregation
    # as the first aggregation in the list. If the API response structure changes, it must
    # error out and be handled appropriately.
    return api_result.aggregations[0].get("entries", {})
