import logging
from typing import Any
from urllib.parse import quote

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from app.lib.api import JSONAPIClient
from app.lib.exceptions import APIResourceNotFound

logger = logging.getLogger(__name__)


def delivery_options_request_handler(
    iaid: str,
    timeout: int = None,
) -> dict[str, Any] | None:
    """
    Makes an API call to the delivery options service (DOAPI) to fetch the
    delivery options for a given iaid.

    Returns DOAPI's JSON exactly as received — no reshaping. It is passed
    straight through to the templates as `delivery_options`. The fields
    are: "delivery_option" (the condition number), "delivery_option_name",
    "group" (the availability group), "label" (display text), "flags" (a
    dict of booleans), "surrogate_links", "advanced_order_url_parameters"
    ({"url_params": ...} or null) and "reader_type".

    No reader type is sent. DOAPI works that out itself (currently it
    treats every request as OffSite) and reports the one it used in the
    response's "reader_type".

    Args:
        iaid: The item archive ID to retrieve delivery options for
        timeout: Request timeout in seconds

    Returns:
        DOAPI's response as a dict, or None if the service has no
        delivery options for this record (404)

    Raises:
        ImproperlyConfigured: If DELIVERY_OPTIONS_API_URL or
            DELIVERY_OPTIONS_API_KEY is not configured
        Exception: If the delivery options service is unavailable or
            returns invalid data. JSONAPIClient.get() only treats
            400/403/404 specially, so DOAPI's 401 (bad key), 422
            (unsupported catalogue level), 429 (rate limited) and 503
            (its own upstreams down) all arrive here as the same generic
            failure and can't be told apart from this function.
    """
    api_url = settings.DELIVERY_OPTIONS_API_URL

    if not api_url:
        raise ImproperlyConfigured("DELIVERY_OPTIONS_API_URL not set")

    api_key = settings.DELIVERY_OPTIONS_API_KEY

    if not api_key:
        raise ImproperlyConfigured("DELIVERY_OPTIONS_API_KEY not set")

    try:
        # DELIVERY_OPTIONS_API_URL is the DOAPI base, including its version
        # prefix (e.g. http://host/api/v1). rstrip so a trailing slash in
        # the setting can't produce a double slash, which DOAPI 404s on.
        client = JSONAPIClient(api_url.rstrip("/"))
        client.add_header("X-API-Key", api_key)

        data = client.get(
            f"delivery-options/rosetta/{quote(iaid, safe='')}", timeout=timeout
        )

        if not data or not isinstance(data, dict):
            raise ValueError("Invalid API response format: expected a JSON object")

        if "delivery_option" not in data:
            raise ValueError("Invalid API response: missing required keys")

        return data

    except APIResourceNotFound:
        # 404 - this record doesn't have delivery options, which is normal
        logger.info(f"No delivery options found for iaid {iaid}")
        return None

    except Exception as e:
        # Log the original exception for debugging
        logger.error(f"Delivery options request error: {e!s}")
        raise Exception("Delivery Options database is currently unavailable")
