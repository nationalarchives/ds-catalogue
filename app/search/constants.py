from enum import StrEnum

RESULTS_PER_PAGE = 20  # max records to show per page
PAGE_LIMIT = 500  # max page number that can be queried
DATATYPE_RECORD = "datatype:record"  # filter for records in search results


class Sort(StrEnum):
    """Options for sorting /search results by a given field."""

    RELEVANCE = ""
    TITLE_ASC = "title:asc"
    TITLE_DESC = "title:desc"
    DATE_ASC = "date:asc"
    DATE_DESC = "date:desc"
