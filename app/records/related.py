import logging
from typing import List, Set

from app.records.constants import TNA_LEVELS
from app.records.models import Record
from app.search.api import search_records

logger = logging.getLogger(__name__)


# Define which TNA levels should be considered "similar" for related records
# Using level codes from TNA_LEVELS: 1=Department, 2=Division, 3=Series,
# 4=Sub-series, 5=Sub-sub-series, 6=Piece, 7=Item
def make_tna_similar_levels(min_level=1, max_level=7):
    return {
        i: (
            [i, i + 1]
            if i == min_level
            else [i - 1, i] if i == max_level else [i - 1, i, i + 1]
        )
        for i in range(min_level, max_level + 1)
    }


TNA_SIMILAR_LEVELS = make_tna_similar_levels()


def get_similar_tna_levels(level_code: int) -> List[str]:
    """
    Get TNA level names that are similar to the given level code.

    Args:
        level_code: The level code of the current TNA record (1-7)

    Returns:
        List of TNA level names to search for
    """
    # Get similar level codes
    similar_codes = TNA_SIMILAR_LEVELS.get(level_code, [level_code])

    # Convert to level names
    level_names = []
    for code in similar_codes:
        if level_name := TNA_LEVELS.get(str(code)):
            level_names.append(level_name)

    return level_names


def get_related_records_by_subjects(
    current_record: Record, limit: int = 3
) -> list[Record]:
    """
    Fetches related records that share subjects with the current record.
    Prioritizes records at similar levels and with more matching subjects.
    Only applies to TNA records (Non-TNA records don't have subjects).

    Args:
        current_record: The record to find relations for
        limit: Maximum number of related records to return (default 3)

    Returns:
        List of related Record objects at similar levels, sorted by
        number of matching subjects, or empty list if none found
    """
    # Only TNA records have subjects
    if not current_record.is_tna or not current_record.subjects:
        return []

    if not current_record.level_code:
        logger.warning(f"TNA record {current_record.iaid} has no level_code")
        return []

    # Get appropriate level filters for TNA records
    similar_levels = get_similar_tna_levels(current_record.level_code)

    if not similar_levels:
        logger.warning(
            f"No similar levels found for TNA level_code {current_record.level_code}"
        )
        return []

    logger.debug(
        f"Searching for related records to {current_record.level} "
        f"at levels: {similar_levels}"
    )

    # Strategy 1: Try to find records with ALL subjects first (if not too many)
    if len(current_record.subjects) <= 3:
        records = _search_with_all_subjects(
            current_record, similar_levels, limit
        )
        if len(records) >= limit:
            return records[:limit]

    # Strategy 2: Find records with ANY subjects and rank by match count
    all_matches = _search_and_rank_by_subject_matches(
        current_record,
        similar_levels,
        limit * 3,  # Get more candidates to ensure best matches
    )

    return all_matches[:limit]


def _search_with_all_subjects(
    current_record: Record, similar_levels: List[str], limit: int
) -> list[Record]:
    """
    Search for TNA records that have ALL the same subjects at similar levels.
    Since multiple level filters use AND logic, we search each level separately
    and combine results to achieve OR behavior.

    Args:
        current_record: The TNA record to find relations for
        similar_levels: List of TNA level names to filter by
        limit: Maximum number of related records to return

    Returns:
        List of records matching all subjects at similar levels
    """
    all_results = []
    seen_iaids = set()

    # Search each level separately (to get OR behavior for levels)
    for level in similar_levels:
        # Build filters list - each filter is a separate parameter
        filters = ["group:tna", f"level:{level}"]

        # Add all subject filters (these use AND logic - must match ALL)
        for subject in current_record.subjects:
            filters.append(f"subject:{subject}")

        params = {
            "filter": filters,
            "aggs": [],
        }

        try:
            api_result = search_records(
                query="*",
                results_per_page=limit,
                page=1,
                sort="",
                params=params,
            )

            for record in api_result.records:
                # Skip the current record and duplicates
                if (
                    record.iaid != current_record.iaid
                    and record.iaid not in seen_iaids
                ):
                    all_results.append(record)
                    seen_iaids.add(record.iaid)

                    # Stop if we have enough results
                    if len(all_results) >= limit:
                        return all_results

        except Exception as e:
            logger.debug(
                f"No TNA records with all subjects at level '{level}' "
                f"found for {current_record.iaid}: {e}"
            )
            continue

    return all_results


