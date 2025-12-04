from app.records.models import Record
from app.search.models import APISearchResponse
from django.test import SimpleTestCase


class APISearchResponseTests(SimpleTestCase):
    maxDiff = None

    def test_api_search_response_default_values(self):

        self.api_results = {}

        self.api_search_response = APISearchResponse(self.api_results)

        self.assertIsInstance(self.api_search_response, APISearchResponse)
        self.assertEqual(len(self.api_search_response.records), 0)
        self.assertEqual(self.api_search_response.stats_total, 0)
        self.assertEqual(self.api_search_response.stats_results, 0)
        self.assertEqual(self.api_search_response.buckets, {})

    def test_api_search_response_attributes_with_empty_results_from_api(self):

        self.api_results = {
            "data": [],
            "buckets": [{"name": "group", "total": 0, "other": 0}],
            "stats": {
                "total": 0,
                "results": 0,
            },
        }

        self.api_search_response = APISearchResponse(self.api_results)

        self.assertIsInstance(self.api_search_response, APISearchResponse)
        self.assertEqual(len(self.api_search_response.records), 0)
        self.assertEqual(self.api_search_response.stats_total, 0)
        self.assertEqual(self.api_search_response.stats_results, 0)
        self.assertEqual(self.api_search_response.buckets, {})

    def test_api_search_response_attributes_with_results_from_api(self):

        self.api_results = {
            "data": [
                {
                    "@template": {
                        "details": {
                            "id": "C11175621",
                        }
                    }
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
                "total": 26008838,
                "results": 20,
            },
        }

        self.api_search_response = APISearchResponse(self.api_results)

        self.assertIsInstance(self.api_search_response, APISearchResponse)

        self.assertEqual(len(self.api_search_response.records), 1)
        self.assertIsInstance(self.api_search_response.records[0], Record)

        self.assertEqual(self.api_search_response.stats_total, 26008838)

        self.assertEqual(self.api_search_response.stats_results, 20)

        self.assertEqual(self.api_search_response.buckets, {"tna": 1})
