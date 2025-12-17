import logging
import random
from typing import List

from app.records.constants import RELATED_RECORDS_FETCH_LIMIT, TNA_LEVELS
from app.records.models import Record
from app.search.api import search_records

logger = logging.getLogger(__name__)

_LEVEL_FILTERS_SERIES_TO_ITEM = [
    f"level:{TNA_LEVELS[str(i)]}" for i in range(3, 8)
]


def get_tna_related_records_by_subjects(
    current_record: Record, limit: int = 3, timeout: int = None
) -> list[Record]:
    """
    Fetches related records that share subjects with the current record.
    Returns a random selection from matching records.
    Only applies to TNA records (Non-TNA records don't have subjects).

    Args:
        current_record: The record to find relations for
        limit: Maximum number of related records to return (default 3)
        timeout: Request timeout in seconds

    Returns:
        List of related Record objects (random selection), or empty list if none found
    """
    # Only TNA records have subjects
    if not current_record.is_tna or not current_record.subjects:
        return []

    # Fetch 10 candidates
    list_of_related_records = _search_by_subject_matches(
        current_record,
        fetch_limit=RELATED_RECORDS_FETCH_LIMIT,
        timeout=timeout,
    )

    # Randomly select up to 'limit' records from the candidates
    if len(list_of_related_records) <= limit:
        return list_of_related_records

    return random.sample(list_of_related_records, limit)


def _search_with_all_subjects(
    current_record: Record, fetch_limit: int, timeout: int = None
) -> dict:
    """
    Search for records by adding all subjects as filters.

    Currently uses OR logic (matches ANY subject) due to API limitations.
    When logical AND is implemented, this will return only records matching
    ALL subjects, providing more closely related results.

    Args:
        current_record: The TNA record to find relations for
        fetch_limit: Maximum number of matches to fetch
        timeout: Request timeout in seconds

    Returns:
        Dictionary of record matches keyed by record ID, or empty dict on error
    """
    record_matches = {}

    filters = ["group:tna"]

    # Add pre-computed level filters
    filters.extend(_LEVEL_FILTERS_SERIES_TO_ITEM)

    for subject in current_record.subjects:
        filters.append(f"subject:{subject}")

    params = {"filter": filters, "aggs": []}

    try:
        api_result = search_records(
            query="*",
            results_per_page=fetch_limit,
            page=1,
            sort="",
            params=params,
            timeout=timeout,
        )

        for record in api_result.records:
            if record.id != current_record.id:
                record_matches[record.id] = record

    except Exception as e:
        logger.debug(f"Failed to search with all subjects: {e}")

    return record_matches


def _search_individual_subjects(
    current_record: Record,
    fetch_limit: int,
    record_matches: dict,
    timeout: int = None,
) -> dict:
    """Search by individual subjects until enough matches are found.

    Args:
        current_record: The TNA record to find relations for
        fetch_limit: Maximum number of additional matches to fetch
        record_matches: Existing matches to add to
        timeout: Request timeout in seconds

    Returns:
        Updated dictionary of record matches
    """

    record_subject_list = list(current_record.subjects)

    # By using a random shuffle, we won't get the same related records appearing over and again
    random.shuffle(record_subject_list)

    for subject in record_subject_list:
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
                timeout=timeout,
            )

            for record in api_result.records:
                if record.id == current_record.id:
                    continue

                if record.id not in record_matches:
                    record_matches[record.id] = record

        except Exception as e:
            logger.debug(f"Failed to search for subject '{subject}': {e}")

    return record_matches


def _search_by_subject_matches(
    current_record: Record, fetch_limit: int, timeout: int = None
) -> list[Record]:
    """
    Search for TNA records with matching subjects using a two-stage strategy.

    Stage 1: Search with ALL subjects combined (attempts logical AND, but currently
             uses OR due to API limitations)
    Stage 2: If insufficient results, search individual subjects with random shuffle
             to provide variety across page loads

    When logical AND is implemented in the search API, stage 1 will return more
    closely related records that match ALL subjects rather than ANY subject.

    Args:
        current_record: The TNA record to find relations for
        fetch_limit: Maximum number of candidates to fetch
        timeout: Request timeout in seconds

    Returns:
        List of records (unsorted, may contain fewer than fetch_limit)
    """
    # TODO: When filter logical AND is implemented, this function will provide even more closely related records

    # Try searching with all subjects first
    record_matches = _search_with_all_subjects(
        current_record, fetch_limit, timeout
    )

    # If not enough results, search individual subjects
    if len(record_matches) < fetch_limit:
        record_matches = _search_individual_subjects(
            current_record,
            fetch_limit - len(record_matches),
            record_matches,
            timeout,
        )

    return list(record_matches.values())


def get_related_records_by_series(
    current_record: Record, limit: int = 3, timeout: int = None
) -> list[Record]:
    """
    Fetches related records from the same series as the current record.
    This is a fallback when subject-based relations aren't available.

    Args:
        current_record: The record to find relations for
        limit: Maximum number of related records to return (default 3)
        timeout: Request timeout in seconds

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
            f"Series {series.id} found but has no reference number "
            f"for record {current_record.id}"
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
            timeout=timeout,
        )

        results = []
        for record in api_result.records:
            # Skip current record
            if record.id != current_record.id:
                results.append(record)

            if len(results) >= limit:
                break

        return results

    except Exception as e:
        logger.debug(
            f"Failed to search for series records with ref '{series_ref}': {e}"
        )
        return []
