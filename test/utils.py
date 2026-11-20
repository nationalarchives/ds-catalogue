"""Utils used to support running Tests"""

import logging
from unittest.mock import patch


def prevent_request_warnings(original_function):
    """
    If we need to test for 404, 503s this decorator can prevent
    the request class from throwing warnings.

    Ex: suppresses 404 for get request
    """

    def new_function(*args, **kwargs):
        # set logging level before triggering original function
        logger = logging.getLogger("django.request")
        previous_logging_level = logger.getEffectiveLevel()
        logger.setLevel(logging.CRITICAL)  # Suppresses ERROR and below

        # trigger original function that would throw error
        original_function(*args, **kwargs)

        # set logging level back to previous
        logger.setLevel(previous_logging_level)

    return new_function


def patch_collection_choices(return_value=(("VALUE1", "VALUE1 Collection"),)):
    """Mock collection choices to avoid unintended reuse of test API responses.
    Overrides the default collection choices for testing purposes.
    """
    return patch(
        "app.search.forms.get_all_collection_choices",
        return_value=return_value,
    )
