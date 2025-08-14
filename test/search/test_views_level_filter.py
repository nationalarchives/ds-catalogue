from http import HTTPStatus

import responses
from django.conf import settings
from django.test import TestCase


class CatalogueSearchViewLevelFilterTests(TestCase):
    """Mainly tests the context."""

    @responses.activate
    def test_catalogue_search_context_with_valid_level_param(self):

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
                        "name": "level",
                        "entries": [
                            {"value": "Lettercode", "doc_count": 100},
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

        # valid level params, Department->Lettercode replacement
        self.response = self.client.get(
            "/catalogue/search/?q=ufo&level=Department&level=Division"
        )

        self.assertEqual(
            self.response.context_data.get("form").fields["level"].value,
            ["Department", "Division"],
        )
        self.assertEqual(
            self.response.context_data.get("form").fields["level"].cleaned,
            ["Department", "Division"],
        )
        # queried valid values without their response have a count of 0
        # shows Lettercode to Deparment replacement
        self.assertEqual(
            self.response.context_data.get("form").fields["level"].items,
            [
                {
                    "text": "Department (100)",
                    "value": "Department",
                    "checked": True,
                },
                {"text": "Division (0)", "value": "Division", "checked": True},
            ],
        )
        self.assertEqual(
            self.response.context_data.get("selected_filters"),
            [
                {
                    "label": "Level: Department",
                    "href": "?q=ufo&level=Division",
                    "title": "Remove Department level",
                },
                {
                    "label": "Level: Division",
                    "href": "?q=ufo&level=Department",
                    "title": "Remove Division level",
                },
            ],
        )

    @responses.activate
    def test_catalogue_search_context_with_invalid_level_param(self):

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
                        "name": "level",
                        "entries": [
                            {"value": "Item", "doc_count": 100},
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

        # with valid and invalid param values
        self.response = self.client.get(
            "/catalogue/search/?q=ufo&level=Item&level=Division&level=invalid"
        )

        self.assertEqual(
            self.response.context_data.get("form").fields["level"].value,
            ["Item", "Division", "invalid"],
        )
        self.assertEqual(
            self.response.context_data.get("form").fields["level"].cleaned,
            None,
        )
        # with some invalid input filter show valid with count 0
        self.assertEqual(
            self.response.context_data.get("form").fields["level"].items,
            [
                {"text": "Item (0)", "value": "Item", "checked": True},
                {"text": "Division (0)", "value": "Division", "checked": True},
            ],
        )
        # with some invalid input selected shows all filters
        self.assertEqual(
            self.response.context_data.get("selected_filters"),
            [
                {
                    "label": "Level: Item",
                    "href": "?q=ufo&level=Division&level=invalid",
                    "title": "Remove Item level",
                },
                {
                    "label": "Level: Division",
                    "href": "?q=ufo&level=Item&level=invalid",
                    "title": "Remove Division level",
                },
                {
                    "label": "Level: invalid",
                    "href": "?q=ufo&level=Item&level=Division",
                    "title": "Remove invalid level",
                },
            ],
        )
