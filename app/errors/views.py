import logging
from http import HTTPStatus

from django.http import HttpRequest, HttpResponse, HttpResponseServerError
from django.shortcuts import render
from django.template import TemplateDoesNotExist

from .constants import (
    PAGE_NOT_FOUND_TEMPLATE,
    SERVER_ERROR_TEMPLATE,
    UNKNOWN_REQUEST_TEMPLATE,
)

logger = logging.getLogger(__name__)


def page_not_found_error_view(
    request, exception=None, status_code=HTTPStatus.NOT_FOUND
):
    try:
        response = render(
            request,
            PAGE_NOT_FOUND_TEMPLATE,
            context={"status_code": status_code},
        )
    except TemplateDoesNotExist as e:
        logger.error(f"Template missing: {e}")
        return HttpResponseServerError("Internal Server Error: Template not found.")
    response.status_code = status_code
    return response


def server_error_view(
    request, exception=None, status_code=HTTPStatus.INTERNAL_SERVER_ERROR
):
    try:
        response = render(
            request, SERVER_ERROR_TEMPLATE, context={"status_code": status_code}
        )
    except TemplateDoesNotExist as e:
        logger.error(f"Template missing: {e}")
        return HttpResponseServerError("Internal Server Error: Template not found.")
    response.status_code = status_code
    return response


def unknown_request_view(
    request: HttpRequest,
    status_code: HTTPStatus = HTTPStatus.BAD_REQUEST,
    errors: list[dict[str, str]] | None = None,
    show_new_search: bool = False,
) -> HttpResponse | HttpResponseServerError:
    """Render the unknown request error page.

    Args:
        request: The Django request object.
        status_code: The HTTP status code to return.
        NOTE: status_code MUST be HTTP 400, 405 or 406 only.
        errors: A list of dictionaries containing error details.
        show_new_search: Whether to show the "Start new search" link. Usually set to True
        when called from Search views.

    Returns:
        A Django HttpResponse or HttpResponseServerError object with the rendered template
        and status code.
    """
    allowed_status_codes = {
        HTTPStatus.BAD_REQUEST,
        HTTPStatus.METHOD_NOT_ALLOWED,
        HTTPStatus.NOT_ACCEPTABLE,
    }
    if status_code not in allowed_status_codes:
        logger.error(
            f"Invalid status code passed to unknown_request_view: {status_code}"
        )
        raise ValueError(f"Unsupported status code: {status_code}")

    try:
        response = render(
            request,
            UNKNOWN_REQUEST_TEMPLATE,
            context={
                "status_code": status_code,
                "errors": errors,
                "show_new_search": show_new_search,
            },
        )
    except TemplateDoesNotExist as e:
        logger.error(f"Template missing: {e}")
        return HttpResponseServerError("Internal Server Error: Template not found.")
    response.status_code = status_code
    return response
