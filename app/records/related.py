import logging
import random
from typing import List

from app.records.constants import TNA_LEVELS
from app.records.models import Record
from app.search.api import search_records

logger = logging.getLogger(__name__)

_LEVEL_FILTERS_SERIES_TO_ITEM = [
    f"level:{TNA_LEVELS[str(i)]}" for i in range(3, 8)
]


def get_related_records_by_subjects(
    current_record: Record, limit: int = 3
) -> list[Record]:
    """
    Fetches related records that share subjects with the current record.
    Returns a random selection from matching records.
    Only applies to TNA records (Non-TNA records don't have subjects).

    Args:
        current_record: The record to find relations for
        limit: Maximum number of related records to return (default 3)

    Returns:
        List of related Record objects (random selection), or empty list if none found
    """
    # Only TNA records have subjects
    if not current_record.is_tna or not current_record.subjects:
        return []

    # Fetch 10 candidates
    all_matches = _search_by_subject_matches(
        current_record,
        fetch_limit=10,
    )

    # Randomly select up to 'limit' records from the candidates
    if len(all_matches) <= limit:
        return all_matches

    return random.sample(all_matches, limit)


def _search_with_all_subjects(current_record: Record, fetch_limit: int) -> dict:
    """Search for records matching ALL subjects."""
    record_matches = {}

    filters = ["group:tna"]

    # Add pre-computed level filters
    filters.extend(_LEVEL_FILTERS_SERIES_TO_ITEM)

    for subject in current_record.subjects:
        filters.append(f"subject:{subject}")

    params = {"filter": filters, "aggs": []}

    # TODO: When filter AND is implemented, this function will provide even more closely related records
    try:
        api_result = search_records(
            query="*",
            results_per_page=fetch_limit,
            page=1,
            sort="",
            params=params,
        )

        for record in api_result.records:
            if record.iaid != current_record.iaid:
                record_matches[record.iaid] = record

    except Exception as e:
        logger.debug(f"Failed to search with all subjects: {e}")

    return record_matches


def _search_individual_subjects(
    current_record: Record, fetch_limit: int, record_matches: dict
) -> None:
    """Search by individual subjects until enough matches are found."""

    remaining_subjects = list(current_record.subjects)
    random.shuffle(remaining_subjects)

    for subject in remaining_subjects:
        if len(record_matches) >= fetch_limit:
            break

        filters = ["group:tna", f"subject:{subject}"]
        # Add pre-computed level filters
        filters.extend(_LEVEL_FILTERS_SERIES_TO_ITEM)

        params = {"filter": filters, "aggs": []}

        try:
            api_result = search_records(
                query="*",
                results_per_page=fetch_limit,
                page=1,
                sort="",
                params=params,
            )

            for record in api_result.records:
                if record.iaid == current_record.iaid:
                    continue

                if record.iaid not in record_matches:
                    record_matches[record.iaid] = record

        except Exception as e:
            logger.debug(f"Failed to search for subject '{subject}': {e}")


def _search_by_subject_matches(
    current_record: Record, fetch_limit: int
) -> list[Record]:
    """
    Search for TNA records with matching subjects.
    First tries ALL subjects (AND), then falls back to individual subjects until enough matches found.

    Args:
        current_record: The TNA record to find relations for
        fetch_limit: Maximum number of candidates to fetch

    Returns:
        List of records (unsorted)
    """
    # Try searching with all subjects first
    record_matches = _search_with_all_subjects(current_record, fetch_limit)

    # If not enough results, search individual subjects
    if len(record_matches) < fetch_limit:
        _search_individual_subjects(current_record, fetch_limit, record_matches)

    return list(record_matches.values())


# TODO: related by series is only partially correct because, at the moment, records aren't retrieved in order of relevance
def get_related_records_by_series(
    current_record: Record, limit: int = 3
) -> list[Record]:
    """
    Fetches related records from the same series as the current record.
    This is a fallback when subject-based relations aren't available.

    Args:
        current_record: The record to find relations for
        limit: Maximum number of related records to return (default 3)

    Returns:
        List of related Record objects from the same series
    """
    # Only proceed if record has a series in its hierarchy
    if not current_record.is_tna or not current_record.hierarchy_series:
        return []

    series = current_record.hierarchy_series
    series_ref = series.reference_number

    if not series_ref:
        logger.warning(
            f"Series {series.iaid} found but has no reference number "
            f"for record {current_record.iaid}"
        )
        return []

    params = {
        "filter": ["group:tna"],
        "aggs": [],
    }

    try:
        api_result = search_records(
            query=series_ref,
            results_per_page=limit
            * 2,  # Get extra to filter out current record
            page=1,
            sort="",
            params=params,
        )

        results = []
        for record in api_result.records:
            # Skip current record
            if record.iaid != current_record.iaid:
                results.append(record)

            if len(results) >= limit:
                break

        return results

    except Exception as e:
        logger.debug(
            f"Failed to search for series records with ref '{series_ref}': {e}"
        )
        return []
