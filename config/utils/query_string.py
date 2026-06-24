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


def qs_remove_value(existing_qs: QueryDict, filter: str, return_object: bool = False):
    # Don't change the currently rendering existing query string!
    rtn_qs = existing_qs.copy()
    if filter in rtn_qs:
        rtn_qs.pop(filter)
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
        values = [value for value in qs.getlist(key) if value != ""]
        if values:
            cleaned.setlist(key, values)

    return cleaned.urlencode()
