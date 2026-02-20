# codeql[py/unused-global-variable]: Django settings are used dynamically by the framework
# This intentionally avoids defining __all__ in settings, as it is a CodeQL anti-pattern
# to suppress unused-variable warnings in this way. Django settings files typically
# contain many variables that are accessed dynamically.
# Caveat: genuinely unused variables will not be flagged automatically and must be
# reviewed manually.

import os

from config.util import strtobool

from .features import *
from .production import *

DEBUG: bool = strtobool(os.getenv("DEBUG", "False"))

SENTRY_SAMPLE_RATE = float(os.getenv("SENTRY_SAMPLE_RATE", "0.25"))
