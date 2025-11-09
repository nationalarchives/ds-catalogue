from enum import StrEnum

RESULTS_PER_PAGE = 20  # max records to show per page
PAGE_LIMIT = 500  # max page number that can be queried
FILTER_DATATYPE_RECORD = (
    "datatype:record"  # filter for records in search results
)


class Sort(StrEnum):
    """Options for sorting /search results by a given field."""

    RELEVANCE = ""
    TITLE_ASC = "title:asc"
    TITLE_DESC = "title:desc"
    DATE_ASC = "date:asc"
    DATE_DESC = "date:desc"


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
