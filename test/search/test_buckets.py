import copy

from app.search.buckets import CATALOGUE_BUCKETS, Aggregation, BucketKeys
from app.search.constants import FieldsConstant
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


class TestEnumChoices(TestCase):

    def test_bucket_keys_enum_choices(self):
        expected_choices = [
            (BucketKeys.TNA.value, "Records at the National Archives"),
            (BucketKeys.NON_TNA.value, "Records at other UK archives"),
        ]

        self.assertListEqual(
            CATALOGUE_BUCKETS.as_choices(),
            expected_choices,
        )

    def test_aggregation_enum_long_aggs_choices(self):
        """Test that the Aggregation enum returns the expected choices for long aggs."""

        expected_choices = [
            ("", "No filter"),
            ("longCollection", "collection"),
            ("longHeldBy", "held_by"),
            ("longSubject", "subject"),
        ]

        self.assertListEqual(
            Aggregation.as_input_choices_for_long_aggs(),
            expected_choices,
        )

    def test_get_field_name_from_aggregation_enum(self):
        """Test that the Aggregation enum returns the expected field name for long aggs."""

        test_data = (
            (
                # label
                "Collection",
                # config long_aggs value
                "longCollection",
                # expected value
                FieldsConstant.COLLECTION,
            ),
            (
                # label
                "Held By",
                # config long_aggs value
                "longHeldBy",
                # expected value
                FieldsConstant.HELD_BY,
            ),
            (
                # label
                "Subject",
                # config long_aggs value
                "longSubject",
                # expected value
                FieldsConstant.SUBJECT,
            ),
            (
                # label
                "Level (no long aggs)",
                # config long_aggs value
                "",
                # expected value
                None,
            ),
            (
                # label
                "Closure (no long aggs)",
                # config long_aggs value
                "",
                # expected value
                None,
            ),
            (
                # label
                "NOT-CONFIGURED-OR-UNKNOWN",
                # unknown long_aggs value or not configured
                "NOT-CONFIGURED-OR-UNKNOWN",
                # expected value
                None,
            ),
        )

        for label, aggs_name, expected_value in test_data:
            with self.subTest(label):
                field_name = Aggregation.get_field_name_for_long_aggs_name(
                    aggs_name
                )
                self.assertEqual(field_name, expected_value)

    def test_get_aggregation_enum_from_field_name(self):
        """Test that the Aggregation enum returns the expected long aggs name for field name."""

        test_data = (
            (
                # label
                "Collection",
                # field
                FieldsConstant.COLLECTION,
                # expected value
                "longCollection",
            ),
            (
                # label
                "Held By",
                # field
                FieldsConstant.HELD_BY,
                # expected value
                "longHeldBy",
            ),
            (
                # label
                "Subject",
                # field
                FieldsConstant.SUBJECT,
                # expected value
                "longSubject",
            ),
        )

        for label, field_name, expected_value in test_data:
            with self.subTest(label):
                long_aggs = Aggregation.get_long_aggs_name_for_field_name(
                    field_name
                )
                self.assertEqual(long_aggs, expected_value)

    def test_get_aggregation_enum_from_field_name_for_none_returns(self):
        """Test that the Aggregation enum returns None for long aggs name
        when field name has no long aggs configured or does not exist.
        """

        test_data = (
            (
                # label
                "Level",
                # field
                FieldsConstant.LEVEL,
                # expected value
                None,
                # expected log message
                "WARNING:app.search.buckets:Long aggregation name not found for field name: level",
            ),
            (
                # label
                "Closure",
                # field
                FieldsConstant.CLOSURE,
                # expected value
                None,
                # expected log message
                "WARNING:app.search.buckets:Long aggregation name not found for field name: closure",
            ),
            (
                # label
                "NOT-CONFIGURED-OR-UNKNOWN",
                # field
                "NOT-CONFIGURED-OR-UNKNOWN",
                # expected value
                None,
                # expected log message
                "WARNING:app.search.buckets:Long aggregation name not found for field name: NOT-CONFIGURED-OR-UNKNOWN",
            ),
        )

        for (
            label,
            field_name,
            expected_value,
            expected_log_message,
        ) in test_data:
            with self.subTest(label):
                with self.assertLogs(
                    "app.search.buckets", level="WARNING"
                ) as log:
                    value = Aggregation.get_long_aggs_name_for_field_name(
                        field_name
                    )
                    self.assertEqual(value, expected_value)
                    self.assertIn(expected_log_message, "".join(log.output))
