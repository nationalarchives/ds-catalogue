import copy

from app.search.buckets import CATALOGUE_BUCKETS, BucketKeys
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
