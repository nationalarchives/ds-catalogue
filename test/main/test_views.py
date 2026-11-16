from http import HTTPStatus
from unittest.mock import patch

import responses
from django.conf import settings
from django.core.cache import cache
from django.test import TestCase


class CatalogueViewTests(TestCase):
    """Tests url routing, response codes, context data for the catalogue view."""

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    @responses.activate
    @patch("app.main.views.fetch_global_notifications", return_value=None)
    @patch("app.main.views.get_explore_the_collection", return_value={})
    def test_catalogue_view(
        self,
        mock_get_explore_the_collection,
        mock_fetch_global_notifications,
    ):

        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [],
                "errors": [],
                "aggregations": [
                    {
                        "name": "longSubject",
                        "entries": [
                            # unordered on purpose to test sorting
                            {
                                "value": "NURSING",
                                "doc_count": 75,
                            },
                            {
                                "value": "CONFLICT",
                                "doc_count": 50,
                            },
                            {
                                "value": "NAVY",
                                "doc_count": 100,
                            },
                            {
                                "value": "CRIME",
                                "doc_count": 200,
                            },
                        ],
                    }
                ],
                "stats": {
                    "total": 28024092,
                    "results": 0,
                    "providers": 1,
                    "latency": 31,
                },
                "buckets": [
                    {
                        "name": "group",
                        "entries": [
                            {"value": "tna", "count": 28024092},
                        ],
                    }
                ],
            },
            status=HTTPStatus.OK,
        )

        # get response
        response = self.client.get("/catalogue/")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        context_data = response.context_data

        # test that the API was called the expected number of times
        self.assertEqual(len(responses.calls), 1)

        # test that the API was called with the expected URL
        url = responses.calls[0].request.url
        self.assertEqual(
            "https://rosetta.test/data/search?filter=group%3Atna&aggs=longSubject&q=%2A&size=0",
            url,
        )

        # test that the context contains the expected data
        expected_subjects_grouped_by_letter = {
            "C": ["CONFLICT", "CRIME"],
            "N": ["NAVY", "NURSING"],
        }
        self.assertEqual(
            context_data.get("subjects_grouped_by_letter"),
            expected_subjects_grouped_by_letter,
        )
