from app.lib.api import ResourceNotFound, rosetta_request_handler

from .buckets import CATALOGUE_BUCKETS
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
            "sort": sort,
            # "sortOrder": order, # Unused for Rosetta
        }
    )

    # Add from only when results_per_page > 0,
    # for long filters with size=0, its not required
    if results_per_page > 0:
        params["from"] = ((page - 1) * results_per_page,)

    # remove params having empty values, for long filters size=0 is valid
    params = {
        param: value
        for param, value in params.items()
        if value not in [None, "", []]
    }

    results = rosetta_request_handler(uri, params)
    if "data" not in results:
        raise Exception("No data returned")
    if "buckets" not in results:
        raise Exception("No 'buckets' returned")
    if not len(results["data"]) and page == 1:
        """
        Raises error when "data" is not found and when all "buckets"
        counts are zero.

        "data" is empty, possible reasons:
        1. when search api is queried on "q" results in no matches.
        2. when search api is queried other than "q" e.g. "collection",
        "level", "held_by", etc. results in no matches.
        In both cases, "buckets" cound have counts or not.
        Buckets counts depend on the "q" param.
        """
        has_config_bucket_entries = False
        for bucket in results["buckets"]:
            if bucket.get("name", "") == "group":
                if len(bucket.get("entries", [])) > 0:
                    for entry in bucket.get("entries", []):
                        # check if at least one configured bucket has count
                        if entry.get("value", "") in [
                            bucket.key for bucket in CATALOGUE_BUCKETS
                        ]:
                            if entry.get("count", 0) > 0:
                                has_config_bucket_entries = True
                                break
        if not has_config_bucket_entries:
            raise ResourceNotFound("No results found")
    return APISearchResponse(results)
