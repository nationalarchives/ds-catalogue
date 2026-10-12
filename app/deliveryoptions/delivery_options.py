"""
Distressing-content check for records.

This module used to build delivery options markup from the previous
delivery options service's response. That is gone: DOAPI's JSON is now
passed straight to the templates. What remains has nothing to do with
delivery options and would sit better elsewhere (e.g. alongside the records
code) — it is only here because it always has been.
"""

from functools import lru_cache

from django.conf import settings


@lru_cache(maxsize=1)
def _get_dcs_prefix_variants():
    """Build and cache exact and slash variants of all prefixes."""
    variants = set()
    for prefix in settings.DCS_PREFIXES:
        variants.add(prefix)  # Exact match
        variants.add(f"{prefix}/")  # With slash
    return variants


def has_distressing_content(reference: str) -> bool:
    """
    Check if a reference number matches any of the distressing content prefixes.

    Args:
        reference: The reference number to check

    Returns:
        True if the reference number starts with any distressing content prefix
    """
    variants = _get_dcs_prefix_variants()

    # Check exact match first (fastest)
    if reference in variants:
        return True

    # Check if starts with any slash variant
    for variant in variants:
        if variant.endswith("/") and reference.startswith(variant):
            return True

    return False
