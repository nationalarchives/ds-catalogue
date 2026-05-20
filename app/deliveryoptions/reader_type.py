import logging
from ipaddress import ip_address, ip_network
from typing import List, Optional

from django.conf import settings
from django.http import HttpRequest

from app.deliveryoptions.constants import Reader

logger = logging.getLogger(__name__)


def is_onsite(visitor_ip_address: str) -> bool:
    """
    Check if a visitor's IP address is within the on-site IP ranges.

    Args:
        visitor_ip_address: The visitor's IP address

    Returns:
        True if the visitor is on-site, False otherwise
    """
    return is_ip_in_cidr(visitor_ip_address, settings.ONSITE_IP_ADDRESSES)


def is_subscribed() -> bool:
    """
    Check if the user has a subscription.

    Returns:
        True if the user has a subscription, False otherwise

    TODO: once user management is in place
    """
    return False


def is_staff(visitor_ip_address: str) -> bool:
    """
    Check if a visitor's IP address is within the staff IP ranges.

    Args:
        visitor_ip_address: The visitor's IP address

    Returns:
        True if the visitor is staff, False otherwise
    """
    return is_ip_in_cidr(visitor_ip_address, settings.STAFFIN_IP_ADDRESSES)


def get_reader_type(request: HttpRequest) -> Reader:
    """
    Determine the reader type based on request information.

    Args:
        request: The HTTP request

    Returns:
        The determined reader type
    """
    reader = Reader.UNDEFINED

    try:
        visitor_ip_address = get_client_ip(request)
    except Exception as e:
        logger.warning(
            f"Cannot determine the users ip address - returning OFFSITE ({type(e)}: {e.args})"
        )
        return Reader.OFFSITE

    if reader == Reader.UNDEFINED:
        if is_subscribed():
            reader = Reader.SUBSCRIPTION
        elif is_onsite(visitor_ip_address):
            reader = Reader.ONSITEPUBLIC
        elif is_staff(visitor_ip_address):
            reader = Reader.STAFFIN
        else:
            reader = Reader.OFFSITE

    return reader


def get_client_ip(request: HttpRequest) -> Optional[str]:
    """
    Extract the client IP address from the HTTP request.

    This function properly handles IP address extraction by:
    1. Only trusting X-Forwarded-For headers when they come from trusted proxies
    2. Validating IP addresses for proper format
    3. Handling multiple proxy hops correctly

    The function will use REMOTE_ADDR by default unless the request comes from
    a trusted proxy (defined in settings.TRUSTED_PROXIES), in which case it will
    use the leftmost non-trusted-proxy IP in the X-Forwarded-For chain.s

    Args:
        request: The Django HTTP request object

    Returns:
        The client's IP address, or None if it couldn't be determined or was invalid

    Example:
        ip = get_client_ip(request)
        if ip:
            # Process valid IP
        else:
            # Handle missing/invalid IP

    Note:
        Configure TRUSTED_PROXIES in Django settings to specify which IP
        addresses are allowed to set X-Forwarded-For headers.

    TODO: This is most probably going to be redundant when the code goes to AWS and an alternative will be provided
    """
    # Define trusted proxies
    TRUSTED_PROXIES = getattr(settings, "TRUSTED_PROXIES", [])

    # Get the immediate client IP
    remote_addr = request.META.get("REMOTE_ADDR")

    # Check if we have X-Forwarded-For header
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    # If no X-Forwarded-For or remote_addr isn't a trusted proxy, use remote_addr
    if not forwarded_for or remote_addr not in TRUSTED_PROXIES:
        return validate_ip(remote_addr)

    # Process X-Forwarded-For from trusted proxy
    # Format: client, proxy1, proxy2, ...
    forwarded_ips = [ip.strip() for ip in forwarded_for.split(",")]

    # Return the leftmost IP that isn't a trusted proxy
    for ip in forwarded_ips:
        if ip not in TRUSTED_PROXIES:
            return validate_ip(ip)

    # If all IPs in the chain are trusted, use the leftmost one
    # fmt: off
    return (
        validate_ip(forwarded_ips[0])
        if forwarded_ips
        else validate_ip(remote_addr)
    )
    # fmt: on


def validate_ip(ip_str: str) -> Optional[str]:
    """
    Validate that the string is a proper IP address.

    Args:
        ip_str: String representation of an IP address

    Returns:
        Valid IP address string or None if invalid
    """
    if not ip_str:
        return None

    try:
        # This will raise ValueError for invalid IPs
        ip = ip_address(ip_str)
        return str(ip)
    except ValueError:
        return None


def is_ip_in_cidr(ip: str, cidr: List[str]) -> bool:
    """
    Check if an IP address is within any of the specified CIDR ranges.
    Args:
        ip : The IP address to check
        cidr: A list of strings containing CIDR ranges
    Returns:
        True if the IP is within any of the specified ranges, False otherwise
    Raises:
        ValueError: If the IP address or CIDR range is invalid
    """
    try:
        # Parse the IP address
        ip_obj = ip_address(ip)

        # Parse each CIDR range
        for cidr_range in cidr:
            network = ip_network(cidr_range.strip(), strict=False)
            if ip_obj in network:
                return True
        # If no match is found
        return False
    except ValueError as e:
        raise ValueError(f"Invalid IP or CIDR: {e}")
