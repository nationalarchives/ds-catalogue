from http import HTTPStatus
from unittest.mock import patch

import responses
from django.conf import settings
from django.test import TestCase

from app.search.constants import (
    PAGE_LIMIT,
    RESULTS_PER_PAGE,
)


class CatalogueSearchViewInvalidPageNumberTests(TestCase):
    """Test invalid page number param values for catalogue search view."""

    def test_page_constants(self):
        """Test page related constants are as expected."""

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

    @patch("app.lib.api.logger")
    @responses.activate
    def test_requested_pages_exceed_total_calc_pages_returns_404(self, mock_logger):
        """Test page number param greater than calculated total pages returns 404.
        This page number is less than the PAGE_LIMIT, so the API is called to get
        the total records available for the query, which is used to calculate total
        pages."""

        # test queried search page number param greater than calculated total pages returns 404
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [],  # no data returned, as page 36 exceeds total pages
                "aggregations": [],
                "buckets": [
                    {
                        "name": "group",
                        "entries": [
                            {"value": "tna", "count": 698},
                        ],
                    }
                ],
                "stats": {
                    "total": 698,  # total records available for the query, which is used to calculate total pages
                    "results": 0,  # 0 results returned for this page, as page 36 exceeds total pages
                },
            },
            status=HTTPStatus.OK,
        )

        # Because page 36 is below PAGE_LIMIT, the API is queried for the total result count.
        # With 698 total results and 20 per page, there are 35 pages in total.
        # Requesting page 36 therefore exceeds the available pages and should return 404.
        response = self.client.get("/catalogue/search/?q=ufo&page=36")
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)

        # test from param is calculated correctly for the last page of results
        mock_logger.debug.assert_called_with(
            "https://rosetta.test/data/search?"
            "filter=group%3Atna"
            "&aggs=level"
            "&aggs=collection"
            "&aggs=closure"
            "&aggs=subject"
            "&q=ufo"
            "&size=20"
            "&from=700"
        )

    @responses.activate
    def test_requested_page_above_page_limit_returns_404(self):
        """Test page number param greater than PAGE_LIMIT returns 404."""

        # page number just above PAGE_LIMIT e.g. 501
        # bypasses calling the API and raises PageNotFound,
        # so no mock response is registered.
        response = self.client.get("/catalogue/search/?page=501")
        self.assertEqual(
            HTTPStatus.NOT_FOUND,
            response.status_code,
            msg=f"Expected 404 for page=501, got {response.status_code} instead.",
        )
