"""
Filter and global function implementations for the Jinja2 environment.

These are registered into the environment in `config/jinja.py`. Keep this
module focused on environment wiring; function implementations live in
`config/utils/`.

Note: `override_tna_record_count` remains here pending confirmation that
moving it to `config/utils/records.py` won't introduce a circular import
via `app.records`.
"""

from config.utils.date import now_iso_8601, now_iso_8601_date
from config.utils.encoding import base64_decode, base64_encode
from config.utils.json_utils import dump_json, parse_json
from config.utils.markup_truncation import truncate_preserve_mark_tags
from config.utils.number import format_number
from config.utils.query_string import (
    qs_append_value,
    qs_is_value_active,
    qs_remove_value,
    qs_replace_value,
    qs_toggle_value,
    sanitise_search_qs,
)
from config.utils.string_processing import (
    none_to_empty_string,
    normalise_record_field,
    remove_string_case_insensitive,
    tna_html,
)


def override_tna_record_count(value, record):
    """
    Override the record count for records held by The National Archives.

    TODO: move to config/utils/records.py once circular import risk via
    app.records has been confirmed safe.
    """
    if record.is_tna:
        return "Over 27 million"
    return value


__all__ = [
    "base64_decode",
    "base64_encode",
    "dump_json",
    "format_number",
    "none_to_empty_string",
    "normalise_record_field",
    "now_iso_8601",
    "now_iso_8601_date",
    "override_tna_record_count",
    "parse_json",
    "qs_append_value",
    "qs_is_value_active",
    "qs_remove_value",
    "qs_replace_value",
    "qs_toggle_value",
    "remove_string_case_insensitive",
    "sanitise_search_qs",
    "tna_html",
    "truncate_preserve_mark_tags",
]
