# codeql[unused-global-variable]: Django settings are used dynamically by the framework
# This intentionally avoids defining __all__ in settings, as it is a CodeQL anti-pattern
# to suppress unused-variable warnings in this way. Django settings files typically
# contain many variables that are accessed dynamically.
# Caveat: genuinely unused variables will not be flagged automatically and must be
# reviewed manually.

import os

from config.util import strtobool

from .features import *
from .production import *

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")

DEBUG = strtobool(os.getenv("DEBUG", "False"))

SENTRY_SAMPLE_RATE = float(os.getenv("SENTRY_SAMPLE_RATE", "1.0"))

if DEBUG:
    # logging
    LOGGING["root"]["level"] = "DEBUG"  # noqa: F405

    try:
        import debug_toolbar

        INSTALLED_APPS += [  # noqa: F405
            "debug_toolbar",
        ]

        MIDDLEWARE = [
            "debug_toolbar.middleware.DebugToolbarMiddleware",
        ] + MIDDLEWARE  # noqa: F405

        DEBUG_TOOLBAR_CONFIG = {
            "SHOW_TOOLBAR_CALLBACK": lambda request: True,
            "SHOW_COLLAPSED": True,
        }
    except ImportError:
        # Debug toolbar is not installed
        pass
