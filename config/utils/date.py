"""
Date and datetime formatting utilities.
"""

from datetime import datetime, timezone


def now_iso_8601() -> str:
    """Return the current UTC time as an ISO 8601 string with a Z suffix."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def now_iso_8601_date() -> str:
    """Return the current UTC date as a YYYY-MM-DD string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")
