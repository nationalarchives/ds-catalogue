from datetime import UTC, datetime


def now_iso_8601():
    """Current UTC time as an ISO 8601 string, e.g. 2026-06-23T17:25:56Z.

    Uses an aware UTC datetime so the trailing 'Z' (the UTC designator) is
    accurate regardless of the server's local timezone.
    """
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def now_iso_8601_date():
    """Current UTC date as an ISO 8601 string, e.g. 2026-06-23."""
    return datetime.now(UTC).strftime("%Y-%m-%d")
