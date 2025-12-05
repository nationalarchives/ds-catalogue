import logging
from typing import Any, Dict, List, Optional

from app.lib.api import JSONAPIClient, ResourceNotFound
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


def delivery_options_request_handler(
    iaid: str,
) -> Optional[List[Dict[str, Any]]]:
    """
    Makes an API call to the delivery options service to fetch available
    delivery options for a given iaid.

    Args:
        iaid: The item archive ID to retrieve delivery options for

    Returns:
        The delivery options data for the specified item, or None if:
        - No delivery options are available for this record (404)
        - The API times out
        - The API returns invalid/malformed data
        - Any other API error occurs

    Raises:
        ImproperlyConfigured: If the DELIVERY_OPTIONS_API_URL setting is not configured
    """
    # Validate API URL configuration
    api_url = settings.DELIVERY_OPTIONS_API_URL

    if not api_url:
        raise ImproperlyConfigured("DELIVERY_OPTIONS_API_URL not set")

    try:
        # Create API client with timeout from settings
        client = JSONAPIClient(
            api_url,
            params={"iaid": iaid},
            timeout=settings.DELIVERY_OPTIONS_API_TIMEOUT,
        )

        # Attempt to get data with specific error handling
        data = client.get()

        # Validate response structure - return None if invalid
        if not data or not isinstance(data, list):
            logger.warning(
                f"Invalid API response format for iaid {iaid}: expected a non-empty list"
            )
            return None

        # Ensure each item in the list has the required keys
        for item in data:
            if not all(key in item for key in ["options", "surrogateLinks"]):
                logger.warning(
                    f"Invalid API response for iaid {iaid}: missing required keys"
                )
                return None

        return data

    except ResourceNotFound:
        # 404 - This record doesn't have delivery options, which is OK
        logger.info(f"No delivery options found for iaid {iaid}")
        return None

    except Exception as e:
        # Handle timeouts, connection errors, and all other errors gracefully
        # This is a non-critical API - page should still load without delivery options
        logger.warning(
            f"Delivery options unavailable for iaid {iaid}: {str(e)}"
        )
        return None
