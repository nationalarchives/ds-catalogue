"""
Module for handling delivery options for records.

Provides functionality to construct and process delivery options for records
based on their availability conditions and the type of user requesting access.

# TODO: The JSON file will be replaced by templates at some point. This will require
# an overhaul of much of the code.
"""

import inspect
import json
import logging
import re
from functools import lru_cache
from ipaddress import ip_address
from typing import Any, Dict, List, Optional, Union

from app.deliveryoptions.constants import (
    DELIVERY_OPTIONS_CONFIG,
    AvailabilityCondition,
    delivery_option_tags,
)
from app.deliveryoptions.departments import DEPARTMENT_DETAILS
from app.deliveryoptions.helpers import get_dept
from app.deliveryoptions.reader_type import get_reader_type
from app.records.models import Record
from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest

logger = logging.getLogger(__name__)

# Dictionary to serve as a cache for file contents, preventing redundant file reads
# TODO: To be replaced by templating
file_cache = {}


def read_delivery_options(file_path: str) -> Dict:
    """
    Read and parse the delivery options JSON configuration file.

    Uses a file cache to avoid re-reading the same file multiple times.

    Args:
        file_path: Path to the delivery options JSON file

    Returns:
        The parsed delivery options configuration

    TODO: To be replaced by templating as a future date
    """
    # Check if file content is already in the cache
    if file_path not in file_cache:
        # Open the file in read mode
        with open(file_path, "r") as file:
            # Load the JSON content from the file
            file_content = json.load(file)

            # Cache the file content for future use
            file_cache[file_path] = file_content

    # Return the file content either from the cache or newly loaded
    return file_cache[file_path]


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


def get_delivery_option_dict(
    dict_cache: Dict, record_id: int
) -> Optional[Dict[str, Any]]:
    """
    Get a record from the cache by its ID.

    Args:
        dictcache: The cache dictionary
        record_id: The record ID to retrieve

    Returns:
        The record if found, None otherwise

    # TODO: To be replaced by templating
    """
    try:
        return dict_cache["deliveryOptions"]["option"][record_id]
    except Exception:
        return None


def html_replacer(value: str, record: Record, api_surrogate_list: List) -> str:
    """
    Replace placeholders in a string with actual values.

    Finds all tags in the format {TagName} and replaces them with
    the result of calling the corresponding function from delivery_option_tags.

    Args:
        value: The string containing placeholders
        record: The record object
        api_surrogate_data: List of surrogate data

    Returns:
        The string with placeholders replaced with actual values

    Raises:
        Exception: If a placeholder function call fails
    """
    tags = re.findall(r"{[A-Za-z]*}", value)

    for tag in tags:
        try:
            function = delivery_option_tags[tag]

            # Get the function signature parameters
            function_signature = inspect.signature(function)
            params = {}

            # Add only the parameters the function expects
            param_names = set(function_signature.parameters.keys())

            if "record" in param_names:
                params["record"] = record
            if "api_surrogate_list" in param_names:
                params["api_surrogate_list"] = api_surrogate_list

            if replacement := function(**params):
                value = value.replace(tag, replacement)

        except Exception:
            raise

    return value


def html_builder(
    delivery_option_data: Union[List, str],
    record_data: Record,
    api_surrogate_data: List = None,
    dcs: bool = False,
) -> str:
    """
    Build HTML content from delivery option data, replacing placeholders.

    Args:
        delivery_option_data: The delivery option data to process
        record_data: The record object
        api_surrogate_data: List of surrogate data
        dcs: Whether to include distressing content section

    Returns:
        The processed HTML content
    """
    html = ""

    # The description can contain an ordinary description and a DCS description. Which one
    # is chosen is down to whether the document reference prefix matches any in
    # DCS_PREFIXES. So, if the code finds a descriptionDCS record but
    # the prefix doesn't match, it skips it.

    if isinstance(delivery_option_data, list):
        for item in delivery_option_data:
            if not dcs and item["name"] == "descriptionDCS":
                pass
            else:
                html += html_replacer(
                    item["value"], record_data, api_surrogate_data
                )
    else:
        html = html_replacer(
            delivery_option_data, record_data, api_surrogate_data
        )

    return html


def surrogate_link_builder(surrogates: List) -> List[Any]:
    """
    Extract surrogate links and AV media links from surrogate data.

    Args:
        surrogates: The list of surrogate data

    Returns:
        A list containing surrogate links (including AV media links)
    """
    surrogate_list = []

    for s in surrogates:
        if s["xReferenceURL"]:
            surrogate_list.append(s["xReferenceURL"])

    return surrogate_list


