from http import HTTPStatus
from unittest.mock import patch

import responses
from django.conf import settings
from django.test import TestCase


class CatalogueSearchViewDebugAPITnaBucketTests(TestCase):
    """Tests API calls (url) made by the catalogue search view for tna bucket/group."""

    @patch("app.lib.api.logger")
    @responses.activate
    def test_catalogue_debug_api(self, mock_logger):

        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [
                    {
                        "@template": {
                            "details": {
                                "iaid": "C123456",
                                "source": "CAT",
                            }
                        }
                    }
                ],
                # Note: api response is not checked for these values
                "aggregations": [
                    {
                        "name": "level",
                        "entries": [
                            {"value": "somevalue", "doc_count": 100},
                        ],
                    },
                    {
                        "name": "collection",
                        "entries": [
                            {"value": "somevalue", "doc_count": 100},
                        ],
                    },
                    {
                        "name": "subject",
                        "entries": [
                            {"value": "somevalue", "doc_count": 100},
                        ],
                    },
                ],
                "buckets": [
                    {
                        "name": "group",
                        "entries": [
                            # Note: api response is not checked for these values
                            {"value": "somevalue", "count": 1},
                        ],
                    }
                ],
                "stats": {
                    "total": 26008838,
                    "results": 20,
                },
            },
            status=HTTPStatus.OK,
        )

        # default query
        response = self.client.get("/catalogue/search/")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        mock_logger.debug.assert_called_with(
            "https://rosetta.test/data/search?"
            "filter=group%3Atna"
            "&aggs=level"
            "&aggs=collection"
            "&aggs=closure"
            "&aggs=subject"
            "&q=%2A"
            "&size=20"
            "&from=0"
        )

        # with group=tna param
        response = self.client.get("/catalogue/search/?group=tna")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        mock_logger.debug.assert_called_with(
            "https://rosetta.test/data/search?"
            "filter=group%3Atna"
            "&aggs=level"
            "&aggs=collection"
            "&aggs=closure"
            "&aggs=subject"
            "&q=%2A"
            "&size=20"
            "&from=0"
        )

        # query with held_by param (should be ignored for tna group)
        response = self.client.get(
            "/catalogue/search/?group=tna&held_by=somearchive"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        mock_logger.debug.assert_called_with(
            "https://rosetta.test/data/search?"
            "filter=group%3Atna"
            "&aggs=level"
            "&aggs=collection"
            "&aggs=closure"
            "&aggs=subject"
            "&q=%2A"
            "&size=20"
            "&from=0"
        )

        # Test subject filter for TNA group
        response = self.client.get(
            "/catalogue/search/?group=tna" "&subject=Army" "&subject=Navy"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        mock_logger.debug.assert_called_with(
            "https://rosetta.test/data/search?"
            "filter=group%3Atna"
            "&filter=subject%3AArmy"
            "&filter=subject%3ANavy"
            "&aggs=level"
            "&aggs=collection"
            "&aggs=closure"
            "&aggs=subject"
            "&q=%2A"
            "&size=20"
            "&from=0"
        )

        # Test covering date filters
        response = self.client.get(
            "/catalogue/search/?"
            "covering_date_from-year=2000"
            "&covering_date_from-month=12"
            "&covering_date_from-day=1"
            "&covering_date_to-year=2000"
            "&covering_date_to-month=12"
            "&covering_date_to-day=31"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        mock_logger.debug.assert_called_with(
            "https://rosetta.test/data/search?"
            "filter=group%3Atna"
            "&filter=coveringFromDate%3A%28%3E%3D2000-12-1%29"
            "&filter=coveringToDate%3A%28%3C%3D2000-12-31%29"
            "&aggs=level"
            "&aggs=collection"
            "&aggs=closure"
            "&aggs=subject"
            "&q=%2A"
            "&size=20"
            "&from=0"
        )

        # Test opening date filters
        response = self.client.get(
            "/catalogue/search/?"
            "opening_date_from-year=2000"
            "&opening_date_from-month=12"
            "&opening_date_from-day=1"
            "&opening_date_to-year=2000"
            "&opening_date_to-month=12"
            "&opening_date_to-day=31"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        mock_logger.debug.assert_called_with(
            "https://rosetta.test/data/search?"
            "filter=group%3Atna"
            "&filter=openingFromDate%3A%28%3E%3D2000-12-1%29"
            "&filter=openingToDate%3A%28%3C%3D2000-12-31%29"
            "&aggs=level&aggs=collection"
            "&aggs=closure"
            "&aggs=subject"
            "&q=%2A"
            "&size=20"
            "&from=0"
        )

        # Test longCollection filter
        response = self.client.get(
            "/catalogue/search/?filter_list=longCollection"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        mock_logger.debug.assert_called_with(
            "https://rosetta.test/data/search?"
            "filter=group%3Atna"
            "&aggs=longCollection"
            "&q=%2A"
            "&size=0"
        )

        # Test longSubject filter
        response = self.client.get("/catalogue/search/?filter_list=longSubject")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        mock_logger.debug.assert_called_with(
            "https://rosetta.test/data/search?"
            "filter=group%3Atna"
            "&aggs=longSubject"
            "&q=%2A"
            "&size=0"
        )

        # Test online filter (digitised parameter)
        response = self.client.get("/catalogue/search/?group=tna&online=true")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        actual_url = mock_logger.debug.call_args[0][0]

        self.assertIn("digitised=true", actual_url)

        self.assertNotIn("filter=digitised", actual_url)
        self.assertNotIn("digitised%3Atrue", actual_url)  # URL encoded version

        # Test online filter with other filters combined
        response = self.client.get(
            "/catalogue/search/?group=tna&online=true&q=test&level=Item"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        actual_url = mock_logger.debug.call_args[0][0]
        self.assertIn("digitised=true", actual_url)
        self.assertIn("filter=level%3AItem", actual_url)  # level as filter
        self.assertNotIn("filter=digitised", actual_url)  # NOT as filter

        # Test that online filter is NOT applied when online=false or not specified
        response = self.client.get("/catalogue/search/?group=tna&q=test")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        actual_url = mock_logger.debug.call_args[0][0]
        # digitised parameter should NOT be in the URL
        self.assertNotIn("digitised", actual_url)
