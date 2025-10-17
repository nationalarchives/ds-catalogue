import logging

from app.records.models import Record
from app.search.api import search_records

logger = logging.getLogger(__name__)


def get_related_records_by_subjects(
    current_record: Record, limit: int = 3
) -> list[Record]:
    """
    Fetches related records that share subjects with the current record.
    Only returns Item or Piece level records.
    Only applies to TNA records (Non-TNA records don't have subjects).

    Args:
        current_record: The record to find relations for
        limit: Maximum number of related records to return (default 3)

    Returns:
        List of related Record objects at Item or Piece level, or empty list if none found
    """
    if not current_record.is_tna or not current_record.subjects:
        return []

    # Build subject filters for the API
    # Format: ["subject:Navy", "subject:Army", ...]
    subject_filters = [
        f"subject:{subject}" for subject in current_record.subjects
    ]

    # Only tna - function not called in the first place if nonTna
    group_filter = "group:tna"

    # TODO: Consider what levels to look for based on level of current record

    # Build API parameters
    params = {
        "filter": [group_filter] + subject_filters,
        "aggs": [],  # No aggregations needed
    }

    try:
        # Search for related records
        # Request limit + 1 in case current record is in results
        api_result = search_records(
            query="*",  # Match all, filtering by subjects and level
            results_per_page=limit + 1,
            page=1,
            sort="",  # Relevance sort (records matching more subjects rank higher)
            params=params,
        )

        # Filter out the current record from results
        related_records = [
            record
            for record in api_result.records
            if record.iaid != current_record.iaid
        ]

        # Return only the requested limit
        return related_records[:limit]

    except Exception as e:
        # Log the error but don't break the page
        logger.warning(
            f"Failed to fetch related records by subjects for {current_record.iaid}: {e}"
        )
        return []


def get_related_records_by_series(
    current_record: Record, limit: int = 3
) -> list[Record]:
    """
    Fetches related records from the same series as the current record.
    Only returns Item or Piece level records.
    This is a fallback when subject-based relations aren't available.

    Args:
        current_record: The record to find relations for
        limit: Maximum number of related records to return (default 3)

    Returns:
        List of related Record objects from the same series, or empty list if none found
    """
    # Only proceed if record has a series in its hierarchy
    if not current_record.is_tna or not current_record.hierarchy_series:
        return []

    # Get the series reference number
    series = current_record.hierarchy_series
    series_ref = series.reference_number

    if not series_ref:
        logger.warning(
            f"Series {series.iaid} found but has no reference number for record {current_record.iaid}"
        )
        return []

    # Determine the group filter (TNA vs Non-TNA)
    group_filter = "group:tna"

    # Add level filters for Item and Piece
    level_filters = ["level:Item", "level:Piece"]

    # Build API parameters
    params = {
        "filter": [group_filter] + level_filters,
        "aggs": [],  # No aggregations needed
    }

    try:
        # Search for related records using the series reference as the query
        # This will match records whose reference number starts with the series code
        # TODO: when 'sort relevance' is implemented, make sure it is added to the sort parameter below
        api_result = search_records(
            query=series_ref,
            results_per_page=limit + 1,
            page=1,
            sort="",
            params=params,
        )

        # Filter out the current record from results
        related_records = [
            record
            for record in api_result.records
            if record.iaid != current_record.iaid
        ]

        # Return only the requested limit
        return related_records[:limit]

    except Exception as e:
        # Log the error but don't break the page
        logger.warning(
            f"Failed to fetch related records by series for {current_record.iaid}: {e}"
        )
        return []
