import re

# Matches a <mark> opening or closing tag (case-insensitive). The capturing
# group makes re.split keep the tags as their own tokens.
_MARK_TAG_RE = re.compile(r"(</?mark\b[^>]*>)", re.IGNORECASE)
# Matches any HTML tag; used to strip non-<mark> markup from visible text.
_HTML_TAG_RE = re.compile(r"<[^>]+>")

_CLOSE_MARK = "</mark>"
_ELLIPSIS = "…"


def _render_mark_tag(tag, open_marks, remaining):
    """Decide how to emit a <mark> open/close token.

    Returns (rendered, open_marks). A closing tag is only emitted when one is
    actually open; an opening tag is dropped once the budget is spent.
    """
    if tag.startswith("</"):
        if open_marks:
            return _CLOSE_MARK, open_marks - 1
        return "", open_marks
    if remaining > 0:
        return tag, open_marks + 1
    return "", open_marks


def _render_text(token, remaining):
    """Emit visible text, stripping non-<mark> markup and honouring the budget.

    Returns (rendered, remaining, hit_limit). Spending the budget exactly
    counts as hitting the limit, so an ellipsis follows.
    """
    text = _HTML_TAG_RE.sub("", token)
    if not text:
        return "", remaining, False
    if len(text) >= remaining:
        return text[:remaining], 0, True
    return text, remaining - len(text), False


def _truncate_tokens(value, max_length):
    """Walk the <mark>/text tokens of `value`, building the truncated result."""
    parts = []
    remaining = max_length
    open_marks = 0
    truncated = False

    for token in _MARK_TAG_RE.split(value):
        if not token:
            continue
        if _MARK_TAG_RE.fullmatch(token):
            rendered, open_marks = _render_mark_tag(token, open_marks, remaining)
            parts.append(rendered)
        else:
            rendered, remaining, truncated = _render_text(token, remaining)
            parts.append(rendered)
            if truncated:
                break

    parts.extend([_CLOSE_MARK] * open_marks)
    if truncated:
        parts.append(_ELLIPSIS)
    return "".join(parts)


def truncate_preserve_mark_tags(value, max_length=250):
    """Truncate text to `max_length` visible characters.

    - Keeps only <mark> tags (with their attributes) and strips all other HTML.
    - Counts only visible characters; tags do not count towards the limit.
    - Auto-closes any <mark> left open at the truncation point.
    - Appends an ellipsis (…) when the text is shortened.
    """
    if value is None:
        return ""
    try:
        max_length = int(max_length)
    except (TypeError, ValueError):
        return value
    if max_length <= 0 or not value:
        return ""
    return _truncate_tokens(value, max_length)
