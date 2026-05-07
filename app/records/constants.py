from enum import Enum, StrEnum

from django.conf import settings


class _LevelLookupMixin:
    @classmethod
    def from_id(cls, level_id: str):
        return next((m for m in cls if m.level_id == level_id), None)

    @classmethod
    def level_from_code(cls, level_id: str) -> str:
        member = cls.from_id(level_id)
        return member.label if member else ""


# Some of these values are also used by Delivery Options
# TODO: use integer values rather than strings for level_ids
class TnaLevels(_LevelLookupMixin, Enum):
    """
    TNA Hierarchy levels, as defined in the API.
    Each member's value is a tuple of:
        (level_id: str, label: str)
    level_id - level id in the API
    label - the value that describes the level id for display and filter construction
    """

    DEPARTMENT = ("1", "Department")
    DIVISION = ("2", "Division")
    SERIES = ("3", "Series")
    SUB_SERIES = ("4", "Sub-series")
    SUB_SUB_SERIES = ("5", "Sub-sub-series")
    PIECE = ("6", "Piece")
    ITEM = ("7", "Item")

    def __init__(self, level_id: str, label: str):
        self.level_id = level_id
        self.label = label


# TODO: use integer values rather than strings for level_ids
class NonTnaLevels(_LevelLookupMixin, Enum):
    """
    Non TNA Hierarchy levels, as defined in the API.
    Each member's value is a tuple of:
        (level_id: str, label: str)
    level_id - level id in the API
    label - the value that describes the level id for display
    """

    FONDS = ("1", "Fonds")
    SUB_FONDS = ("2", "Sub-fonds")
    SUB_SUB_FONDS = ("3", "Sub-sub-fonds")
    SUB_SUB_SUB_FONDS = ("4", "Sub-sub-sub-fonds")
    SERIES = ("5", "Series")
    SUB_SERIES = ("6", "Sub-series")
    SUB_SUB_SERIES = ("7", "Sub-sub-series")
    SUB_SUB_SUB_SERIES = ("8", "Sub-sub-sub-series")
    FILE = ("9", "File")
    ITEM = ("10", "Item")
    SUB_ITEM = ("11", "Sub-item")

    def __init__(self, level_id: str, label: str):
        self.level_id = level_id
        self.label = label


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


class RecordTypes(StrEnum):
    """Record types"""

    ARCHON = "ARCHON"
    CREATORS = "CREATORS"


TNA_ARCHON_CODE = "66"
