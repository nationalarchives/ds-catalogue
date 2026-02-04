from django.conf import settings

# Some of these values are also used by Delivery Options
# TODO: Refactor to use Enums throughout the codebase
TNA_LEVELS = {
    "1": "Department",
    "2": "Division",
    "3": "Series",
    "4": "Sub-series",
    "5": "Sub-sub-series",
    "6": "Piece",
    "7": "Item",
}


# Some of these values are also used by Delivery Options
# TODO: Refactor to use Enums throughout the codebase

NON_TNA_LEVELS = {
    "1": "Fonds",
    "2": "Sub-fonds",
    "3": "Sub-sub-fonds",
    "4": "Sub-sub-sub-fonds",
    "5": "Series",
    "6": "Sub-series",
    "7": "Sub-sub-series",
    "8": "Sub-sub-sub-series",
    "9": "File",
    "10": "Item",
    "11": "Sub-item",
}

SUBJECTS_LIMIT = 20

MISSING_COUNT_TEXT = "Unknown number of"

RELATED_RECORDS_FETCH_LIMIT = 10

TNA_HELD_BY_VALUES = [
    "The National Archives",
    "The National Archives, Kew",
]

API_TIMEOUTS = {
    "subjects": settings.WAGTAIL_API_TIMEOUT,
    "related": settings.ROSETTA_ENRICHMENT_API_TIMEOUT,
    "delivery": settings.DELIVERY_OPTIONS_API_TIMEOUT,
}

THREADPOOL_MAX_WORKERS = 3
