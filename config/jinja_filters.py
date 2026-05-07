"""
Filter and global function implementations for the Jinja2 environment.

These are registered into the environment in `config/jinja.py`. Keep this
module focused on the function bodies; environment wiring belongs there.
"""

import base64
import json
import re
from datetime import datetime
from urllib.parse import unquote

from app.lib.constants import DATE_YMD_SEPARATOR
from app.lib.fields import DateKeys
from app.records.utils import change_discovery_record_details_links
from app.search.constants import FieldsConstant
from django.http import QueryDict

# ---------------------------------------------------------------------------
# Text and HTML
# ---------------------------------------------------------------------------


def slugify(s):
    s = s.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_-]+", "-", s)
    s = re.sub(r"^-+|-+$", "", s)
    return s


def sanitise_record_field(s):
    # Remove whitespace between <p> tags
    s = re.sub(r"(</p>)\s+(<p[ >])", r"\1\2", s).strip()
    s = change_discovery_record_details_links(s)
    return s


def tna_html(s):
    if not s:
        return s
    # lists_to_tna_lists
    s = s.replace("<ul>", '<ul class="tna-ul">')
    # s = re.sub(r'<ul( class="([^"]*)")?>', r'<ul class="tna-ul \g<2>">', s)
    s = s.replace("<ol>", '<ol class="tna-ol">')
    # b_to_strong
    s = s.replace("<b>", "<strong>")
    s = s.replace("<b ", "<strong ")
    s = s.replace("</b>", "</strong>")
    # strip_wagtail_attributes
    s = re.sub(r' data-block-key="([^"]*)"', "", s)
    # replace_line_breaks
    s = s.replace("\r\n", "<br>")
    # add_rel_to_external_links
    s = re.sub(
        r'<a href="(?!https:\/\/(www|discovery|webarchive)\.nationalarchives\.gov\.uk\/)',
        '<a rel="noreferrer nofollow noopener" href="',
        s,
    )
    return s


def remove_string_case_insensitive(value: str, to_remove: str):
    if not value or not to_remove:
        return value
    pattern = re.compile(re.escape(to_remove), re.IGNORECASE)
    return pattern.sub("", value)


def none_to_empty_string(value):
    """Convert None to empty string for Jinja2 templates."""
    if value is None:
        return ""
    return value


# ---------------------------------------------------------------------------
# truncate_preserve_mark_tags and its private helpers
# ---------------------------------------------------------------------------

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
        return visible, False

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
            visible, truncated = _consume_text(
                token, output, visible, max_length
            )
            if visible >= max_length:
                truncated = True

    output.extend(["</mark>"] * open_marks)
    if truncated:
        output.append("…")

    return "".join(output)


# ---------------------------------------------------------------------------
# Encoding and JSON
# ---------------------------------------------------------------------------


def parse_json(s):
    try:
        unquoted_string = unquote(s)
        return json.loads(unquoted_string)
    except Exception:
        return {}


def dump_json(obj):
    return json.dumps(obj, indent=2)


def base64_encode(s):
    s = bytes(s, "utf-8")
    s = base64.urlsafe_b64encode(s)
    return s.decode("utf-8", "ignore")


def base64_decode(s):
    if not s:
        return ""
    try:
        raw = s.encode("utf-8")
        padding = (-len(raw)) % 4
        if padding:
            raw += b"=" * padding
        decoded = base64.urlsafe_b64decode(raw)
    except Exception:
        return ""
    return decoded.decode("utf-8", "ignore")


# ---------------------------------------------------------------------------
# Search query string sanitisation
# ---------------------------------------------------------------------------


def _allowed_search_qs_keys() -> set[str]:
    date_fields = {
        FieldsConstant.COVERING_DATE_FROM,
        FieldsConstant.COVERING_DATE_TO,
        FieldsConstant.OPENING_DATE_FROM,
        FieldsConstant.OPENING_DATE_TO,
    }
    allowed = {
        FieldsConstant.Q,
        FieldsConstant.GROUP,
        FieldsConstant.SORT,
        FieldsConstant.DISPLAY,
        FieldsConstant.FILTER_LIST,
        FieldsConstant.LEVEL,
        FieldsConstant.COLLECTION,
        FieldsConstant.SUBJECT,
        FieldsConstant.ONLINE,
        FieldsConstant.CLOSURE,
        FieldsConstant.HELD_BY,
        "page",
    }
    for field in date_fields:
        allowed.add(field)
        for date_key in DateKeys:
            allowed.add(f"{field}{DATE_YMD_SEPARATOR}{date_key.value}")
    return allowed


