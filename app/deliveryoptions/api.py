import logging
from typing import Any, Dict, List, Optional

from app.lib.api import JSONAPIClient, ResourceNotFound
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from app.deliveryoptions.constants import DELIVERY_OPTIONS_API_TIMEOUT

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
        The delivery options data for the specified item, or None if no
        delivery options are available for this record (404)

    Raises:
        ImproperlyConfigured: If the DELIVERY_OPTIONS_API_URL setting is not configured
        Exception: If the delivery options service is unavailable or returns invalid data
    """
    # Validate API URL configuration
    api_url = settings.DELIVERY_OPTIONS_API_URL

    if not api_url:
        raise ImproperlyConfigured("DELIVERY_OPTIONS_API_URL not set")

    try:
        # Create API client
        client = JSONAPIClient(api_url, timeout=DELIVERY_OPTIONS_API_TIMEOUT)
        client.add_parameters({"iaid": iaid})

        # Attempt to get data with specific error handling
        data = client.get()

        # Validate response structure
        if not data or not isinstance(data, list):
            raise ValueError(
                "Invalid API response format: expected a non-empty list"
            )

        # Ensure each item in the list has the required keys
        for item in data:
            if not all(key in item for key in ["options", "surrogateLinks"]):
                raise ValueError("Invalid API response: missing required keys")

        return data

    except ResourceNotFound:
        # 404 - This record doesn't have delivery options, which is normal
        logger.info(f"No delivery options found for iaid {iaid}")
        return None

    except Exception as e:
        # Log the original exception for debugging
        logger.error(f"Delivery options request error: {str(e)}")
        raise Exception("Delivery Options database is currently unavailable")
