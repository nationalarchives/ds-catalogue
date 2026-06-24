import re

from app.records.utils import change_discovery_record_details_links


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


def override_tna_record_count(value, record):
    """
    Override the record count for records that are held by The National Archives.
    """
    if record.is_tna:
        return "Over 27 million"

    return value
