import os

from config.util import strtobool

FEATURE_PHASE_BANNER: bool = strtobool(
    os.getenv("FEATURE_PHASE_BANNER", "True")
)


# TODO: Remove Temporary feature flag and related code
# when the feature is disabled and API data issue is resolved.
# True: activates link to Discovery Archon Page for non-TNA records,
#       Catalogue Archon Page for TNA records with static data
# False: activates links to Catalogue Archon Page with API data
FEATURE_ENABLE_HELD_BY_DISCOVERY: bool = strtobool(
    os.getenv("FEATURE_ENABLE_HELD_BY_DISCOVERY", "True")
)
