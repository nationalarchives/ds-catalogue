from app.lib.api import ResourceNotFound, rosetta_request_handler

from .models import APISearchResponse


def search_records(
    query, results_per_page=12, page=1, sort="", order="asc", params={}
) -> APISearchResponse:
    """
    Prepares the api url for the requested data and calls the handler.
    Raises error on invalid response or invalid result.

    sort: date:[asc|desc]; title:[asc|desc]
    params: filter, aggregation, etc
    The errors are handled by a custom middleware in the app.
    """
    uri = "search"
    params.update(
        {
            "q": query or "*",
            "size": results_per_page,
            "from": (page - 1) * results_per_page,
            "sort": sort,
            # "sortOrder": order, # Unused for Rosetta
        }
    )
    # remove params having no values
    params = {param: value for param, value in params.items() if value}

    results = rosetta_request_handler(uri, params)
    if "data" not in results:
        raise Exception("No data returned")
    if "buckets" not in results:
        raise Exception("No 'buckets' returned")
    if not len(results["data"]) and page == 1:
        raise ResourceNotFound("No results found")
    return APISearchResponse(results)
