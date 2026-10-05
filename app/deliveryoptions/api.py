import logging
from typing import Any
from typing import Any

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .api import JSONAPIClient
from .exceptions import APIResourceNotFound

logger = logging.getLogger(__name__)


def delivery_options_request_handler(
    iaid: str,
    reader_type: str | None = None,
    timeout: int = None,
) -> dict[str, Any] | None:
    """
    Makes an API call to DOAPI (the new delivery-options service) to
    fetch delivery options for a given iaid.

    Not a drop-in replacement for delivery_options_request_handler
    (api.py) — genuinely different response shapes. That one talks to
    the old service (a JSON list, "options"/"surrogateLinks" keys);
    this one talks to DOAPI (a single JSON object, snake_case:
    "delivery_option"/"surrogate_links"/etc).

    Args:
        iaid: The item archive ID to retrieve delivery options for
        reader_type: StaffIn | OnSitePublic | OffSite | Subscription.
            Omit to let DOAPI default to OffSite.

    Returns:
        The delivery options dict for the specified item, or None if
        the record has no delivery options (404)

    Raises:
        ImproperlyConfigured: If DOAPI_URL is not configured
        Exception: If DOAPI is unavailable or returns invalid data.
            NOTE: JSONAPIClient.get() only distinguishes 400/403/404
            specifically — DOAPI's 401 (bad key), 422 (unsupported
            level/no delivery option), 429 (rate limited), and 503
            (Rosetta/DORIS down) all collapse into the same generic
            APIRequestFailedError here. If any of those need telling
            apart later, that's a JSONAPIClient change, not something
            fixable in this function alone.
    """
    api_url = settings.DOAPI_URL

    if not api_url:
        raise ImproperlyConfigured("DOAPI_URL not set")

    try:
        client = JSONAPIClient(api_url)
        client.add_headers({"X-API-Key": settings.DOAPI_API_KEY})
        if reader_type:
            client.add_parameters({"reader_type": reader_type})

        data = client.get(f"delivery-options/rosetta/{iaid}", timeout=timeout)

        if not data or not isinstance(data, dict):
            raise ValueError("Invalid API response format: expected a JSON object")

        if "delivery_option" not in data:
            raise ValueError("Invalid API response: missing required keys")

        return data

    except APIResourceNotFound:
        # 404 - no delivery options for this record, which is normal
        logger.info(f"No delivery options found for iaid {iaid}")
        return None

    except Exception as e:
        logger.error(f"DOAPI delivery options request error: {e!s}")
        raise Exception("DOAPI delivery options service is currently unavailable")
