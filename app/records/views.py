"""Views for displaying archive records."""

import logging
from http import HTTPStatus

from app.deliveryoptions.delivery_options import has_distressing_content
from app.deliveryoptions.helpers import BASE_TNA_DISCOVERY_URL
from app.lib.api import JSONAPIClient
from app.records.api import (
    get_subjects_enrichment,
    record_details_by_id,
)
from app.records.labels import FIELD_LABELS
from app.records.models import Record
from app.records.related import (
    get_related_records_by_series,
    get_related_records_by_subjects,
)
from django.conf import settings
from django.http import HttpRequest
from django.template.response import TemplateResponse

logger = logging.getLogger(__name__)


# Helper functions (will become mixin methods when converting to CBVs)


def _get_global_alerts() -> dict:
    """
    Fetches global alerts and mourning notices from Wagtail.

    Returns:
        Dictionary containing global_alert data, or empty dict on error
    """
    global_alerts_client = JSONAPIClient(settings.WAGTAIL_API_URL)
    global_alerts_client.add_parameters(
        {"fields": "_,global_alert,mourning_notice"}
    )
    try:
        return global_alerts_client.get(
            f"/pages/{settings.WAGTAIL_HOME_PAGE_ID}"
        )
    except Exception as e:
        logger.error(f"Failed to fetch global alerts: {e}")
        return {}


def _enrich_record_subjects(record: Record) -> None:
    """
    Enriches a record with subjects data in-place.

    Fetches related articles and content for the record's subject tags
    from the Wagtail CMS and attaches them to the record object.

    Args:
        record: The record to enrich (modified in-place)
    """
    if record.subjects:
        subjects_enrichment = get_subjects_enrichment(
            record.subjects, limit=settings.MAX_SUBJECTS_PER_RECORD
        )
        record._subjects_enrichment = subjects_enrichment
    else:
        record._subjects_enrichment = {}


def _get_related_records(record: Record, limit: int = 3) -> list[Record]:
    """
    Fetches related records using subjects first, then series as fallback.

    Attempts to find related records by shared subjects. If fewer than the
    requested limit are found, backfills the remaining slots with records
    from the same archival series.

    Args:
        record: The record to find relations for
        limit: Maximum number of related records to return (default: 3)

    Returns:
        List of related Record objects (up to limit)
    """
    related_records = get_related_records_by_subjects(record, limit=limit)

    # Backfill from series if needed
    if len(related_records) < limit:
        remaining_slots = limit - len(related_records)
        series_records = get_related_records_by_series(
            record, limit=remaining_slots
        )
        related_records.extend(series_records)

    return related_records


def _get_delivery_options_context(iaid: str) -> dict:
    """
    Fetch and process delivery options for a record.

    Calls the delivery options API to determine how a record can be accessed
    (e.g., available online, orderable, closed, etc.) and maps the result to
    an availability group for display purposes.

    Args:
        iaid: The document IAID (Information Asset Identifier)

    Returns:
        Dictionary with delivery options context containing:
        - delivery_option: The AvailabilityCondition name as string (if valid)
        - do_availability_group: The availability group name (if mapped to a group)
        Returns empty dict if unavailable or on error.
    """
    try:
        delivery_result = delivery_options_request_handler(iaid)

        # Ensure we have at least one delivery_result in the returned list
        if not isinstance(delivery_result, list) or not delivery_result:
            return {}

        # Extract the delivery option value - we know there is at least 1 record and we are only interested in the first
        first_result = delivery_result[0]
        delivery_option_value = first_result.get("options")

        if delivery_option_value is None:
            return {}

        # Convert to AvailabilityCondition enum and get name
        try:
            delivery_option_enum = AvailabilityCondition(delivery_option_value)
            delivery_option_name = delivery_option_enum.name
        except ValueError:
            logger.warning(
                f"Unknown delivery option value {delivery_option_value} for iaid {iaid}"
            )
            return {}

        # Build context with the delivery option name
        context = {"delivery_option": delivery_option_name}

        # Get the availability group for this delivery option
        do_availability_group = get_availability_group(delivery_option_value)

        # Add availability group to context if it exists
        if do_availability_group is not None:
            context["do_availability_group"] = do_availability_group.name

        return context

    except Exception as e:
        logger.error(
            f"Failed to get delivery options for iaid {iaid}: {str(e)}",
            exc_info=True,
        )
        return {}


def _check_distressing_content(record: Record) -> bool:
    """
    Checks if record has distressing/sensitive content.

    Logs an info message if a content warning is found for the record.

    Args:
        record: The record to check

    Returns:
        True if distressing content warning exists, False otherwise
    """
    has_warning = has_distressing_content(record.reference_number)

    if has_warning:
        logger.info(
            f"Document {record.reference_number} has a sensitive content warning"
        )

    return has_warning


# Views


def record_detail_view(request: HttpRequest, id: str) -> TemplateResponse:
    """
    View for rendering an individual archive record's details page.

    Fetches record data by ID, enriches it with subjects data, finds related records,
    checks for sensitive content warnings, and renders the appropriate template
    based on the record type (standard, ARCHON, or CREATORS).

    Args:
        request: The Django HTTP request object
        id: The record IAID (Information Asset Identifier)

    Returns:
        TemplateResponse with rendered record detail page
    """
    # Fetch record and build base context
    record = record_details_by_id(id=id)

    context = {
        "field_labels": FIELD_LABELS,
        "global_alert": _get_global_alerts(),
        "record": record,
    }

    # Enrich record with subjects
    _enrich_record_subjects(record)

    # Fetch related records
    context["related_records"] = _get_related_records(record, limit=3)

    # Determine template based on record type
    template_name = "records/record_detail.html"
    determine_delivery_options = True

    if record.custom_record_type == "ARCHON":
        template_name = "records/archon_detail.html"
        determine_delivery_options = False
    elif record.custom_record_type == "CREATORS":
        template_name = "records/creator_detail.html"
        determine_delivery_options = False

    # Separated from above if statement because this is permanent logic
    if determine_delivery_options:
        context.update(_get_delivery_options_context(record.iaid))

    # Check for distressing content
    context["distressing_content"] = _check_distressing_content(record)

    return TemplateResponse(
        request=request, template=template_name, context=context
    )


def related_records_view(request: HttpRequest, id: str) -> TemplateResponse:
    """
    View for rendering a record's related records page.

    Displays records that are related to the specified record through
    hierarchical or associative relationships.

    Args:
        request: The Django HTTP request object
        id: The record IAID (Information Asset Identifier)

    Returns:
        TemplateResponse with rendered related records page
    """
    return TemplateResponse(
        request=request,
        template="records/related_records.html",
        context={
            "record": record_details_by_id(id=id),
        },
    )


def records_help_view(request: HttpRequest, id: str) -> TemplateResponse:
    """
    View for rendering help/guidance for users new to archives.

    Provides contextual help information about understanding and using
    archive records for the specified record.

    Args:
        request: The Django HTTP request object
        id: The record IAID (Information Asset Identifier)

    Returns:
        TemplateResponse with rendered help page
    """
    return TemplateResponse(
        request=request,
        template="records/new_to_archives.html",
        context={
            "record": record_details_by_id(id=id),
        },
    )