def process_order_buttons(
    delivery_option_data: List,
    record_data: Record,
    api_surrogate_data: List = None,
) -> List[Dict]:
    """
    Process order buttons data with HTML replacement.

    Args:
        delivery_option_data: The data to process
        record_data: The record object
        api_surrogate_data: List of surrogate data

    Returns:
        A list of processed order button data
    """
    result = []
    for item in delivery_option_data:
        processed_item = {}
        for key, value in item.items():
            if key in ["href", "text"]:
                processed_item[key] = html_builder(
                    value,
                    record_data,
                    api_surrogate_data=api_surrogate_data,
                )
            else:
                processed_item[key] = value
        result.append(processed_item)
    return result


def generic_builder(
    delivery_option_data: Union[List, str],
    record_data: Record,
    api_surrogate_data: List = None,
    builder_type: str = "default",
) -> Union[str, List]:
    """
    A generic builder function to handle various delivery option content types.

    Args:
        delivery_option_data: The data to process
        record_data: The record object
        api_surrogate_data: List of surrogate data
        builder_type: Type of builder to determine special processing

    Returns:
        Processed content (str or List) based on the builder type
    """
    # Handle special case for distressing content
    dcs_flag = False
    if builder_type == "description" and has_distressing_content(
        record_data.reference_number
    ):
        dcs_flag = True

    # Handle order buttons specifically
    if builder_type == "orderbuttons" and isinstance(
        delivery_option_data, list
    ):
        return process_order_buttons(
            delivery_option_data, record_data, api_surrogate_data
        )

    # Standard HTML building
    return html_builder(
        delivery_option_data,
        record_data,
        api_surrogate_data=api_surrogate_data,
        dcs=dcs_flag,
    )


def construct_delivery_options(
    api_result: List, record: Record, request: HttpRequest
) -> Dict[str, Any]:
    """
    Construct delivery options based on record and request information.

    This is the main function to build the delivery options for a record.

    Args:
        api_result: List of delivery options
        record: The record object
        request: The HTTP request

    Returns:
        The constructed delivery options
    """

    if api_length := len(api_result) != 1:
        raise ValueError(
            f"Expected one record only ({api_length}) from DORIS database for IAID {record.iaid}"
        )

    delivery_options_context_dict = {}

    reader_type = get_reader_type(request)

    delivery_options_context_dict["reader_type"] = reader_type

    # TODO: the do_dict dictionary will be redundant when we turn to template based code
    do_dict = read_delivery_options(DELIVERY_OPTIONS_CONFIG)

    # Surrogate links is always present as a list, which can be empty
    do_surrogate = surrogate_link_builder(api_result[0]["surrogateLinks"])

    availability_condition = api_result[0]["options"]

    if (
        availability_condition == AvailabilityCondition.ClosedRetainedDeptKnown
        and not get_dept(record.reference_number, "deptname")
    ):
        # Special case. Sometimes, for record type 14 (ClosedRetainedDeptKnown), the department name does not match
        # any entry in the DEPARTMENT_DETAILS dictionary. This shouldn't happen but it does. Therefore, reset the type
        # with that for AvailabilityCondition.ClosedRetainedDeptUnKnown
        availability_condition = AvailabilityCondition.ClosedRetainedDeptUnKnown

    # Get the specific delivery option for this artefact
    # TODO: the do_dict dictionary will be redundant when we turn to template based code
    delivery_option = get_delivery_option_dict(do_dict, availability_condition)

    reader_option = delivery_option["readertype"][reader_type]

    # Mapping of builder types for different option keys
    builder_mappings = {
        "heading": ("do_heading", "heading"),
        "description": ("do_description", "description"),
        "supplementalcontent": ("do_supplemental", "supplemental"),
        "orderbuttons": ("do_orderbuttons", "orderbuttons"),
        "expandlink": ("do_expandlink", "expandlink"),
        "basketlimit": ("do_basketlimit", "basketlimit"),
    }

    for option_key, (context_key, builder_type) in builder_mappings.items():
        if content := reader_option.get(option_key):
            delivery_options_context_dict[context_key] = generic_builder(
                content,
                record,
                api_surrogate_data=do_surrogate,
                builder_type=builder_type,
            )

    return delivery_options_context_dict
