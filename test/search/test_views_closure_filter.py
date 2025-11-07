from http import HTTPStatus

import responses
from django.conf import settings
from django.test import TestCase


class CatalogueSearchViewClosureFilterTests(TestCase):
    """Mainly tests the context."""

    def setUp(self):
        self.maxDiff = None

    @responses.activate
    def test_catalogue_search_context_with_valid_closure_param(self):

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
                    },
                    {
                        "@template": {
                            "details": {
                                "iaid": "C7890",
                                "source": "CAT",
                            }
                        }
                    },
                ],
                "aggregations": [
                    {
                        "name": "closure",
                        "entries": [
                            {
                                "value": "Open Document, Open Description",
                                "doc_count": 150,
                            },
                            {
                                "value": "Closed Or Retained Document, Open Description",
                                "doc_count": 50,
                            },
                        ],
                        "total": 100,
                        "other": 0,
                    }
                ],
                "buckets": [
                    {
                        "name": "group",
                        "entries": [
                            {"value": "tna", "count": 200},
                        ],
                    }
                ],
                "stats": {
                    "total": 2,
                    "results": 20,
                },
            },
            status=HTTPStatus.OK,
        )

        response = self.client.get(
            "/catalogue/search/?q=ufo&closure=Open+Document,+Open+Description&closure=Closed+Or+Retained+Document,+Open+Description"
        )
        context_data = response.context_data
        closure_field = context_data.get("form").fields["closure"]

        self.assertEqual(
            closure_field.value,
            [
                "Open Document, Open Description",
                "Closed Or Retained Document, Open Description",
            ],
        )
        self.assertEqual(
            closure_field.cleaned,
            [
                "Open Document, Open Description",
                "Closed Or Retained Document, Open Description",
            ],
        )
        self.assertEqual(
            closure_field.items,
            [
                {
                    "text": "Open Document, Open Description (150)",
                    "value": "Open Document, Open Description",
                    "checked": True,
                },
                {
                    "text": "Closed Or Retained Document, Open Description (50)",
                    "value": "Closed Or Retained Document, Open Description",
                    "checked": True,
                },
            ],
        )
        self.assertEqual(
            context_data.get("selected_filters"),
            [
                {
                    "label": "Closure status: Open Document, Open Description",
                    "href": "?q=ufo&closure=Closed+Or+Retained+Document%2C+Open+Description",
                    "title": "Remove Open Document, Open Description closure status",
                },
                {
                    "label": "Closure status: Closed Or Retained Document, Open Description",
                    "href": "?q=ufo&closure=Open+Document%2C+Open+Description",
                    "title": "Remove Closed Or Retained Document, Open Description closure status",
                },
            ],
        )
        self.assertEqual(
            closure_field.more_filter_choices_available,
            False,
        )
        self.assertEqual(
            closure_field.more_filter_choices_url,
            "",
        )
        self.assertEqual(
            closure_field.more_filter_choices_text,
            "",
        )

    @responses.activate
    def test_catalogue_search_context_with_invalid_closure_param(self):

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
                        "name": "closure",
                        "entries": [
                            {
                                "value": "Open Document, Open Description",
                                "doc_count": 150,
                            },
                        ],
                        "total": 100,
                        "other": 0,
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
            "/catalogue/search/?q=ufo&closure=Open+Document,+Open+Description&closure=invalid"
        )
        context_data = response.context_data
        closure_field = context_data.get("form").fields["closure"]

        self.assertEqual(
            closure_field.value,
            [
                "Open Document, Open Description",
                "invalid",
            ],
        )
        self.assertEqual(
            closure_field.cleaned,
            [
                "Open Document, Open Description",
                "invalid",
            ],
        )
        self.assertEqual(
            closure_field.items,
            [
                {
                    "text": "Open Document, Open Description (150)",
                    "value": "Open Document, Open Description",
                    "checked": True,
                },
                {
                    "text": "invalid (0)",
                    "value": "invalid",
                    "checked": True,
                },
            ],
        )
        self.assertEqual(
            context_data.get("selected_filters"),
            [
                {
                    "label": "Closure status: Open Document, Open Description",
                    "href": "?q=ufo&closure=invalid",
                    "title": "Remove Open Document, Open Description closure status",
                },
                {
                    "label": "Closure status: invalid",
                    "href": "?q=ufo&closure=Open+Document%2C+Open+Description",
                    "title": "Remove invalid closure status",
                },
            ],
        )
        self.assertEqual(
            closure_field.more_filter_choices_available,
            False,
        )
