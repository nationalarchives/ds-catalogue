"""Module for cache management in the main app."""

import logging

from django.core.cache import cache

from app.records.api import wagtail_request_handler

from .api import fetch_all_subjects
from .constants import (
    GLOBAL_NOTIFICATIONS_CACHE_KEY,
    LANDING_PAGE_CACHE_KEY,
    SUBJECTS_CACHE_KEY,
    SUBJECTS_CACHE_TIMEOUT,
    WAGTAIL_API_CACHE_TIMEOUT,
)

logger = logging.getLogger(__name__)


def get_subjects_grouped_by_letter() -> dict:
    """Fetch and cache all subjects grouped by their starting letter.

    Returns a dictionary where each key is an uppercase letter (A-Z) and
    the value is a list of subjects starting with that letter.
    """
    data = cache.get(SUBJECTS_CACHE_KEY, None)

    if data is None:
        # initialize the data structure with empty lists for each letter
        data = {}
        try:
            api_result = fetch_all_subjects()

            # group subjects by their starting letter
            for item in api_result:
                key = item["value"][0].upper()
                if key not in data:
                    data[key] = []
                data[key].append(item["value"])

            # sort the subjects for each letter
            for letter in data:
                data[letter].sort()

            data = dict(sorted(data.items()))

            if data:
                cache.set(
                    SUBJECTS_CACHE_KEY,
                    data,
                    timeout=SUBJECTS_CACHE_TIMEOUT,
                )
        except Exception as e:
            # Fall back to an empty result if the API request fails,
            # incorrectly formatted data is returned
            data = {}
            logger.error(f"Failed to fetch all Subjects: {e}")

    return data


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


def get_explore_the_collection() -> dict:
    """Get explore the collection data (top_pages and latest_articles) from cached landing page data."""
    data = fetch_landing_page_data()
    if data is None:
        return {}
    return data.get("explore_the_collection", {})
