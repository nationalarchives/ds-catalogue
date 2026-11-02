from enum import StrEnum

# Elasticsearch limitation: can only return first 10,000 results
# With RESULTS_PER_PAGE=20, PAGE_LIMIT=500 ensures we never request beyond
# that limit: 500 pages × 20 results/page = 10,000 results.
RESULTS_PER_PAGE = 20  # max records to show per page
LONG_FILTER_RESULTS_PER_PAGE = 0  # for long filter, skip pagination to get all options
LONG_FILTER_SUBJECT_PARAMS = {"filter": ["group:tna"], "aggs": "longSubject"}
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
    ALL_WORDS = "all_words"
    EXACT_WORDS = "exact_words"
    ANY_WORDS = "any_words"
    IGNORE_WORDS = "ignore_words"
    REFERENCES = "references"
    COVERING_DATE_FROM = "covering_date_from"
    COVERING_DATE_TO = "covering_date_to"
    OPENING_DATE_FROM = "opening_date_from"
    OPENING_DATE_TO = "opening_date_to"
    DISPLAY = "display"
    REFERENCE_NUMBER = "reference_number"
    PARISH = "parish"
    COUNTY = "county"
    COUNTRY = "country"


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
    FieldsConstant.REFERENCE_NUMBER,
]


class Display(StrEnum):
    """Options for displaying /search results."""

    LIST = "list"
    GRID = "grid"


# Advanced search input limits
ADV_SEARCH_TEXTAREA_MAX_CHARS = 2000
ADV_SEARCH_TEXTAREA_MAX_LINES = 200


# Manorial Documents Register (MDR) search
# TODO: backend - confirm the canonical list of historic counties. These values
# match the options in the Discovery MDR search (/manor-search).
MDR_HISTORIC_COUNTIES = [
    "Anglesey",
    "Bedfordshire",
    "Berkshire",
    "Brecknockshire",
    "Buckinghamshire",
    "Caernarfonshire",
    "Cambridgeshire",
    "Cardiganshire",
    "Carmarthenshire",
    "Cheshire",
    "Cornwall",
    "Cumberland",
    "Denbighshire",
    "Derbyshire",
    "Devon",
    "Dorset",
    "Durham",
    "Essex",
    "Flintshire",
    "Glamorgan",
    "Gloucestershire",
    "Hampshire",
    "Herefordshire",
    "Hertfordshire",
    "Huntingdonshire",
    "Isle of Wight",
    "Kent",
    "Lancashire",
    "Leicestershire",
    "Lincolnshire",
    "Merioneth",
    "Middlesex",
    "Monmouthshire",
    "Montgomeryshire",
    "Norfolk",
    "Northamptonshire",
    "Northumberland",
    "Nottinghamshire",
    "Oxfordshire",
    "Pembrokeshire",
    "Radnorshire",
    "Rutland",
    "Shropshire",
    "Somerset",
    "Staffordshire",
    "Suffolk",
    "Surrey",
    "Sussex",
    "Warwickshire",
    "Westmorland",
    "Wiltshire",
    "Worcestershire",
    "Yorkshire, East Riding",
    "Yorkshire, North Riding",
    "Yorkshire, West Riding",
]

MDR_COUNTRIES = ["England", "Wales"]

# MDR search API filters and aggregations
MDR_API_FILTERS = ["schema:manor"]  # limits results to manors
MDR_API_FILTER_COUNTY = "country"  # the country field includes counties
MDR_API_FILTER_COUNTRY = "country"
MDR_API_AGGS_COUNTRY = "country"
MDR_API_FILTER_START_DATE = "startDate"
MDR_API_FILTER_END_DATE = "endDate"
# TODO: backend - parish filter is not yet supported by the API
MDR_API_FILTER_PARISH = "parish"
