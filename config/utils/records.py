"""Utilities for formatting and transforming record data."""

import re

from app.records.utils import change_discovery_record_details_links


def override_tna_record_count(value, record):
    """
    Override the record count for records that are held by The National Archives.
    """
    if record.is_tna:
        return "Over 27 million"

    return value


def normalise_record_field(s):
    """
    Normalise a record field string by removing unnecessary HTML whitespace
    and rewriting legacy discovery record links.
    """
    # Remove whitespace between <p> tags
    s = re.sub(r"(</p>)\s+(<p[ >])", r"\1\2", s).strip()
    s = change_discovery_record_details_links(s)
    return s
