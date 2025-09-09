from unittest.mock import patch

import responses
from app.search.api import search_records
from app.search.models import APISearchResponse
from django.conf import settings
from django.test import TestCase


class SearchRecordsSubjectsTests(TestCase):
    """Tests for subjects integration in search API calls."""

    @responses.activate
    def test_search_records_with_subjects_aggregation(self):
        """Test that subjects aggregation is included in API response."""

        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [{"@template": {"details": {"iaid": "C198022"}}}],
                "aggregations": [
                    {
                        "name": "subjects",
                        "entries": [
                            {"value": "2", "doc_count": 150},
                            {"value": "6", "doc_count": 75},
                            {"value": "18", "doc_count": 50},
                        ],
                    }
                ],
                "buckets": [
                    {
                        "name": "group",
                        "entries": [
                            {"value": "tna", "count": 1},
                        ],
                    }
                ],
                "stats": {
                    "total": 1,
                    "results": 1,
                },
            },
            status=200,
        )

        api_results = search_records(query="military")

        self.assertIsInstance(api_results, APISearchResponse)
        self.assertEqual(len(api_results.aggregations), 1)

        subjects_aggregation = api_results.aggregations[0]
        self.assertEqual(subjects_aggregation["name"], "subjects")
        self.assertEqual(len(subjects_aggregation["entries"]), 3)

        # Check specific subject entries
        entries = subjects_aggregation["entries"]
        self.assertEqual(entries[0]["value"], "2")
        self.assertEqual(entries[0]["doc_count"], 150)
        self.assertEqual(entries[1]["value"], "6")
        self.assertEqual(entries[1]["doc_count"], 75)

    @responses.activate
    def test_search_records_with_subjects_filter_params(self):
        """Test that subjects filter parameters are passed correctly to API."""

        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [{"@template": {"details": {"iaid": "C198022"}}}],
                "aggregations": [],
                "buckets": [
                    {
                        "name": "group",
                        "entries": [
                            {"value": "tna", "count": 1},
                        ],
                    }
                ],
                "stats": {
                    "total": 1,
                    "results": 1,
                },
            },
            status=200,
        )

        # Test with subjects filter parameters
        params = {
            "filter": ["group:tna", "subjects:2", "subjects:6"],
            "aggs": ["level", "collection", "subjects"],
        }

        api_results = search_records(query="military", params=params)

        self.assertIsInstance(api_results, APISearchResponse)

        # Verify the request was made with correct parameters
        self.assertEqual(len(responses.calls), 1)
        request_url = responses.calls[0].request.url

        # Check that subjects filters are in the URL
        self.assertIn("filter=subjects%3A2", request_url)
        self.assertIn("filter=subjects%3A6", request_url)
        self.assertIn("aggs=subjects", request_url)

    @responses.activate
    def test_search_records_with_empty_subjects_aggregation(self):
        """Test handling of empty subjects aggregation."""

        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [{"@template": {"details": {"iaid": "C198022"}}}],
                "aggregations": [
                    {
                        "name": "subjects",
                        "entries": [],
                    }
                ],
                "buckets": [
                    {
                        "name": "group",
                        "entries": [
                            {"value": "tna", "count": 1},
                        ],
                    }
                ],
                "stats": {
                    "total": 1,
                    "results": 1,
                },
            },
            status=200,
        )

        api_results = search_records(query="rare_topic")

        self.assertIsInstance(api_results, APISearchResponse)
        self.assertEqual(len(api_results.aggregations), 1)

        subjects_aggregation = api_results.aggregations[0]
        self.assertEqual(subjects_aggregation["name"], "subjects")
        self.assertEqual(len(subjects_aggregation["entries"]), 0)

    @responses.activate
    def test_search_records_multiple_aggregations_including_subjects(self):
        """Test that subjects aggregation works alongside other aggregations."""

        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [{"@template": {"details": {"iaid": "C198022"}}}],
                "aggregations": [
                    {
                        "name": "level",
                        "entries": [
                            {"value": "Item", "doc_count": 100},
                        ],
                    },
                    {
                        "name": "collection",
                        "entries": [
                            {"value": "BT", "doc_count": 50},
                        ],
                    },
                    {
                        "name": "subjects",
                        "entries": [
                            {"value": "2", "doc_count": 25},
                            {"value": "7", "doc_count": 15},
                        ],
                    },
                ],
                "buckets": [
                    {
                        "name": "group",
                        "entries": [
                            {"value": "tna", "count": 1},
                        ],
                    }
                ],
                "stats": {
                    "total": 1,
                    "results": 1,
                },
            },
            status=200,
        )

        api_results = search_records(query="test")

        self.assertIsInstance(api_results, APISearchResponse)
        self.assertEqual(len(api_results.aggregations), 3)

        # Check all aggregations are present
        aggregation_names = [agg["name"] for agg in api_results.aggregations]
        self.assertIn("level", aggregation_names)
        self.assertIn("collection", aggregation_names)
        self.assertIn("subjects", aggregation_names)

        # Check subjects aggregation specifically
        subjects_agg = next(
            agg for agg in api_results.aggregations if agg["name"] == "subjects"
        )
        self.assertEqual(len(subjects_agg["entries"]), 2)
        self.assertEqual(subjects_agg["entries"][0]["value"], "2")
        self.assertEqual(subjects_agg["entries"][0]["doc_count"], 25)


class SubjectsAPIIntegrationTests(TestCase):
    """Integration tests for subjects functionality with API calls."""

    @patch("app.lib.api.logger")
    @responses.activate
    def test_catalogue_view_subjects_api_params(self, mock_logger):
        """Test that subjects parameters are correctly passed to API."""

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
                "aggregations": [
                    {
                        "name": "subjects",
                        "entries": [
                            {"value": "2", "doc_count": 100},
                        ],
                    }
                ],
                "buckets": [
                    {
                        "name": "group",
                        "entries": [
                            {"value": "tna", "count": 1},
                        ],
                    }
                ],
                "stats": {
                    "total": 1,
                    "results": 1,
                },
            },
            status=200,
        )

        # Test API call with subjects filter
        response = self.client.get("/catalogue/search/?subjects=2&subjects=6")
        self.assertEqual(response.status_code, 200)

        # Check that the API was called with correct subjects filters
        logged_url = mock_logger.debug.call_args[0][0]
        self.assertIn("filter=subjects%3A2", logged_url)
        self.assertIn("filter=subjects%3A6", logged_url)
        self.assertIn("aggs=subjects", logged_url)
