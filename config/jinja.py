"""
Jinja2 environment factory for the application.

Filter and global function implementations live in `config.jinja_filters`;
this module only handles environment construction and registration.
"""

import json

from app.lib.xslt_transformations import apply_generic_xsl
from config.jinja_filters import (
    base64_decode,
    base64_encode,
    dump_json,
    format_number,
    none_to_empty_string,
    now_iso_8601,
    now_iso_8601_date,
    override_tna_record_count,
    parse_json,
    qs_append_value,
    qs_is_value_active,
    qs_remove_value,
    qs_replace_value,
    qs_toggle_value,
    remove_string_case_insensitive,
    sanitise_record_field,
    sanitize_search_qs,
    slugify,
    tna_html,
    truncate_preserve_mark_tags,
)
from django.conf import settings
from django.templatetags.static import static
from django.urls import reverse
from jinja2 import Environment


def _read_tna_frontend_version() -> str:
    """Read the TNA frontend package version, returning '' on any failure."""
    try:
        with open(
            "/app/node_modules/@nationalarchives/frontend/package.json",
        ) as package_json:
            try:
                data = json.load(package_json)
                return data["version"] or ""
            except ValueError:
                # Invalid JSON in package.json for TNA frontend; skipping version setting.
                return ""
    except FileNotFoundError:
        # package.json for TNA frontend not found; skipping version setting.
        return ""


def environment(**options):
    env = Environment(**options)

    env.globals.update(
        {
            "static": static,
            "app_config": {
                "GA4_ID": settings.GA4_ID,
                "CONTAINER_IMAGE": settings.CONTAINER_IMAGE,
                "BUILD_VERSION": settings.BUILD_VERSION,
                "TNA_FRONTEND_VERSION": _read_tna_frontend_version(),
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
            "sanitize_search_qs": sanitize_search_qs,
            "sanitise_record_field": sanitise_record_field,
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