def _search_and_rank_by_subject_matches(
    current_record: Record, similar_levels: List[str], fetch_limit: int
) -> list[Record]:
    """
    Search for TNA records with ANY matching subjects at similar levels
    and rank by match count.

    Args:
        current_record: The TNA record to find relations for
        similar_levels: List of TNA level names to filter by
        fetch_limit: Maximum number of candidates to fetch

    Returns:
        List of records sorted by number of matching subjects (descending)
    """
    # Track records and their match counts
    record_matches = (
        {}
    )  # {iaid: (Record, set_of_matching_subjects, level_distance)}

    # Since multiple level filters use AND logic, we need to search each level separately
    # to get OR behavior (records at ANY of the similar levels)
    for level in similar_levels:
        for subject in current_record.subjects:
            params = {
                "filter": ["group:tna", f"subject:{subject}", f"level:{level}"],
                "aggs": [],
            }

            try:
                api_result = search_records(
                    query="*",
                    results_per_page=10,  # Smaller sample per subject/level combo
                    page=1,
                    sort="",
                    params=params,
                )

                for record in api_result.records:
                    # Skip the current record
                    if record.iaid == current_record.iaid:
                        continue

                    if record.iaid not in record_matches:
                        # Calculate level distance for secondary sorting
                        level_distance = abs(
                            record.level_code - current_record.level_code
                        )
                        record_matches[record.iaid] = (
                            record,
                            set(),
                            level_distance,
                        )

                    # Add this subject to the matching subjects set
                    record_matches[record.iaid][1].add(subject)

            except Exception as e:
                logger.debug(
                    f"Failed to search for subject '{subject}' at level '{level}': {e}"
                )
                continue

    # Sort records by:
    # 1. Number of matching subjects (descending)
    # 2. Level distance (ascending) - prefer same/nearby levels
    sorted_records = sorted(
        record_matches.values(),
        key=lambda x: (
            -len(x[1]),  # Negative for descending sort on match count
            x[2],  # Ascending sort on level distance
        ),
    )

    # Log match quality for debugging
    if sorted_records and logger.isEnabledFor(logging.DEBUG):
        for record, matching_subjects, level_distance in sorted_records[:5]:
            logger.debug(
                f"TNA record {record.iaid} ({record.level}) matches "
                f"{len(matching_subjects)}/{len(current_record.subjects)} subjects, "
                f"level_distance={level_distance}: {matching_subjects}"
            )

    # Return just the Record objects
    return [record for record, _, _ in sorted_records[:fetch_limit]]


def get_related_records_by_series(
    current_record: Record, limit: int = 3
) -> list[Record]:
    """
    Fetches related records from the same series as the current record.
    For TNA records, prioritizes records at similar levels.
    This is a fallback when subject-based relations aren't available.

    Args:
        current_record: The record to find relations for
        limit: Maximum number of related records to return (default 3)

    Returns:
        List of related Record objects from the same series at similar levels
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

    # Get similar levels based on current record's level
    if current_record.level_code:
        similar_levels = get_similar_tna_levels(current_record.level_code)
    else:
        # Fallback to Item/Piece if no level code
        logger.warning(f"TNA record {current_record.iaid} has no level_code")
        similar_levels = ["Item", "Piece"]

    # Since multiple level filters use AND logic, search each level separately
    all_results = []
    seen_iaids = set()

    for level in similar_levels:
        params = {
            "filter": ["group:tna", f"level:{level}"],
            "aggs": [],
        }

        try:
            api_result = search_records(
                query=series_ref,
                results_per_page=limit,
                page=1,
                sort="",
                params=params,
            )

            for record in api_result.records:
                # Skip current record and duplicates
                if (
                    record.iaid != current_record.iaid
                    and record.iaid not in seen_iaids
                ):
                    # Calculate level distance if possible
                    if current_record.level_code and record.level_code:
                        level_distance = abs(
                            record.level_code - current_record.level_code
                        )
                    else:
                        level_distance = 0

                    all_results.append((level_distance, record))
                    seen_iaids.add(record.iaid)

        except Exception as e:
            logger.debug(
                f"Failed to fetch related records by series at level '{level}' "
                f"for {current_record.iaid}: {e}"
            )
            continue

    # Sort by level distance and return top results
    all_results.sort(key=lambda x: x[0])
    return [record for _, record in all_results[:limit]]
