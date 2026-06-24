import re


def none_to_empty_string(value):
    """Convert None to empty string for Jinja2 templates."""

    if value is None:
        return ""
    return value


def remove_string_case_insensitive(value: str, to_remove: str):
    if not value or not to_remove:
        return value
    pattern = re.compile(re.escape(to_remove), re.IGNORECASE)
    return pattern.sub("", value)
