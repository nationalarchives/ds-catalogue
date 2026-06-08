"""
Query string helper utilities.

Used as both Jinja2 globals and standalone helpers. All functions treat the
incoming QueryDict as immutable — mutations are performed on a copy.
"""

from django.http import QueryDict

from app.lib.constants import DATE_YMD_SEPARATOR
from app.lib.fields import DateKeys
from app.search.constants import FieldsConstant

from config.utils.encoding import base64_decode


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


def sanitise_search_qs(encoded: str) -> str:
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
        values = [v for v in qs.getlist(key) if v != ""]
        if values:
            cleaned.setlist(key, values)

    return cleaned.urlencode()


def qs_is_value_active(existing_qs: QueryDict, filter: str, by: str) -> bool:
    """Active when identical key/value pair exists in the query string."""
    if not existing_qs or not filter:
        return False
    return str(by) in existing_qs.getlist(filter)


def qs_toggle_value(
    existing_qs: QueryDict, filter: str, by: str, return_object: bool = False
):
    """Add or remove a key/value pair from the query string."""
    rtn_qs = existing_qs.copy()
    if qs_is_value_active(existing_qs, filter, by):
        new_list = rtn_qs.getlist(filter).copy()
        new_list.remove(str(by))
        if new_list:
            rtn_qs.setlist(filter, new_list)
        else:
            rtn_qs.pop(filter)
    else:
        rtn_qs.update({filter: by})
    return rtn_qs if return_object else rtn_qs.urlencode()


def qs_replace_value(
    existing_qs: QueryDict, filter: str, by: str, return_object: bool = False
):
    """Replace all values for a key with a single new value."""
    rtn_qs = existing_qs.copy()
    rtn_qs[filter] = by
    return rtn_qs if return_object else rtn_qs.urlencode()


def qs_append_value(
    existing_qs: QueryDict, filter: str, by: str, return_object: bool = False
):
    """Append a value to a key if it is not already present."""
    rtn_qs = existing_qs.copy()
    if filter and not qs_is_value_active(existing_qs, filter, by):
        rtn_qs.update({filter: by})
    return rtn_qs if return_object else rtn_qs.urlencode()


def qs_remove_value(
    existing_qs: QueryDict, filter: str, return_object: bool = False
):
    """Remove all values for a key from the query string."""
    rtn_qs = existing_qs.copy()
    if filter in rtn_qs:
        rtn_qs.pop(filter)
    return rtn_qs if return_object else rtn_qs.urlencode()
