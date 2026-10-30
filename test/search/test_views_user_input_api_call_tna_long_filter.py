from http import HTTPStatus
from unittest.mock import patch

import responses
from django.conf import settings
from django.test import TestCase, override_settings


@override_settings(DEBUG=False)
class CatalogueSearchViewDebugAPILongFilterTnaBucketTests(TestCase):
    """Tests Long filter API calls (url) made by the catalogue search view for tna bucket/group."""

    @patch("app.lib.api.logger")
    @responses.activate
    def test_catalogue_long_filter_collection_debug_api(self, mock_logger):

        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                # "data": [],
                "aggregations": [
                    {
                        "name": "longCollection",
                        "entries": [
                            {"value": "somevalue", "doc_count": 100},
                        ],
                    },
                ],
                "buckets": [
                    {
                        "name": "group",
                        "entries": [
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

        # Test longCollection filter
        response = self.client.get("/catalogue/search/?filter_list=longCollection")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        mock_logger.debug.assert_called_with(
            "https://rosetta.test/data/search?"
            "filter=group%3Atna"
            "&aggs=longCollection"
            "&q=%2A"
            "&size=0"
        )

    @patch("app.lib.api.logger")
    @responses.activate
    def test_catalogue_long_filter_subject_debug_api(self, mock_logger):

        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "aggregations": [
                    {
                        "name": "longSubject",
                        "entries": [
                            {"value": "somevalue", "doc_count": 100},
                        ],
                    },
                ],
                "buckets": [
                    {
                        "name": "group",
                        "entries": [
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
