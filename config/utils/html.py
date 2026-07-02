"""
Utilities for transforming and normalising HTML markup.

These helpers operate on HTML content and are independent of application-specific business rules.
"""

import re

from app.records.utils import change_discovery_record_details_links


def tna_html(s):
    """
    Transforms HTML into TNA-compatible frontend markup.
    """
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
