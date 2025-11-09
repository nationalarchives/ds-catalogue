import logging
import os
from http import HTTPStatus

import requests
from app.deliveryoptions.api import delivery_options_request_handler
from app.deliveryoptions.constants import AvailabilityCondition
from app.deliveryoptions.delivery_options import (
    construct_delivery_options,
    get_availability_group,
    has_distressing_content,
)
from app.deliveryoptions.helpers import BASE_TNA_DISCOVERY_URL
from app.lib.api import JSONAPIClient, ResourceNotFound
from app.records.api import record_details_by_id, wagtail_request_handler
from app.records.labels import FIELD_LABELS
from django.conf import settings
from django.http import HttpRequest
from django.template.response import TemplateResponse
from django.utils.text import slugify
from sentry_sdk import capture_message

# TODO: Implement record_detail_by_reference once Rosetta has support
# from app.records.api import record_details_by_ref
# from django.template.loader import get_template
# from django.urls import reverse
# def record_detail_by_reference(request, reference):
#     """
#     View for rendering a record's details page.
#     """
#     template_name = "records/record_detail.html"
#     context = {"field_labels": FIELD_LABELS, "level_labels": LEVEL_LABELS, "non_tna_level_labels": NON_TNA_LEVEL_LABELS}

#     try:
#         # record = record_details_by_ref(id=reference)
#         record = record_details_by_id(id="D4664016")
#     except ResourceNotFound:
#         raise Http404
#     except Exception:
#         raise HttpResponseServerError

#     context.update(
#         record=record,
#         canonical=reverse(
#             "details-page-machine-readable", kwargs={"id": record.id}
#         ),
#     )

#     if record.custom_record_type:
#         if record.custom_record_type == "ARCHON":
#             template_name = "records/archon_detail.html"
#         if record.custom_record_type == "CREATORS":
#             template_name = "records/creator_detail.html"

#     return TemplateResponse(
#         request=request, template=template_name, context=context
#     )

logger = logging.getLogger(__name__)


# TODO: reimplement these views as classed based as they are starting to get more complex.
def get_subjects_enrichment(subjects_list: list[str], limit: int = 10) -> dict:
    """
    Makes API call to enrich subjects data for a single record.

    Fetches additional article/content data associated with the provided subject tags
    from the Wagtail CMS article_tags endpoint.

    Args:
        subjects_list: List of subject strings to enrich
        limit: Maximum number of enrichment items to return (default: 10)

    Returns:
        Dictionary containing enrichment data with articles/content related to the subjects,
        or empty dict on failure or if no subjects provided.
    """
    if not subjects_list:
        return {}

    slugified_subjects = [slugify(subject) for subject in subjects_list]
    subjects_param = ",".join(slugified_subjects)

    try:
        params = {"tags": subjects_param, "limit": limit}
        results = wagtail_request_handler("/article_tags", params)
        logger.info(
            f"Successfully fetched subjects enrichment for: {subjects_param}"
        )
        return results
    except ResourceNotFound:
        logger.warning(f"No subjects enrichment found for {subjects_param}")
        return {}
    except Exception as e:
        logger.warning(
            f"Failed to fetch subjects enrichment for {subjects_param}: {e}"
        )
        return {}


def get_delivery_options_context(iaid: str) -> dict:
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


