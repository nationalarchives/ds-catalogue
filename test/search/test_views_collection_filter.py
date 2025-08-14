from http import HTTPStatus

import responses
from django.conf import settings
from django.test import TestCase


class CatalogueSearchViewCollectionFilterTests(TestCase):
    """Mainly tests the context."""

    @responses.activate
    def test_catalogue_search_context_with_config_collection_params_returns_data_for_all_params(
        self,
    ):

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

        # configured collection params
        self.response = self.client.get(
            "/catalogue/search/?q=NOTCONFIGUREDHASRESULTS&collection=BT&collection=WO"
        )

        self.assertEqual(
            self.response.context_data.get("form").fields["collection"].value,
            ["BT", "WO"],
        )
        self.assertEqual(
            self.response.context_data.get("form").fields["collection"].cleaned,
            ["BT", "WO"],
        )
        self.assertEqual(
            self.response.context_data.get("form").fields["collection"].items,
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
            self.response.context_data.get("selected_filters"),
            [
                {
                    "label": "Collection: BT - Board of Trade and successors",
                    "href": "?q=NOTCONFIGUREDHASRESULTS&collection=WO",
                    "title": "Remove BT - Board of Trade and successors collection",
                },
                {
                    "label": "Collection: WO - War Office, Armed Forces, Judge Advocate General, and related bodies",
                    "href": "?q=NOTCONFIGUREDHASRESULTS&collection=BT",
                    "title": "Remove WO - War Office, Armed Forces, Judge Advocate General, and related bodies collection",
                },
            ],
        )

    @responses.activate
    def test_catalogue_search_context_with_collection_params_returns_data_for_some_params(
        self,
    ):

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
                            {
                                "value": "NOTCONFIGUREDHASRESULTS",
                                "doc_count": 2,
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

        # configured collection name param=BT has results,
        # configured collection name param=WO does not have results
        # not configured collection name param=NOTCONFIGUREDNORESULTS does not have results
        # not configured collection name param=NOTCONFIGUREDHASRESULTS has results
        self.response = self.client.get(
            "/catalogue/search/?q=NOTCONFIGUREDHASRESULTS&collection=BT&collection=WO&collection=NOTCONFIGUREDNORESULTS&collection=NOTCONFIGUREDHASRESULTS"
        )

        self.assertEqual(
            self.response.context_data.get("form").fields["collection"].value,
            ["BT", "WO", "NOTCONFIGUREDNORESULTS", "NOTCONFIGUREDHASRESULTS"],
        )
        self.assertEqual(
            self.response.context_data.get("form").fields["collection"].cleaned,
            ["BT", "WO", "NOTCONFIGUREDNORESULTS", "NOTCONFIGUREDHASRESULTS"],
        )
        # queried valid values without their have a count of 0
        self.assertEqual(
            self.response.context_data.get("form").fields["collection"].items,
            [
                {
                    "text": "BT - Board of Trade and successors (50)",
                    "value": "BT",
                    "checked": True,
                },
                {
                    "text": "NOTCONFIGUREDHASRESULTS (2)",
                    "value": "NOTCONFIGUREDHASRESULTS",
                    "checked": True,
                },
                {
                    "text": "WO - War Office, Armed Forces, Judge Advocate General, and related bodies (0)",
                    "value": "WO",
                    "checked": True,
                },
                {
                    "text": "NOTCONFIGUREDNORESULTS (0)",
                    "value": "NOTCONFIGUREDNORESULTS",
                    "checked": True,
                },
            ],
        )
        self.assertEqual(
            self.response.context_data.get("selected_filters"),
            [
                {
                    "label": "Collection: BT - Board of Trade and successors",
                    "href": "?q=NOTCONFIGUREDHASRESULTS&collection=WO&collection=NOTCONFIGUREDNORESULTS&collection=NOTCONFIGUREDHASRESULTS",
                    "title": "Remove BT - Board of Trade and successors collection",
                },
                {
                    "label": "Collection: WO - War Office, Armed Forces, Judge Advocate General, and related bodies",
                    "href": "?q=NOTCONFIGUREDHASRESULTS&collection=BT&collection=NOTCONFIGUREDNORESULTS&collection=NOTCONFIGUREDHASRESULTS",
                    "title": "Remove WO - War Office, Armed Forces, Judge Advocate General, and related bodies collection",
                },
                {
                    "label": "Collection: NOTCONFIGUREDNORESULTS",
                    "href": "?q=NOTCONFIGUREDHASRESULTS&collection=BT&collection=WO&collection=NOTCONFIGUREDHASRESULTS",
                    "title": "Remove NOTCONFIGUREDNORESULTS collection",
                },
                {
                    "label": "Collection: NOTCONFIGUREDHASRESULTS",
                    "href": "?q=NOTCONFIGUREDHASRESULTS&collection=BT&collection=WO&collection=NOTCONFIGUREDNORESULTS",
                    "title": "Remove NOTCONFIGUREDHASRESULTS collection",
                },
            ],
        )
