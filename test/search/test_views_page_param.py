from http import HTTPStatus
from unittest.mock import patch

import responses
from django.conf import settings
from django.test import TestCase
from django.utils.encoding import force_str

from app.search.constants import (
    PAGE_LIMIT,
    PAGE_LIMIT_WARNING_MESSAGE,
    PAGE_LIMIT_WARNING_THRESHOLD,
    RESULTS_PER_PAGE,
)


class CatalogueSearchViewInvalidPageNumberTests(TestCase):
    """Test invalid page number param values for catalogue search view."""

    def test_page_constants(self):
        """Test page related constants are as expected."""

        self.assertEqual(500, PAGE_LIMIT)
        self.assertEqual(20, RESULTS_PER_PAGE)

    def test_invalid_page_number_param_returns_404(self):
        """Test invalid page number param returns 404."""

        # test page number param less than 1 returns 404
        response = self.client.get("/catalogue/search/?page=0")
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)

        # test page number param is not an integer returns 404
        response = self.client.get("/catalogue/search/?page=ABC")
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)

    @patch("app.lib.api.logger")
    @responses.activate
    def test_requested_page_exceed_total_calc_pages_returns_404(self, mock_logger):
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


class CatalogueSearchViewValidPageNumberTests(TestCase):
    """Tests various parts related to page number when valid page number param is used
    for catalogue search view."""

    def setUp(self):
        self.maxDiff = None
        self.page_limit_warning = (
            "Only the first 10,000 results are shown, "
            "apply filters to narrow your search."
        )

    def test_page_constants(self):
        """Test page related constants are as expected."""

        self.assertEqual(500, PAGE_LIMIT)
        self.assertEqual(20, RESULTS_PER_PAGE)
        self.assertEqual(495, PAGE_LIMIT_WARNING_THRESHOLD)
        self.assertEqual(self.page_limit_warning, PAGE_LIMIT_WARNING_MESSAGE)

    @patch("app.lib.api.logger")
    @responses.activate
    def test_last_page_within_page_limit_and_page_warning_treshold(self, mock_logger):
        """Tests page related parts when page number equals to last page and has pages
        of records less than PAGE_LIMIT."""

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
                    "total": 698,
                    "results": 18,
                },
            },
            status=HTTPStatus.OK,
        )

        response = self.client.get("/catalogue/search/?q=ufo&page=35")

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
            "&from=680"
        )

        context_data = response.context_data

        # test pagination context data
        # 698 results / 20 results per page = 34.9 pages, so page=35 is the last page
        self.assertEqual(
            {
                "items": [
                    {"number": "1", "href": "?q=ufo&page=1", "current": False},
                    {"ellipsis": True},
                    {"number": "34", "href": "?q=ufo&page=34", "current": False},
                    {"number": "35", "href": "?q=ufo&page=35", "current": True},
                ],
                "previous": {
                    "href": "?q=ufo&page=34",
                    "title": "Previous page of results",
                },
            },
            context_data["pagination"],
        )
        self.assertEqual(35, context_data["page"])

        html = force_str(response.content)

        # test that the page limit warning is not shown for the last page of results
        # since it is below the PAGE_LIMIT_WARNING_THRESHOLD
        self.assertNotIn(self.page_limit_warning, html)

    @patch("app.lib.api.logger")
    @responses.activate
    def test_requesting_last_page_when_more_records_exist(self, mock_logger):
        """Tests page related parts when page number equals to PAGE_LIMIT and has pages
        of records more than PAGE_LIMIT."""

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
                            {"value": "tna", "count": 28024092},
                        ],
                    }
                ],
                "stats": {
                    "total": 28024092,  # more pages of records exist than PAGE_LIMIT, so last page is PAGE_LIMIT
                    "results": 20,
                },
            },
            status=HTTPStatus.OK,
        )

        response = self.client.get("/catalogue/search/?page=500")

        # test from param is calculated correctly for the last page of results
        mock_logger.debug.assert_called_with(
            "https://rosetta.test/data/search?"
            "filter=group%3Atna"
            "&aggs=level"
            "&aggs=collection"
            "&aggs=closure"
            "&aggs=subject"
            "&q=%2A"
            "&size=20"
            "&from=9980"
        )

        context_data = response.context_data

        # test pagination context data
        # more pages of records exist than PAGE_LIMIT, so last page is PAGE_LIMIT
        # 28024092 results / 20 results per page = 1401204.6 pages
        # Since 1401205 pages is greater than PAGE_LIMIT (500), pages = 500
        self.assertEqual(
            {
                "items": [
                    {"number": "1", "href": "?page=1", "current": False},
                    {"ellipsis": True},
                    {"number": "499", "href": "?page=499", "current": False},
                    {"number": "500", "href": "?page=500", "current": True},
                ],
                "previous": {"href": "?page=499", "title": "Previous page of results"},
            },
            context_data["pagination"],
        )
        self.assertEqual(500, context_data["page"])

        html = force_str(response.content)

        # test that the page limit warning is shown for the last page of results
        # since it is above the PAGE_LIMIT_WARNING_THRESHOLD
        self.assertIn(self.page_limit_warning, html)
