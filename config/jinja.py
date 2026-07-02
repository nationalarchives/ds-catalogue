import json
import re

from django.conf import settings
from django.http import QueryDict
from django.templatetags.static import static
from django.urls import reverse
from jinja2 import Environment
from tna_utilities.string import slugify

from app.lib.xslt_transformations import apply_generic_xsl
from app.records.utils import change_discovery_record_details_links
from config.utils.date_iso8601 import now_iso_8601, now_iso_8601_date
from config.utils.encoding import base64_decode, base64_encode
from config.utils.html import tna_html
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
from config.utils.records import normalise_record_field, override_tna_record_count
from config.utils.string_processing import (
    none_to_empty_string,
    remove_string_case_insensitive,
)


def environment(**options):
    env = Environment(**options)

    TNA_FRONTEND_VERSION = ""
    try:
        with open(
            "/app/node_modules/@nationalarchives/frontend/package.json",
        ) as package_json:
            try:
                data = json.load(package_json)
                TNA_FRONTEND_VERSION = data["version"] or ""
            except ValueError:
                # Invalid JSON in package.json for TNA frontend; skipping version setting.
                pass
    except FileNotFoundError:
        # package.json for TNA frontend not found; skipping version setting.
        pass

    env.globals.update(
        {
            "static": static,
            "app_config": {
                "GA4_ID": settings.GA4_ID,
                "CONTAINER_IMAGE": settings.CONTAINER_IMAGE,
                "BUILD_VERSION": settings.BUILD_VERSION,
                "TNA_FRONTEND_VERSION": TNA_FRONTEND_VERSION,
                "COOKIE_DOMAIN": settings.COOKIE_DOMAIN,
            },
            "feature": {"PHASE_BANNER": settings.FEATURE_PHASE_BANNER},
            "url": reverse,
            "now_iso_8601": now_iso_8601,
            "now_iso_8601_date": now_iso_8601_date,
            "qs_append_value": qs_append_value,
            "qs_is_value_active": qs_is_value_active,
            "qs_remove_value": qs_remove_value,
            "qs_replace_value": qs_replace_value,
            "qs_toggle_value": qs_toggle_value,
        }
    )
    env.filters.update(
        {
            "slugify": slugify,
            "dump_json": dump_json,
            "format_number": format_number,
            "base64_encode": base64_encode,
            "base64_decode": base64_decode,
            "sanitise_search_qs": sanitise_search_qs,
            "normalise_record_field": normalise_record_field,
            "apply_generic_xsl": apply_generic_xsl,
            "parse_json": parse_json,
            "tna_html": tna_html,
            "remove_string_case_insensitive": remove_string_case_insensitive,
            "truncate_preserve_mark_tags": truncate_preserve_mark_tags,
            "override_tna_record_count": override_tna_record_count,
            "none_to_empty_string": none_to_empty_string,
        }
    )
    return env
