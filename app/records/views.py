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
    Returns enrichment data or empty dict on failure.
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

    Args:
        iaid: The document iaid

    Returns:
        Dictionary with delivery options context containing:
        - delivery_option: The AvailabilityCondition name as string (if valid)
        - availability_group: The availability group name (if mapped to a group)
        May return empty dict if unavailable or on error.
    """
    try:
        delivery_result = delivery_options_request_handler(iaid)

        # Validate we got results and it's a list
        if not delivery_result or not isinstance(delivery_result, list):
            logger.info(f"No delivery options available for iaid {iaid}")
            return {}

        # Check list is not empty before accessing first element
        if len(delivery_result) == 0:
            logger.info(f"Empty delivery options list for iaid {iaid}")
            return {}

        # Extract the delivery option value
        first_result = delivery_result[0]
        delivery_option_value = first_result.get("options")

        if delivery_option_value is None:
            logger.warning(
                f"No 'options' value in delivery result for iaid {iaid}"
            )
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
        availability_group = get_availability_group(delivery_option_value)

        # Add availability group to context if it exists
        if availability_group is not None:
            context["availability_group"] = availability_group.name

        return context

    except Exception as e:
        logger.error(
            f"Failed to get delivery options for iaid {iaid}: {str(e)}",
            exc_info=True,
        )
        return {}


def record_detail_view(request, id):
    """
    View for rendering a record's details page.
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
    if determine_delivery_options:
        # Add temporary delivery options context
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
    if determine_delivery_options:
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


def related_records_view(request, id):
    template_name = "records/related_records.html"
    context: dict = {}

    record = record_details_by_id(id=id)

    context.update(
        record=record,
    )

    return TemplateResponse(
        request=request, template=template_name, context=context
    )


def records_help_view(request, id):
    template_name = "records/new_to_archives.html"
    context: dict = {}

    record = record_details_by_id(id=id)

    context.update(
        record=record,
    )

    return TemplateResponse(
        request=request, template=template_name, context=context
    )
