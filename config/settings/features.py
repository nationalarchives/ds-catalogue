import os

from config.util import strtobool

FEATURE_PHASE_BANNER: bool = strtobool(
    os.getenv("FEATURE_PHASE_BANNER", "True")
)
