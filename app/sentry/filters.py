import asyncio

from sentry_sdk.types import Event, Hint

DELIVERY_OPTIONS_ERRORS = (
    "Delivery Options database is currently unavailable",
    "Delivery options request error: Resource not found",
    "Delivery options request error: The request timed out",
    "Delivery options request error: Request failed",
    "Delivery options request error: A connection error occured",
)


def should_ignore_exception(hint: Hint) -> bool:
    """ASGI can raise CancelledError when a request is cancelled.
    Ignore expected asyncio cancellation noise from Sentry."""

    exc_info = hint.get("exc_info")

    if not exc_info:
        return False

    return exc_info[0] is asyncio.CancelledError


def should_ignore_delivery_options(hint: Hint) -> bool:
    """Ignore known, handled Delivery Options failures from Sentry."""

    exc_info = hint.get("exc_info")

    if not exc_info:
        return False

    exc_value = exc_info[1]

    if exc_value is None:
        return False

    message = str(exc_value)

    return any(error in message for error in DELIVERY_OPTIONS_ERRORS)


def before_send(event: Event, hint: Hint) -> Event | None:
    """Filter out known, non-critical exceptions before sending to Sentry."""
    
    if should_ignore_exception(hint):
        return None

    if should_ignore_delivery_options(hint):
        return None

    return event
