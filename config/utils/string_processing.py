"""
String and HTML transformation utilities.

Pure-Python helpers with no Jinja2 dependency. Registered as filters in
`config/jinja.py` but usable independently.
"""

import re

from app.records.utils import change_discovery_record_details_links


def normalise_record_field(s):
    # Remove whitespace between <p> tags
    s = re.sub(r"(</p>)\s+(<p[ >])", r"\1\2", s).strip()
    s = change_discovery_record_details_links(s)
    return s


def tna_html(s):
    """
    Transforms HTML into TNA-compatible frontend markup.
    """
    if not s:
        return s
    # lists_to_tna_lists
    s = s.replace("<ul>", '<ul class="tna-ul">')
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
