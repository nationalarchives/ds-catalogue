# Search Pagination Limitations

## Elasticsearch Result Limit

Elasticsearch has a hard limit of **10,000 results** per query. This is a known architectural constraint that prevents deep pagination queries for performance reasons.

### Implementation

To work within this constraint:

- **RESULTS_PER_PAGE**: 20 results per page
- **PAGE_LIMIT**: 500 pages maximum
- **Math**: 500 pages × 20 results/page = 10,000 results

See [app/search/constants.py](../../app/search/constants.py) for these constants.

### What Happens When Limits Are Hit

- **Invalid page number** (< 1, not an integer, or > PAGE_LIMIT): View raises `PageNotFound`, returns HTTP 404 immediately without querying the API.
- **Page beyond calculated total**: If results total fewer than 10,000, requesting a page beyond the calculated total also returns HTTP 404.
- **Very high page numbers** (e.g., 999,999,999): The guard in `CatalogueSearchView.page` property prevents the API call entirely, avoiding potential server errors.
