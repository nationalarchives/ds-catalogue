from http import HTTPStatus

import responses
from app.search.collection_names import COLLECTION_CHOICES
from django.conf import settings
from django.test import TestCase


class CatalogueSearchViewCollectionFilterTests(TestCase):
    """Mainly tests the context.
    Collection filter is only available for tna group."""

    @responses.activate
    def test_search_with_known_filters_returns_results(
        self,
    ):
        """Test that known filter values which match the config return results."""

        # &collection=BT&collection=WO
        input_collections = ["BT", "WO"]
        collection_query = "&" + "&".join(
            f"collection={col}" for col in input_collections
        )

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

        # input matches configured collection
        config_values = [choice[0] for choice in COLLECTION_CHOICES]
        self.assertTrue(set(input_collections).issubset(config_values))

        # + &collection=BT&collection=WO
        response = self.client.get(
            "/catalogue/search/?q=ufo" + collection_query
        )

        context_data = response.context_data
        form = context_data.get("form")
        collection_field = form.fields["collection"]

        self.assertEqual(len(context_data.get("results")), 1)

        self.assertEqual(
            collection_field.value,
            ["BT", "WO"],
        )
        self.assertEqual(
            collection_field.cleaned,
            ["BT", "WO"],
        )
        self.assertEqual(collection_field.choices_updated, True)
        self.assertEqual(
            collection_field.items,
            [
                {
                    "text": "BT - Board of Trade and successors (50)",
                    "value": "BT",
                    "checked": True,
                },
                {
                    "text": "WO - War Office, Armed Forces, Judge Advocate General, and related bodies (35)",
                    "value": "WO",
                    "checked": True,
                },
            ],
        )
        self.assertEqual(
            context_data.get("selected_filters"),
            [
                {
                    "label": "Collection: BT - Board of Trade and successors",
                    "href": "?q=ufo&collection=WO",
                    "title": "Remove BT - Board of Trade and successors collection",
                },
                {
                    "label": "Collection: WO - War Office, Armed Forces, Judge Advocate General, and related bodies",
                    "href": "?q=ufo&collection=BT",
                    "title": "Remove WO - War Office, Armed Forces, Judge Advocate General, and related bodies collection",
                },
            ],
        )

    @responses.activate
    def test_search_with_known_filters_with_unmatched_config_returns_results(
        self,
    ):
        """Test that known filter value found in API response but does not match config
        returns results."""

        input_collection = "VALUE-DOES-NOT-MATCH-CONFIG"

        # data present for input collection
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
                            {
                                "value": "VALUE-DOES-NOT-MATCH-CONFIG",
                                "doc_count": 50,
                            },
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
                    "total": 26008838,
                    "results": 20,
                },
            },
            status=HTTPStatus.OK,
        )

        # input does not match configured collection
        config_values = [choice[0] for choice in COLLECTION_CHOICES]
        self.assertNotIn(input_collection, config_values)

        # &collection=VALUE-DOES-NOT-MATCH-CONFIG
        response = self.client.get(
            "/catalogue/search/?collection=" + input_collection
        )

        context_data = response.context_data
        form = context_data.get("form")
        collection_field = form.fields["collection"]

        self.assertEqual(len(context_data.get("results")), 1)

        self.assertEqual(
            collection_field.value,
            ["VALUE-DOES-NOT-MATCH-CONFIG"],
        )
        self.assertEqual(
            collection_field.cleaned,
            [
                "VALUE-DOES-NOT-MATCH-CONFIG",
            ],
        )
        self.assertEqual(collection_field.choices_updated, True)
        self.assertEqual(
            collection_field.items,
            [
                {
                    "text": "VALUE-DOES-NOT-MATCH-CONFIG (50)",
                    "value": "VALUE-DOES-NOT-MATCH-CONFIG",
                    "checked": True,
                },
            ],
        )
        self.assertEqual(
            context_data.get("selected_filters"),
            [
                {
                    "label": "Collection: VALUE-DOES-NOT-MATCH-CONFIG",
                    "href": "?",
                    "title": "Remove VALUE-DOES-NOT-MATCH-CONFIG collection",
                },
            ],
        )

    @responses.activate
    def test_search_with_unknown_filter_returns_no_results(
        self,
    ):
        """Test that unknown filter values result in no results."""

        # no data for input collection
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [],
                "aggregations": [
                    {
                        "name": "collection",
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
            "/catalogue/search/?collection=DOESNOTEXIST",
        )

        context_data = response.context_data
        form = context_data.get("form")
        collection_field = form.fields["collection"]
        level_field = form.fields["level"]

        self.assertEqual(len(context_data.get("results")), 0)

        self.assertEqual(
            collection_field.value,
            ["DOESNOTEXIST"],
        )
        self.assertEqual(
            collection_field.cleaned,
            ["DOESNOTEXIST"],
        )

        self.assertEqual(collection_field.choices_updated, True)

        # queried valid values without their config have a count of 0
        self.assertEqual(
            collection_field.items,
            [
                {
                    "text": "DOESNOTEXIST (0)",
                    "value": "DOESNOTEXIST",
                    "checked": True,
                },
            ],
        )
        self.assertEqual(
            context_data.get("selected_filters"),
            [
                {
                    "label": "Collection: DOESNOTEXIST",
                    "href": "?",
                    "title": "Remove DOESNOTEXIST collection",
                },
            ],
        )

        self.assertEqual(level_field.choices_updated, True)
        self.assertEqual(level_field.items, [])

    @responses.activate
    def test_search_with_some_known_and_unknown_filters_returns_results(
        self,
    ):
        """Test that known and unknown filter values return results for known filter."""

        # data returned for known collection only
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
                    "total": 26008838,
                    "results": 20,
                },
            },
            status=HTTPStatus.OK,
        )

        response = self.client.get(
            "/catalogue/search/?q=ufo&collection=BT&collection=DOESNOTEXIST",
        )

        context_data = response.context_data
        form = context_data.get("form")
        collection_field = form.fields["collection"]

        self.assertEqual(len(context_data.get("results")), 1)

        self.assertEqual(
            collection_field.value,
            ["BT", "DOESNOTEXIST"],
        )
        self.assertEqual(
            collection_field.cleaned,
            ["BT", "DOESNOTEXIST"],
        )

        self.assertEqual(collection_field.choices_updated, True)

        # queried valid values without their config have a count of 0
        self.assertEqual(
            collection_field.items,
            [
                {
                    "text": "BT - Board of Trade and successors (50)",
                    "value": "BT",
                    "checked": True,
                },
                {
                    "text": "DOESNOTEXIST (0)",
                    "value": "DOESNOTEXIST",
                    "checked": True,
                },
            ],
        )
        self.assertEqual(
            context_data.get("selected_filters"),
            [
                {
                    "label": "Collection: BT - Board of Trade and successors",
                    "href": "?q=ufo&collection=DOESNOTEXIST",
                    "title": "Remove BT - Board of Trade and successors collection",
                },
                {
                    "label": "Collection: DOESNOTEXIST",
                    "href": "?q=ufo&collection=BT",
                    "title": "Remove DOESNOTEXIST collection",
                },
            ],
        )

    @responses.activate
    def test_search_with_unknown_filter_returns_no_results_no_aggs(
        self,
    ):
        """Tests configure choices do not appear when no data is returned
        and also no aggregations returned for the input filter value."""

        # no data for input collection, no aggregations returned
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [],
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
            "/catalogue/search/?collection=DOESNOTEXIST",
        )

        context_data = response.context_data
        form = context_data.get("form")
        collection_field = form.fields["collection"]
        level_field = form.fields["level"]

        self.assertEqual(len(context_data.get("results")), 0)

        self.assertEqual(
            collection_field.value,
            ["DOESNOTEXIST"],
        )
        self.assertEqual(
            collection_field.cleaned,
            ["DOESNOTEXIST"],
        )

        self.assertEqual(collection_field.choices_updated, True)
        # should not reflect configured choices
        self.assertEqual(len(collection_field.items), 1)
        self.assertEqual(
            context_data.get("selected_filters"),
            [
                {
                    "label": "Collection: DOESNOTEXIST",
                    "href": "?",
                    "title": "Remove DOESNOTEXIST collection",
                },
            ],
        )

        self.assertEqual(level_field.choices_updated, True)
        # should not reflect configured choices
        self.assertEqual(len(level_field.items), 0)
