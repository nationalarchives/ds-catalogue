import logging

from app.search.api import search_records
from app.search.constants import (
    LONG_FILTER_RESULTS_PER_PAGE,
    LONG_FILTER_SUBJECT_PARAMS,
)

logger = logging.getLogger(__name__)


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
