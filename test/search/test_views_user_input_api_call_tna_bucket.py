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
                        "name": "subjects",
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
        self.response = self.client.get("/catalogue/search/")
        self.assertEqual(self.response.status_code, HTTPStatus.OK)
        mock_logger.debug.assert_called_with(
            "https://rosetta.test/data/search?aggs=level&aggs=collection&aggs=closure&aggs=subject&filter=group%3Atna&q=%2A&size=20"
        )

        # with group=tna param
        self.response = self.client.get("/catalogue/search/?group=tna")
        self.assertEqual(self.response.status_code, HTTPStatus.OK)
        mock_logger.debug.assert_called_with(
            "https://rosetta.test/data/search?aggs=level&aggs=collection&aggs=closure&aggs=subject&filter=group%3Atna&q=%2A&size=20"
        )

        # query with held_by param (should be ignored for tna group)
        self.response = self.client.get(
            "/catalogue/search/?group=tna&held_by=somearchive"
        )
        self.assertEqual(self.response.status_code, HTTPStatus.OK)
        mock_logger.debug.assert_called_with(
            "https://rosetta.test/data/search?aggs=level&aggs=collection&aggs=closure&aggs=subject&filter=group%3Atna&q=%2A&size=20"
        )

        # Test subjects filter for TNA group
        self.response = self.client.get(
            "/catalogue/search/?group=tna&subject=Army&subject=Navy"
        )
        self.assertEqual(self.response.status_code, HTTPStatus.OK)
        mock_logger.debug.assert_called_with(
            "https://rosetta.test/data/search?aggs=level&aggs=collection&aggs=closure&aggs=subject&filter=group%3Atna&filter=subject%3AArmy&filter=subject%3ANavy&q=%2A&size=20"
        )
