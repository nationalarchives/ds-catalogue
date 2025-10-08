from unittest.mock import patch

import responses
from app.search.api import search_records
from app.search.models import APISearchResponse
from django.conf import settings
from django.test import TestCase


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
