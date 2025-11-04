from http import HTTPStatus

import responses
from app.search.collection_names import COLLECTION_CHOICES
from django.conf import settings
from django.test import TestCase


class CatalogueSearchViewCollectionMoreFilterAttrsTests(TestCase):
    """Collection filter is only available for tna group."""

    @responses.activate
    def test_search_for_more_filter_choices_attributes_without_filters(
        self,
    ):
        """Tests more filter choices attributes are correctly set in context"""

        # data present for input collections
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
                        "name": "collection",
                        "entries": [
                            {"value": "BT", "doc_count": 50},
                            {"value": "WO", "doc_count": 35},
                        ],
                        "total": 100,
                        "other": 50,
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
            },
            status=HTTPStatus.OK,
        )

        response = self.client.get("/catalogue/search/")

        context_data = response.context_data
        form = context_data.get("form")
        collection_field = form.fields["collection"]

        self.assertEqual(len(context_data.get("results")), 1)
        self.assertEqual(
            collection_field.more_filter_choices_available,
            True,
        )
        self.assertEqual(
            collection_field.more_filter_choices_text, "See more collections"
        )
        self.assertEqual(
            collection_field.more_filter_choices_url,
            "?filter_list=longCollection",
        )

    @responses.activate
    def test_search_for_more_filter_choices_attributes_with_filters(
        self,
    ):
        """Tests more filter choices attributes are correctly set in context"""

        # data present for input collections
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
                        "name": "collection",
                        "entries": [
                            {"value": "BT", "doc_count": 50},
                            {"value": "WO", "doc_count": 35},
                        ],
                        "total": 100,
                        "other": 50,
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
            },
            status=HTTPStatus.OK,
        )

        response = self.client.get(
            "/catalogue/search/?"
            "q=ufo"
            "&display=list"
            "&group=tna"
            "&online=true"
            "&covering_date_from-year=1900"
            "&covering_date_to-year=2024"
            "&level=Item"
            "&closure=Open+Document%2C+Open+Description"
            "&sort=title:asc"
        )

        context_data = response.context_data
        form = context_data.get("form")
        collection_field = form.fields["collection"]

        self.assertEqual(len(context_data.get("results")), 1)
        self.assertEqual(
            collection_field.more_filter_choices_available,
            True,
        )
        self.assertEqual(
            collection_field.more_filter_choices_text, "See more collections"
        )
        self.assertEqual(
            collection_field.more_filter_choices_url,
            "?q=ufo"
            "&display=list"
            "&group=tna"
            "&online=true"
            "&covering_date_from-year=1900"
            "&covering_date_to-year=2024"
            "&level=Item"
            "&closure=Open+Document%2C+Open+Description"
            "&sort=title%3Aasc"
            "&filter_list=longCollection",
        )
