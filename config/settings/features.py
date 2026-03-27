import os

from config.util import strtobool

FEATURE_PHASE_BANNER: bool = strtobool(
    os.getenv("FEATURE_PHASE_BANNER", "True")
)

# True: activates link to Catalogue Archon Page and live data for TNA Archon
# False: activates links to Discovery Archon Page and static data for TNA Archon
FEATURE_ENABLE_RECORD_DETAILS_HELD_BY: bool = strtobool(
    os.getenv("FEATURE_ENABLE_RECORD_DETAILS_HELD_BY", "False")
)
