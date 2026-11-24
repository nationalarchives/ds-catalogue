from http import HTTPStatus

import responses
from django.conf import settings
from django.core.cache import cache
from django.test import TestCase

from app.main.cache import get_all_collection_choices
from app.search.collection_names import COLLECTION_NAMES


class AllCollectionChoicesTests(TestCase):
    """Tests for getting all collection choices."""

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_collection_names_length(self):
        """Test that the length of COLLECTION_NAMES is as expected."""
        self.assertEqual(len(COLLECTION_NAMES), 677)

    @responses.activate
    def test_get_all_collection_choices(self):
        """Tests the build and caching of all collection choices."""

        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
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
                "aggregations": [
                    {
                        "name": "longCollection",
                        "total": 1000,
                        "other": 0,
                        "entries": [
                            {"value": "Y", "doc_count": 100},
                            {"value": "LEV", "doc_count": 10},
                            {"value": "ADM", "doc_count": 10},
                            {"value": "BT", "doc_count": 10},
                            {"value": "WO", "doc_count": 10},
                            {"value": "HO", "doc_count": 10},
                            {"value": "E", "doc_count": 10},
                            {"value": "C", "doc_count": 10},
                            {"value": "AIR", "doc_count": 10},
                            {"value": "GTI", "doc_count": 10},
                            {"value": "RAIL", "doc_count": 10},
                            {"value": "YHL", "doc_count": 10},
                            {"value": "YBBK", "doc_count": 10},
                            {"value": "YHNN", "doc_count": 10},
                            {"value": "YFLS", "doc_count": 10},
                            {"value": "YHEA", "doc_count": 10},
                            {"value": "YWAR", "doc_count": 10},
                            {"value": "YBAL", "doc_count": 10},
                            {"value": "YBLU", "doc_count": 10},
                            {"value": "YOWE", "doc_count": 10},
                            {"value": "YLG", "doc_count": 10},
                            {"value": "YBLK", "doc_count": 10},
                            {
                                "value": "UNCONFIGNEWCOLLECTION",
                                "doc_count": 10,
                            },  # unconfigured new collection
                        ],
                        "Y": {"name": "Y", "total": 100},
                    }
                ],
            },
            status=HTTPStatus.OK,
        )

        with self.assertLogs(
            "app.search.parliamentary_archives", level="WARNING"
        ) as lc:
            self.assertIsNone(cache.get("COLLECTION_CHOICES"))
            # Trigger the cache by calling get_all_collection_choices()
            # includes configured and unconfigured collections
            all_collection_choices = get_all_collection_choices()

        self.assertCountEqual(
            [
                "WARNING:app.search.parliamentary_archives:Missing collection values in API data [5+]: ['A', 'AB', 'ACE', 'ACT', 'AE']",
                "WARNING:app.search.parliamentary_archives:Missing API values not present in the configured collection names [5+]: ['UNCONFIGNEWCOLLECTION']",
            ],
            lc.output,
        )

        # check returned collection choices

        self.assertEqual(len(all_collection_choices), 678)
        # Check a configured collection, not part of data returned by the API, is included in the choices
        self.assertIn(("A", "A - Alienation Office"), all_collection_choices)
        # Check another configured collection that is also included by the API is included in the choices
        self.assertIn(("Y", "Y - UK Parliament"), all_collection_choices)
        # Check that the unconfigured new collection is included in the choices
        self.assertIn(
            ("UNCONFIGNEWCOLLECTION", "UNCONFIGNEWCOLLECTION"), all_collection_choices
        )

        # Check that the collections are cached
        cached_collection_choices = cache.get("COLLECTION_CHOICES")

        self.assertEqual(len(cached_collection_choices), 678)
        self.assertIn(("A", "A - Alienation Office"), cached_collection_choices)
        self.assertIn(("Y", "Y - UK Parliament"), cached_collection_choices)
        self.assertIn(
            ("UNCONFIGNEWCOLLECTION", "UNCONFIGNEWCOLLECTION"),
            cached_collection_choices,
        )

    @responses.activate
    def test_get_all_collection_choices_raises_error_invalid_api_response(self):
        """Test that get_all_collection_choices raises an error when the API response is invalid."""

        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
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
                "aggregations": [],
            },
            status=HTTPStatus.OK,
        )

        with self.assertRaisesMessage(Exception, "list index out of range"):
            with self.assertLogs("app.main.cache", level="ERROR") as lc:
                self.assertIsNone(cache.get("COLLECTION_CHOICES"))
                # Trigger the cache by calling get_all_collection_choices()
                # includes configured and unconfigured collections
                _ = get_all_collection_choices()

        self.assertIn(
            "ERROR:app.main.cache:Failed to fetch all Collections: list index out of range",
            lc.output,
        )

        # verify choices are not cached due to the invalid API response
        self.assertIsNone(cache.get("COLLECTION_CHOICES"))
