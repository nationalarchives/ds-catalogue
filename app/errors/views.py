import logging
from http import HTTPStatus

from django.http import HttpResponseServerError
from django.shortcuts import render
from django.template import TemplateDoesNotExist

from .constants import PAGE_NOT_FOUND_TEMPLATE, SERVER_ERROR_TEMPLATE

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
        return HttpResponseServerError(
            "Internal Server Error: Template not found."
        )
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
        return HttpResponseServerError(
            "Internal Server Error: Template not found."
        )
    response.status_code = status_code
    return response
