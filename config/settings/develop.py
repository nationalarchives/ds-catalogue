import os

from config.util import strtobool

from .base import *
from .features import *

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")

DEBUG = strtobool(os.getenv("DEBUG", "False"))

SENTRY_SAMPLE_RATE = float(os.getenv("SENTRY_SAMPLE_RATE", "1.0"))

if DEBUG:
    # logging
    LOGGING["root"]["level"] = "DEBUG"  # noqa: F405

    # debug toolbar
    INSTALLED_APPS += [  # noqa: F405
        "debug_toolbar",
    ]

    MIDDLEWARE = [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ] + MIDDLEWARE  # noqa: F405

    def show_toolbar(request) -> bool:
        return True

    DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": show_toolbar,
        "SHOW_COLLAPSED": True,
    }
