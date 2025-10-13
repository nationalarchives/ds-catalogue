import logging

from app.lib.api import JSONAPIClient, ResourceNotFound, rosetta_request_handler
from app.records.models import APIResponse, Record
from app.search.api import search_records
from django.conf import settings


def record_details_by_id(id, params={}) -> Record:
    """Fetches a record by its ID from the Rosetta API.
    The errors are handled by a custom middleware in the app."""
    uri = "get"
    params.update({"id": id})
    results = rosetta_request_handler(uri, params)
    if "data" not in results:
        raise Exception(f"No data returned for id {id}")
    if len(results["data"]) > 1:
        raise Exception(f"Multiple records returned for id {id}")
    if len(results["data"]) == 1:
        record_data = results["data"][0]
        response = APIResponse(record_data)
        return response.record
    raise ResourceNotFound(f"id {id} does not exist")


def record_details_by_ref(reference, params={}):
    # TODO: Implement record_details_by_ref once Rosetta has support
    pass


def wagtail_request_handler(uri, params={}) -> dict:
    """Prepares and initiates Wagtail API requests using JSONAPIClient"""
    api_url = settings.WAGTAIL_API_URL
    if not api_url:
        raise Exception("WAGTAIL_API_URL not set")

    client = JSONAPIClient(api_url, params)
    return client.get(uri)


def get_related_records_by_subjects(
    current_record: Record, limit: int = 3
) -> list[Record]:
    """
    Fetches related records that share subjects with the current record.
    Only applies to TNA records (Non-TNA records don't have subjects).

    Args:
        current_record: The record to find relations for
        limit: Maximum number of related records to return (default 3)

    Returns:
        List of related Record objects, or empty list if none found
    """
    logger = logging.getLogger(__name__)

    # Only proceed if record is TNA and has subjects
    if not current_record.is_tna or not current_record.subjects:
        return []

    # Build subject filters for the API
    # Format: ["subjects:Art", "subjects:Photography", ...]
    # Note: The API uses "subjects" (plural) not "subject"
    subject_filters = [
        f"subjects:{subject}" for subject in current_record.subjects
    ]

    # Determine the group filter (TNA vs Non-TNA)
    group_filter = "group:tna" if current_record.is_tna else "group:nonTna"

    # Build API parameters
    params = {
        "filter": [group_filter] + subject_filters,
        "aggs": [],  # No aggregations needed
    }

    try:
        # Search for related records
        # Request limit + 1 in case current record is in results
        api_result = search_records(
            query="*",  # Match all, filtering by subjects
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
            f"Failed to fetch related records for {current_record.iaid}: {e}"
        )
        return []

def get_related_records_by_series(
    current_record: Record, limit: int = 3
) -> list[Record]:
    """
    Fetches related records in the same Series as the current record.
    
    Args:
        current_record: The record to find relations for
        limit: Maximum number of related records to return (default 3)
    
    Returns:
        List of related Record objects, or empty list if none found
    """

    logger = logging.getLogger(__name__)
    
    # Only proceed if record is TNA and has a series
    print(f"Hierarchy series: {current_record.hierarchy_series}")
    if not current_record.is_tna or not current_record.hierarchy_series:
        return []
    
    # Get the series reference number
    print(f"Series reference: {current_record.hierarchy_series.reference_number}")
    series_ref = current_record.hierarchy_series.reference_number
    
    # Filter by series reference
    group_filter = "group:tna"
    reference_filter = f"reference:{series_ref}"
    
    # Build API parameters
    params = {
        "filter": [group_filter, reference_filter],
        "aggs": [],
    }
    
    try:
        # Search for related records in the same series
        # Request limit + 1 in case current record is in results
        api_result = search_records(
            query="*",
            results_per_page=limit + 1,
            page=1,
            sort="",
            params=params,
        )
        
        # Filter out the current record from results
        related_records = [
            record for record in api_result.records 
            if record.iaid != current_record.iaid
        ]
        
        if related_records:
            logger.info(
                f"Found {len(related_records[:limit])} related records for {current_record.iaid} by series {series_ref}"
            )
        
        return related_records[:limit]
        
    except Exception as e:
        logger.warning(
            f"Failed to fetch related records by series for {current_record.iaid}: {e}"
        )
        return []