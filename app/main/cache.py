"""Module for cache management in the main app."""

import logging
import string

from django.core.cache import cache

from .api import fetch_all_subjects
from .constants import SUBJECTS_CACHE_KEY, SUBJECTS_CACHE_TIMEOUT

logger = logging.getLogger(__name__)


def empty_subjects_grouped_by_letter() -> dict:
    """Return an empty dictionary with keys A-Z and empty lists as values."""
    return {letter: [] for letter in string.ascii_uppercase}


def get_subjects_grouped_by_letter() -> dict:
    """Fetch and cache all subjects grouped by their starting letter.

    Returns a dictionary where each key is an uppercase letter (A-Z) and
    the value is a list of subjects starting with that letter.
    """
    data = cache.get(SUBJECTS_CACHE_KEY)

    if data is None:
        # initialize the data structure with empty lists for each letter
        data = empty_subjects_grouped_by_letter()
        try:
            api_result = fetch_all_subjects()

            # group subjects by their starting letter
            for item in api_result:
                data[item["value"][0].upper()].append(item["value"])

            # sort the subjects for each letter
            for letter in data:
                data[letter].sort()

            cache.set(
                SUBJECTS_CACHE_KEY,
                data,
                timeout=SUBJECTS_CACHE_TIMEOUT,
            )
        except Exception as e:
            # Fall back to an empty result if the API request fails
            data = empty_subjects_grouped_by_letter()
            logger.error(f"Failed to fetch all Subjects: {e}")

    return data
