from enum import StrEnum

# Elasticsearch limitation: can only return first 10,000 results
# With RESULTS_PER_PAGE=20, PAGE_LIMIT=500 ensures we never request beyond
# that limit: 500 pages × 20 results/page = 10,000 results.
RESULTS_PER_PAGE = 20  # max records to show per page
PAGE_LIMIT = 500  # max page number that can be queried

# UI: warn users when approaching page limit
PAGE_LIMIT_WARNING_THRESHOLD = PAGE_LIMIT - 5  # Show warning at page 495
PAGE_LIMIT_WARNING_MESSAGE = (
    "Only the first 10,000 results are shown, apply filters to narrow your search."
)

FILTER_DATATYPE_RECORD = "datatype:record"  # filter for records in search results


class Sort(StrEnum):
    """Options for sorting /search results by a given field."""

    RELEVANCE = ""
    TITLE_ASC = "title:asc"
    TITLE_DESC = "title:desc"
    DATE_ASC = "dateCovering:asc"
    DATE_DESC = "dateCovering:desc"


# date format for displaying dates in the UI (e.g. active filters, error message
DATE_DISPLAY_FORMAT = "%d-%m-%Y"


class FieldsConstant:
    Q = "q"
    SORT = "sort"
    LEVEL = "level"
    GROUP = "group"
    COLLECTION = "collection"
    ONLINE = "online"
    SUBJECT = "subject"
    HELD_BY = "held_by"
    CLOSURE = "closure"
    FILTER_LIST = "filter_list"
    COVERING_DATE_FROM = "covering_date_from"
    COVERING_DATE_TO = "covering_date_to"
    OPENING_DATE_FROM = "opening_date_from"
    OPENING_DATE_TO = "opening_date_to"
    DISPLAY = "display"


FILTER_FIELDS = [
    FieldsConstant.ONLINE,
    FieldsConstant.LEVEL,
    FieldsConstant.COLLECTION,
    FieldsConstant.SUBJECT,
    FieldsConstant.CLOSURE,
    FieldsConstant.HELD_BY,
    FieldsConstant.COVERING_DATE_FROM,
    FieldsConstant.COVERING_DATE_TO,
    FieldsConstant.OPENING_DATE_FROM,
    FieldsConstant.OPENING_DATE_TO,
]


class Display(StrEnum):
    """Options for displaying /search results."""

    LIST = "list"
    GRID = "grid"
