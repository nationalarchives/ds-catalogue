import logging
import os

logger = logging.getLogger(__name__)


def strtobool(val):
    """Convert a string representation of truth to true (1) or false (0).
    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return True
    elif val in ("n", "no", "f", "false", "off", "0"):
        return False
    else:
        raise ValueError("invalid truth value %r" % (val,))


def get_int_env(key: str, default: int) -> int:
    """
    Get an integer environment variable with fallback to default.

    Handles empty strings, whitespace, zero values, and invalid input.

    Args:
        key: Environment variable name
        default: Default value if not set or invalid (default: 5)

    Returns:
        Integer value, or default if invalid
    """
    try:
        value = os.getenv(key, str(default)).strip()
        if not value:  # Empty string after strip
            return default
        result = int(value)
        # Prevent zero timeout (dangerous - infinite wait)
        return result if result > 0 else default
    except (ValueError, AttributeError):
        logger.warning(f"Invalid value for {key}, using default: {default}")
        return default


def get_bool_env(key: str, default: bool) -> bool:
    """
    Get a boolean environment variable with fallback to default.

    Args:
        key: Environment variable name
        default: Default value if not set or invalid

    Returns:
        Boolean value, or default if invalid
    """
    try:
        value = os.getenv(key, str(default)).strip()
        if not value:
            return default
        return strtobool(value) == 1
    except (ValueError, AttributeError):
        logger.warning(f"Invalid value for {key}, using default: {default}")
        return default
