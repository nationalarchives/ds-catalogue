from http import HTTPStatus

import responses
from django.conf import settings
from django.test import TestCase

from app.search.constants import PAGE_LIMIT, RESULTS_PER_PAGE


class CatalogueSearchViewInvalidPageNumberTests(TestCase):
    """Test invalid page number param values for catalogue search view."""

    @responses.activate
    def test_page_constants(self):
        """Tests page limit and results per page constants are as expected."""

        self.assertEqual(500, PAGE_LIMIT)
        self.assertEqual(20, RESULTS_PER_PAGE)

    @responses.activate
    def test_search_with_invalid_page_number_param_returns_404(self):
        """Test invalid page number param returns 404."""

        # test page number param less than 1 returns 404
        response = self.client.get("/catalogue/search/?page=0")
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)

        # test page number param is not an integer returns 404
        response = self.client.get("/catalogue/search/?page=ABC")
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)

    @responses.activate
    def test_search_with_queried_results_and_page_number_param_returns_404(self):
        """Test page number param greater than calculated total pages returns 404."""

        # test queried search page number param greater than calculated total pages returns 404
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [
                    {
                        "@template": {
                            "details": {
                                "id": "C123456",
                                "source": "CAT",
                            }
                        }
                    }
                ],
                "aggregations": [
                    {
                        "name": "level",
                        "entries": [
                            {"value": "Lettercode", "doc_count": 100},
                        ],
                        "total": 100,
                        "other": 0,
                    }
                ],
                "buckets": [
                    {
                        "name": "group",
                        "entries": [
                            {"value": "tna", "count": 698},
                        ],
                    }
                ],
                "stats": {
                    # total results for this query, with 20 results per page,
                    # gives 35 pages, so page=36 should return 404
                    "total": 698,
                    "results": 0,
                },
            },
            status=HTTPStatus.OK,
        )
        # test page more than calculated total pages (35) returns 404
        response = self.client.get("/catalogue/search/?q=ufo&page=36")
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)

    @responses.activate
    def test_search_without_queried_results_above_page_limit_returns_404(self):
        """Test page number param greater than PAGE_LIMIT returns 404."""

        # test page number param greater than PAGE_LIMIT returns 404
        # When page=501 is queried, the API is queried from 9980 to 10000,
        # which is the last 20 results (RESULTS_PER_PAGE) of the first 10,000 results,
        # so the API returns 0 results
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [],
                "aggregations": [],
                "buckets": [
                    {
                        "name": "group",
                        "entries": [
                            {"value": "tna", "count": 28024092},
                        ],
                    }
                ],
                "stats": {
                    "total": 0,
                    "results": 0,
                },
            },
            status=HTTPStatus.OK,
        )
        response = self.client.get("/catalogue/search/?page=501")
        self.assertEqual(
            HTTPStatus.NOT_FOUND,
            response.status_code,
            msg=f"Expected 404 for page=501, got {response.status_code} instead.",
        )

        # clear responses to avoid interference with next test
        responses.reset()

        # A higher input page number e.g. 999999999 would cause the API
        # to return HTTP 400:
        # {"status": "Bad Request",
        #  "status_code": 400,
        #  "message": "Cannot parse integer from query string parameter 'from'
        #              with value '19999999960'"}
        # The view raises PageNotFound before querying the API, so no mock response is registered.
        # If PageNotFound were not raised, responses would raise a APIBadRequestError here.
        response = self.client.get("/catalogue/search/?page=999999999")
        self.assertEqual(
            HTTPStatus.NOT_FOUND,
            response.status_code,
            msg=f"Expected 404 for page=999999999, got {response.status_code} instead.",
        )
