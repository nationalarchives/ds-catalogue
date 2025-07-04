import logging

from app.lib.api import ResourceNotFound
from django.conf import settings

from .views import page_not_found_error_view, server_error_view

logger = logging.getLogger(__name__)


class CustomExceptionMiddleware:
    """Centralised exception handling and logging."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """Handles exceptions raised by the client JSON api,
        bad data and unhandled exceptions."""

        # show error on screen in DEBUG mode
        if settings.DEBUG:
            raise  # re-raise error

        if isinstance(exception, ResourceNotFound):
            return page_not_found_error_view(
                request=request, exception=exception
            )

        # Exception() raised or Unhandled exceptions

        logger.exception(exception)
        return server_error_view(request=request)