def record_detail_view(request: HttpRequest, id: str) -> TemplateResponse:
    """
    View for rendering an individual archive record's details page.

    Fetches record data by ID, enriches it with subjects data and delivery options,
    checks for sensitive content warnings, and renders the appropriate template
    based on the record type (standard, ARCHON, or CREATORS).

    Args:
        request: The Django HTTP request object
        id: The record IAID (Information Asset Identifier)

    Returns:
        TemplateResponse with rendered record detail page
    """
    template_name = "records/record_detail.html"
    context: dict = {
        "field_labels": FIELD_LABELS,
    }

    global_alerts_client = JSONAPIClient(settings.WAGTAIL_API_URL)
    global_alerts_client.add_parameters(
        {"fields": "_,global_alert,mourning_notice"}
    )
    try:
        context["global_alert"] = global_alerts_client.get(
            f"/pages/{settings.WAGTAIL_HOME_PAGE_ID}"
        )
    except Exception as e:
        logger.error(e)
        context["global_alert"] = {}

    record = record_details_by_id(id=id)

    if record.subjects:
        subjects_enrichment = get_subjects_enrichment(
            record.subjects, limit=settings.MAX_SUBJECTS_PER_RECORD
        )
        record._subjects_enrichment = subjects_enrichment
        logger.info(
            f"Enriched record {record.iaid} with {len(subjects_enrichment)} subject items"
        )
    else:
        record._subjects_enrichment = {}

    context.update(
        record=record,
    )

    determine_delivery_options = True

    if record.custom_record_type:
        if record.custom_record_type == "ARCHON":
            determine_delivery_options = False
            template_name = "records/archon_detail.html"
        elif record.custom_record_type == "CREATORS":
            template_name = "records/creator_detail.html"
            determine_delivery_options = False

    # TODO: This is an alternative action on delivery options while we wait on decisions on how we are going to present it.
    # Only run this for TNA records
    if (
        record.is_tna and determine_delivery_options
    ):  # Add temporary delivery options context
        delivery_options_context = {
            "delivery_options_heading": "How to order it",
            "delivery_instructions": [
                "View this record page in our current catalogue",
                "Check viewing and downloading options",
                "Select an option and follow instructions",
            ],
            "tna_discovery_link": f"{BASE_TNA_DISCOVERY_URL}/details/r/{record.iaid}",
        }
        context.update(delivery_options_context)

    # Separated from above if statement because this is permanent logic
    # Only run this for TNA records
    if (
        record.is_tna and determine_delivery_options
    ):  # Add temporary delivery options context
        context.update(get_delivery_options_context(record.iaid))

    # if determine_delivery_options:
    # TODO: Temporarily commented out delivery options functionality
    # # Only get the delivery options if we are looking at records
    # # Get the delivery options for the iaid
    # delivery_options_context = {}

    # try:
    #     delivery_options = delivery_options_request_handler(
    #         iaid=record.iaid
    #     )

    #     delivery_options_context = construct_delivery_options(
    #         delivery_options, record, request
    #     )

    # except Exception as e:
    #     # Built in order exception option
    #     error_message = f"DORIS Connection error using url '{os.getenv("DELIVERY_OPTIONS_API_URL", "")}' - returning OrderException from Availability Conditions {str(e)}"

    #     # Sentry notification
    #     logger.error(error_message)
    #     capture_message(error_message)

    #     # The delivery options include a special case called OrderException which has nothing to do with
    #     # python exceptions. It is the message to be displayed when the connection is down or there is no
    #     # match for the given iaid. So, we don't treat it as a python exception beyond this point.
    #     delivery_options_context = construct_delivery_options(
    #         [
    #             {
    #                 "options": AvailabilityCondition.OrderException,
    #                 "surrogateLinks": [],
    #                 "advancedOrderUrlParameters": "",
    #             }
    #         ],
    #         record,
    #         request,
    #     )

    # context.update(delivery_options_context)

    context["distressing_content"] = has_distressing_content(
        record.reference_number
    )

    if context["distressing_content"]:
        logger.info(
            f"Document {record.reference_number} has a sensitive content warning"
        )

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
    template_name = "records/related_records.html"
    context: dict = {}

    record = record_details_by_id(id=id)

    context.update(
        record=record,
    )

    return TemplateResponse(
        request=request, template=template_name, context=context
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
    template_name = "records/new_to_archives.html"
    context: dict = {}

    record = record_details_by_id(id=id)

    context.update(
        record=record,
    )

    return TemplateResponse(
        request=request, template=template_name, context=context
    )
