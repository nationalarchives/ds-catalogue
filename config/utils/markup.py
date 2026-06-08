"""
Truncation utility that preserves <mark> tags.

Strips all non-mark HTML, counts visible characters, auto-closes open mark
tags on truncation, and appends an ellipsis where content was cut.
"""

import re

_MARK_TAG_RE = re.compile(r"(</?mark\b[^>]*>)", re.IGNORECASE)
_NON_MARK_HTML_RE = re.compile(r"<[^>]+>")


def _coerce_max_length(max_length):
    """Return max_length as an int, or None if it can't be coerced."""
    try:
        return int(max_length)
    except (TypeError, ValueError):
        return None


def _is_mark_tag(token):
    return bool(_MARK_TAG_RE.fullmatch(token))


def _strip_non_mark_html(token):
    return _NON_MARK_HTML_RE.sub("", token)


def _consume_mark_tag(token, output, open_marks, visible, max_length):
    """
    Handle a <mark> opening or closing tag.
    Returns the updated open_marks count.
    """
    if token.startswith("</"):
        if open_marks:
            output.append("</mark>")
            return open_marks - 1
        return open_marks
    if visible < max_length:
        output.append(token)
        return open_marks + 1
    return open_marks


def _consume_text(token, output, visible, max_length):
    """
    Append as much of the token's visible text as fits.
    Returns (new_visible_count, truncated_flag).
    """
    text = _strip_non_mark_html(token)
    if not text:
        return visible, False

    remaining = max_length - visible
    if remaining <= 0:
        return visible, True

    if len(text) <= remaining:
        output.append(text)
        return visible + len(text), False

    output.append(text[:remaining])
    return max_length, True


def truncate_preserve_mark_tags(value, max_length=250):
    """
    Truncate text to `max_length` visible characters while:
    - Keeping only <mark> tags (with their attributes) and stripping all other HTML.
    - Counting only visible characters (HTML tags do not count).
    - Auto-closing any still-open <mark> tags on truncation.
    - Appending an ellipsis (…) if truncation occurs.
    """
    if value is None:
        return ""

    max_length = _coerce_max_length(max_length)
    if max_length is None:
        return value
    if max_length <= 0 or value == "":
        return ""

    output = []
    visible = 0
    open_marks = 0
    truncated = False

    for token in _MARK_TAG_RE.split(value):
        if truncated:
            break
        if _is_mark_tag(token):
            open_marks = _consume_mark_tag(
                token, output, open_marks, visible, max_length
            )
        else:
            visible, truncated = _consume_text(token, output, visible, max_length)

    output.extend(["</mark>"] * open_marks)
    if truncated:
        output.append("…")

    return "".join(output)