def sanitize_search_qs(encoded: str) -> str:
    """Decode a base64 search query and rebuild a safe, allowlisted query string."""

    decoded = base64_decode(encoded)
    if not decoded:
        return ""

    qs = QueryDict(decoded, mutable=False)
    if not qs:
        return ""

    allowed = _allowed_search_qs_keys()
    cleaned = QueryDict(mutable=True)
    for key in allowed:
        values = [value for value in qs.getlist(key) if value != ""]
        if values:
            cleaned.setlist(key, values)

    return cleaned.urlencode()


# ---------------------------------------------------------------------------
# Dates and numbers
# ---------------------------------------------------------------------------


def now_iso_8601():
    now = datetime.now()
    now_date = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    return now_date


def now_iso_8601_date():
    now = datetime.now()
    now_date = now.strftime("%Y-%m-%d")
    return now_date


def format_number(num):
    try:
        number = int(num)
    except ValueError:
        return num
    return format(number, ",")


# ---------------------------------------------------------------------------
# Query string helpers (used as Jinja globals)
# ---------------------------------------------------------------------------


def qs_is_value_active(existing_qs: QueryDict, filter: str, by: str):
    """Active when identical key/value in existing query string."""
    qs_set = {(filter, str(by))}
    # Not active if either are empty.
    if not existing_qs or not qs_set:
        return False
    # Test for identical key and value in existing query string.
    return str(by) in existing_qs.getlist(filter)


def qs_toggle_value(
    existing_qs: QueryDict, filter: str, by: str, return_object: bool = False
):
    """Resolve filter against an existing query string."""
    # Don't change the currently rendering existing query string!
    rtn_qs = existing_qs.copy()
    # Test for identical key and value in existing query string.
    if qs_is_value_active(existing_qs, filter, by):
        # Create a copy of the list.
        new_list = rtn_qs.getlist(filter).copy()
        # Remove the value from the list.
        new_list.remove(str(by))
        # If the list is not empty, update the query string with the new list.
        if len(new_list):
            rtn_qs.setlist(filter, new_list)
        else:
            rtn_qs.pop(filter)
    else:
        # Add the key/value pair to the query string.
        qs = {filter: by}
        # Update the query string with the new key/value pair.
        rtn_qs.update(qs)
    # Return the query string as a QueryDict object or as a URL encoded string.
    return rtn_qs if return_object else rtn_qs.urlencode()


def qs_replace_value(
    existing_qs: QueryDict, filter: str, by: str, return_object: bool = False
):
    # Don't change the currently rendering existing query string!
    rtn_qs = existing_qs.copy()
    rtn_qs[filter] = by
    return rtn_qs if return_object else rtn_qs.urlencode()


def qs_append_value(
    existing_qs: QueryDict, filter: str, by: str, return_object: bool = False
):
    # Don't change the currently rendering existing query string!
    rtn_qs = existing_qs.copy()
    if filter and not qs_is_value_active(existing_qs, filter, by):
        qs = {filter: by}
        rtn_qs.update(qs)
    return rtn_qs if return_object else rtn_qs.urlencode()


def qs_remove_value(
    existing_qs: QueryDict, filter: str, return_object: bool = False
):
    # Don't change the currently rendering existing query string!
    rtn_qs = existing_qs.copy()
    if filter in rtn_qs:
        rtn_qs.pop(filter)
    return rtn_qs if return_object else rtn_qs.urlencode()


# ---------------------------------------------------------------------------
# Record-specific
# ---------------------------------------------------------------------------


def override_tna_record_count(value, record):
    """
    Override the record count for records that are held by The National Archives.
    """
    if record.is_tna:
        return "Over 27 million"

    return value
