import logging

from app.lib.api import JSONAPIClient, ResourceNotFound, rosetta_request_handler
from app.records.models import APIResponse, Record
from django.conf import settings
from django.utils.text import slugify

logger = logging.getLogger(__name__)


def record_details_by_id(id: str, params: dict = {}) -> Record:
    """
    Fetches a record by its ID from the Rosetta API.

    Args:
        id: The record IAID to fetch
        params: Optional additional parameters for the API request

    Returns:
        Record object

    Raises:
        ResourceNotFound: If record doesn't exist
        Exception: If data format is unexpected

    Note:
        The errors are handled by a custom middleware in the app.
    """
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


def record_details_by_ref(reference: str, params: dict = {}):
    """
    Fetches a record by its reference number.

    Args:
        reference: The reference number to search for
        params: Optional additional parameters for the API request

    Note:
        TODO: Implement once Rosetta has support for reference-based lookup
    """
    # TODO: Implement record_details_by_ref once Rosetta has support
    pass


def wagtail_request_handler(uri: str, params: dict = {}) -> dict:
    """
    Prepares and initiates Wagtail API requests using JSONAPIClient.

    Args:
        uri: The API endpoint URI
        params: Query parameters for the request

    Returns:
        Dictionary containing the API response

    Raises:
        Exception: If WAGTAIL_API_URL is not configured
    """
    api_url = settings.WAGTAIL_API_URL
    if not api_url:
        raise Exception("WAGTAIL_API_URL not set")

    client = JSONAPIClient(api_url, params)
    return client.get(uri)


def get_subjects_enrichment(subjects_list: list[str], limit: int = 10) -> dict:
    """
    Makes API call to enrich subjects data for a single record.

    Fetches additional article/content data associated with the provided subject tags
    from the Wagtail CMS article_tags endpoint.

    Args:
        subjects_list: List of subject strings to enrich
        limit: Maximum number of enrichment items to return (default: 10)

    Returns:
        Dictionary containing enrichment data with articles/content related to the subjects,
        or empty dict on failure or if no subjects provided.
    """
    if not subjects_list:
        return {}

    slugified_subjects = [slugify(subject) for subject in subjects_list]
    subjects_param = ",".join(slugified_subjects)

    try:
        params = {"tags": subjects_param, "limit": limit}
        results = wagtail_request_handler("/article_tags/", params)
        return results
    except ResourceNotFound:
        logger.warning(f"No subjects enrichment found for {subjects_param}")
        return {}
    except Exception as e:
        logger.warning(
            f"Failed to fetch subjects enrichment for {subjects_param}: {e}"
        )
        return {}
