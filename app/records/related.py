import logging
from typing import List, Set

from app.records.constants import TNA_LEVELS
from app.records.models import Record
from app.search.api import search_records

logger = logging.getLogger(__name__)


def get_related_records_by_subjects(
    current_record: Record, limit: int = 3
) -> list[Record]:
    """
    Fetches related records that share subjects with the current record.
    Prioritises records with more matching subjects.
    Only applies to TNA records (Non-TNA records don't have subjects).

    Args:
        current_record: The record to find relations for
        limit: Maximum number of related records to return (default 3)

    Returns:
        List of related Record objects, sorted by
        number of matching subjects, or empty list if none found
    """
    # Only TNA records have subjects
    if not current_record.is_tna or not current_record.subjects:
        return []

    # Find records with matching subjects and rank by match count
    all_matches = _search_and_rank_by_subject_matches(
        current_record,
        limit * 3,  # Get more candidates to ensure best matches
    )

    return all_matches[:limit]


def _calculate_level_distance(record: Record, current_record: Record) -> int:
    """Calculate the level distance between two records."""
    if current_record.level_code and record.level_code:
        return abs(record.level_code - current_record.level_code)
    return 0


def _add_record_match(
    record_matches: dict,
    record: Record,
    current_record: Record,
    matching_subjects: set,
) -> None:
    """Add a record to the matches dictionary."""
    level_distance = _calculate_level_distance(record, current_record)
    record_matches[record.iaid] = (record, matching_subjects, level_distance)


def _search_with_all_subjects(current_record: Record, fetch_limit: int) -> dict:
    """Search for records matching ALL subjects."""
    record_matches = {}

    filters = ["group:tna"]
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
        )

        for record in api_result.records:
            if record.iaid != current_record.iaid:
                _add_record_match(
                    record_matches,
                    record,
                    current_record,
                    set(current_record.subjects),
                )

    except Exception as e:
        logger.debug(f"Failed to search with all subjects: {e}")

    return record_matches


def _search_individual_subjects(
    current_record: Record, fetch_limit: int, record_matches: dict
) -> None:
    """Search by individual subjects until enough matches are found."""
    import random

    remaining_subjects = list(current_record.subjects)
    random.shuffle(remaining_subjects)

    for subject in remaining_subjects:
        if len(record_matches) >= fetch_limit:
            break

        params = {"filter": ["group:tna", f"subject:{subject}"], "aggs": []}

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
                    _add_record_match(
                        record_matches, record, current_record, set()
                    )

                record_matches[record.iaid][1].add(subject)

        except Exception as e:
            logger.debug(f"Failed to search for subject '{subject}': {e}")


def _sort_and_limit_results(
    record_matches: dict, fetch_limit: int
) -> list[Record]:
    """Sort records by match count and level distance, then limit results."""
    sorted_records = sorted(
        record_matches.values(),
        key=lambda x: (-len(x[1]), x[2]),
    )
    return [record for record, _, _ in sorted_records[:fetch_limit]]


def _search_and_rank_by_subject_matches(
    current_record: Record, fetch_limit: int
) -> list[Record]:
    """
    Search for TNA records with matching subjects.
    First tries ALL subjects (AND), then falls back to individual subjects until enough matches found.

    Args:
        current_record: The TNA record to find relations for
        fetch_limit: Maximum number of candidates to fetch

    Returns:
        List of records sorted by number of matching subjects (descending)
    """
    # Try searching with all subjects first
    record_matches = _search_with_all_subjects(current_record, fetch_limit)

    # If not enough results, search individual subjects
    if len(record_matches) < fetch_limit:
        _search_individual_subjects(current_record, fetch_limit, record_matches)

    return _sort_and_limit_results(record_matches, fetch_limit)


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
