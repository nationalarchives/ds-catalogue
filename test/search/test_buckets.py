import copy

from app.search.buckets import CATALOGUE_BUCKETS, Aggregation, BucketKeys
from app.search.models import APISearchResponse
from django.test import TestCase


class TestBuckets(TestCase):

    def setUp(self):

        self.api_results = {
            "data": [
                {
                    "@template": {
                        "details": {
                            "iaid": "C11175621",
                        }
                    }
                }
            ],
            "buckets": [
                {
                    "name": "group",
                    "entries": [
                        {"value": "record", "count": 37470380},
                        {"value": "tna", "count": 26008838},
                        {"value": "nonTna", "count": 16454377},
                        {"value": "digitised", "count": 9055592},
                        {"value": "medalCard", "count": 5481173},
                        {"value": "will", "count": 1016334},
                        {"value": "aggregation", "count": 763209},
                        {"value": "seamenRegister", "count": 684424},
                        {"value": "britishWarMedal", "count": 157424},
                        {"value": "navalReserve", "count": 137920},
                        {"value": "archive", "count": 3587},
                    ],
                    "total": 97233258,
                    "other": 0,
                }
            ],
            "stats": {
                "total": 26008838,
                "results": 20,
            },
        }

        self.buckets = APISearchResponse(self.api_results).buckets
        self.bucket_list = copy.deepcopy(CATALOGUE_BUCKETS)

    def test_bucket_items_without_query(self):

        query = ""

        test_data = (
            (
                # label
                "TNA",
                # current bucket key
                BucketKeys.TNA,
                # expected CATALOGUE buckets with current status
                [
                    {
                        "name": "Records at the National Archives (26,008,838)",
                        "href": "?group=tna",
                        "current": True,
                    },
                    {
                        "name": "Records at other UK archives (16,454,377)",
                        "href": "?group=nonTna",
                        "current": False,
                    },
                ],
            ),
        )

        for label, current_bucket_key, expected in test_data:
            with self.subTest(label):
                self.bucket_list.update_buckets_for_display(
                    query=query,
                    buckets=self.buckets,
                    current_bucket_key=current_bucket_key,
                )

                self.assertListEqual(self.bucket_list.items, expected)

    def test_bucket_items_with_query(self):

        self.bucket_list.update_buckets_for_display(
            query="ufo",
            buckets=self.buckets,
            current_bucket_key=BucketKeys.TNA,
        )

        self.assertListEqual(
            self.bucket_list.items,
            [
                {
                    "name": "Records at the National Archives (26,008,838)",
                    "href": "?group=tna&q=ufo",
                    "current": True,
                },
                {
                    "name": "Records at other UK archives (16,454,377)",
                    "href": "?group=nonTna&q=ufo",
                    "current": False,
                },
            ],
        )


class SubjectsBucketsTests(TestCase):
    """Tests for subjects integration in buckets configuration."""

    def test_subjects_aggregation_exists(self):
        """Test that SUBJECTS aggregation is defined."""
        self.assertEqual(Aggregation.SUBJECTS, "subjects")
        self.assertIn("subjects", [agg.value for agg in Aggregation])

    def test_tna_bucket_includes_subjects_aggregation(self):
        """Test that TNA bucket includes subjects in its aggregations."""
        tna_bucket = CATALOGUE_BUCKETS.get_bucket(BucketKeys.TNA.value)

        self.assertIn(Aggregation.SUBJECTS.value, tna_bucket.aggregations)

        # Check all expected aggregations are present
        expected_aggregations = [
            Aggregation.LEVEL.value,
            Aggregation.COLLECTION.value,
            Aggregation.SUBJECTS.value,
        ]

        for aggregation in expected_aggregations:
            self.assertIn(aggregation, tna_bucket.aggregations)

    def test_non_tna_bucket_does_not_include_subjects(self):
        """Test that non-TNA bucket doesn't include subjects aggregation."""
        non_tna_bucket = CATALOGUE_BUCKETS.get_bucket(BucketKeys.NON_TNA.value)

        # Non-TNA bucket should not have any aggregations including subjects, except for heldBy
        self.assertEqual(non_tna_bucket.aggregations, ["heldBy"])

    def test_all_aggregation_values_are_strings(self):
        """Test that all aggregation enum values are strings."""
        for aggregation in Aggregation:
            self.assertIsInstance(aggregation.value, str)

        # Test specific values
        self.assertEqual(Aggregation.LEVEL.value, "level")
        self.assertEqual(Aggregation.COLLECTION.value, "collection")
        self.assertEqual(Aggregation.SUBJECTS.value, "subjects")

    def test_tna_bucket_aggregations_order(self):
        """Test that aggregations are in expected order."""
        tna_bucket = CATALOGUE_BUCKETS.get_bucket(BucketKeys.TNA.value)

        expected_order = ["level", "collection", "subjects"]

        self.assertEqual(tna_bucket.aggregations, expected_order)
