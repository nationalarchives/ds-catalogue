"""
API views for progressive loading of record detail components.

These endpoints are called via AJAX to load non-critical content
after the initial page render.
"""

import logging
import time

from app.deliveryoptions.api import delivery_options_request_handler
from app.deliveryoptions.constants import AvailabilityCondition
from app.deliveryoptions.delivery_options import get_availability_group
from app.deliveryoptions.helpers import BASE_TNA_DISCOVERY_URL
from app.records.api import get_subjects_enrichment
from app.records.models import Record
from app.records.related import (
    get_related_records_by_series,
    get_tna_related_records_by_subjects,
)
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)


@require_GET
def delivery_options_api(request, record_id):
    """
    API endpoint to fetch delivery options for progressive loading.

    Returns JSON with delivery options data including availability
    group and temporary display information.

    Args:
        request: Django request object
        record_id: The record IAID

    Returns:
        JsonResponse with delivery options data or error
    """
    try:
        from app.records.api import record_details_by_id

        # Get the record
        record = record_details_by_id(id=record_id)

        # Check if delivery options should be included
        from app.deliveryoptions.constants import (
            DELIVERY_OPTIONS_NON_TNA_LEVELS,
            DELIVERY_OPTIONS_TNA_LEVELS,
        )

        should_include = False
        if record.custom_record_type not in ["ARCHON", "CREATORS"]:
            if (
                record.is_tna
                and record.level_code in DELIVERY_OPTIONS_TNA_LEVELS
            ):
                should_include = True
            elif (
                not record.is_tna
                and record.level_code in DELIVERY_OPTIONS_NON_TNA_LEVELS
            ):
                should_include = True

        if not should_include:
            return JsonResponse(
                {
                    "success": True,
                    "has_delivery_options": False,
                }
            )

        # Fetch delivery options
        delivery_result = delivery_options_request_handler(record.iaid)

        if not isinstance(delivery_result, list) or not delivery_result:
            return JsonResponse(
                {
                    "success": True,
                    "has_delivery_options": False,
                }
            )

        first_result = delivery_result[0]
        delivery_option_value = first_result.get("options")

        if delivery_option_value is None:
            return JsonResponse(
                {
                    "success": True,
                    "has_delivery_options": False,
                }
            )

        # Convert to AvailabilityCondition enum
        try:
            delivery_option_enum = AvailabilityCondition(delivery_option_value)
            delivery_option_name = delivery_option_enum.name
        except ValueError:
            logger.warning(
                f"Unknown delivery option value {delivery_option_value} "
                f"for iaid {record.iaid}"
            )
            return JsonResponse(
                {
                    "success": True,
                    "has_delivery_options": False,
                }
            )

        # Get availability group
        do_availability_group = get_availability_group(delivery_option_value)
        do_availability_group_name = (
            do_availability_group.name if do_availability_group else None
        )

        # Build response
        response_data = {
            "success": True,
            "has_delivery_options": True,
            "delivery_option": delivery_option_name,
            "do_availability_group": do_availability_group_name,
            "delivery_options_heading": "How to order it",
            "delivery_instructions": [
                "View this record page in our current catalogue",
                "Check viewing and downloading options",
                "Select an option and follow instructions",
            ],
            "tna_discovery_link": f"{BASE_TNA_DISCOVERY_URL}/details/r/{record.iaid}",
        }

        return JsonResponse(response_data)

    except Exception as e:
        logger.error(f"Failed to fetch delivery options for {record_id}: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@require_GET
def related_records_api(request, record_id):
    """
    API endpoint to fetch related records for progressive loading.

    Returns JSON with related records data that can be rendered
    client-side.

    Args:
        request: Django request object
        record_id: The record IAID

    Returns:
        JsonResponse with related records data or error
    """
    try:
        from app.records.api import record_details_by_id

        # Get the record
        record = record_details_by_id(id=record_id)

        # Get related records limit from query param or use default
        limit = int(request.GET.get("limit", 3))

        # Fetch related records
        related_records = []

        # Try subjects first
        subjects_records = get_tna_related_records_by_subjects(
            record, limit=limit
        )
        related_records.extend(subjects_records)

        # Backfill with series records if needed
        if len(related_records) < limit:
            remaining = limit - len(related_records)
            series_records = get_related_records_by_series(
                record, limit=remaining
            )

            # Avoid duplicates
            existing_iaids = {r.iaid for r in related_records}
            for series_record in series_records:
                if series_record.iaid not in existing_iaids:
                    related_records.append(series_record)
                    if len(related_records) >= limit:
                        break

        # Serialize records to JSON-friendly format
        serialized_records = []
        for rel_record in related_records:
            serialized_records.append(
                {
                    "iaid": rel_record.iaid,
                    "level": rel_record.level,
                    "summary_title": rel_record.summary_title,
                    "reference_number": rel_record.reference_number,
                    "url": rel_record.url,
                    "date_covering": rel_record.date_covering,
                    "description": rel_record.clean_description
                    or rel_record.description,
                }
            )

        return JsonResponse(
            {
                "success": True,
                "count": len(serialized_records),
                "related_records": serialized_records,
            }
        )

    except Exception as e:
        logger.error(f"Failed to fetch related records for {record_id}: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@require_GET
def subjects_enrichment_api(request, record_id):
    """
    API endpoint to fetch subjects enrichment for progressive loading.

    Returns pre-rendered HTML to maintain design system consistency.

    Args:
        request: Django request object
        record_id: The record IAID

    Returns:
        JsonResponse with HTML string or error
    """
    try:
        from app.records.api import record_details_by_id
        from django.template.loader import render_to_string

        # Get the record
        record = record_details_by_id(id=record_id)

        # Check if record has subjects
        if not record.subjects:
            return JsonResponse(
                {"success": True, "has_enrichment": False, "html": ""}
            )

        # Fetch subjects enrichment
        limit = int(request.GET.get("limit", settings.MAX_SUBJECTS_PER_RECORD))
        enrichment_data = get_subjects_enrichment(record.subjects, limit=limit)

        # Handle list vs dict format
        if isinstance(enrichment_data, list):
            items = enrichment_data
        elif isinstance(enrichment_data, dict):
            items = enrichment_data.get("items", [])
        else:
            items = []

        # Check if we have any items
        if not items:
            return JsonResponse(
                {"success": True, "has_enrichment": False, "html": ""}
            )

        # Filter out newly published items
        filtered_items = []
        for item in items:
            if not item.get("is_newly_published", False):
                filtered_items.append(item)

        # Limit to first 3 items
        filtered_items = filtered_items[:3]

        if not filtered_items:
            return JsonResponse(
                {"success": True, "has_enrichment": False, "html": ""}
            )

        # Render the HTML using the template
        html = render_to_string(
            "records/fragments/subjects_enrichment_content.html",
            {"items": filtered_items},
        )

        return JsonResponse(
            {"success": True, "has_enrichment": True, "html": html}
        )

    except Exception as e:
        logger.error(
            f"Failed to fetch subjects enrichment for {record_id}: {e}"
        )
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@require_GET
def available_online_api(request, record_id):
    """API endpoint for available online box - uses Phase 2 data."""
    try:
        from app.deliveryoptions.api import delivery_options_request_handler
        from app.deliveryoptions.delivery_options import get_availability_group
        from app.records.api import record_details_by_id
        from django.template.loader import render_to_string

        record = record_details_by_id(id=record_id)

        # Fetch delivery options (same as Phase 2)
        delivery_result = delivery_options_request_handler(record.iaid)

        do_availability_group = None
        if isinstance(delivery_result, list) and delivery_result:
            delivery_option_value = delivery_result[0].get("options")
            if delivery_option_value is not None:
                do_availability_group = get_availability_group(
                    delivery_option_value
                )
                do_availability_group = (
                    do_availability_group.name
                    if do_availability_group
                    else None
                )

        html = render_to_string(
            "records/fragments/available_online_content.html",
            {"record": record, "do_availability_group": do_availability_group},
        )

        return JsonResponse(
            {
                "success": True,
                "has_content": bool(do_availability_group),
                "html": html,
            }
        )
    except Exception as e:
        logger.error(f"Failed to fetch available online for {record_id}: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@require_GET
def available_in_person_api(request, record_id):
    """API endpoint for available in person box - uses Phase 2 data."""
    try:
        from app.deliveryoptions.api import delivery_options_request_handler
        from app.deliveryoptions.delivery_options import get_availability_group
        from app.records.api import record_details_by_id
        from django.template.loader import render_to_string

        record = record_details_by_id(id=record_id)

        # Fetch delivery options (same as Phase 2)
        delivery_result = delivery_options_request_handler(record.iaid)

        do_availability_group = None
        if isinstance(delivery_result, list) and delivery_result:
            delivery_option_value = delivery_result[0].get("options")
            if delivery_option_value is not None:
                do_availability_group = get_availability_group(
                    delivery_option_value
                )
                do_availability_group = (
                    do_availability_group.name
                    if do_availability_group
                    else None
                )

        html = render_to_string(
            "records/fragments/available_in_person_content.html",
            {"record": record, "do_availability_group": do_availability_group},
        )

        return JsonResponse(
            {
                "success": True,
                "has_content": bool(do_availability_group),
                "html": html,
            }
        )
    except Exception as e:
        logger.error(
            f"Failed to fetch available in person for {record_id}: {e}"
        )
        return JsonResponse({"success": False, "error": str(e)}, status=500)
