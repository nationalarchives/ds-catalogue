from http import HTTPStatus

import responses
from app.search.constants import Display, FieldsConstant
from app.search.forms import CatalogueSearchCommonForm
from django.conf import settings
from django.test import TestCase
from django.utils.encoding import force_str


class CatalogueSearchViewDisplayTests(TestCase):
    """Mainly tests the context."""

    @responses.activate
    def test_search_with_default_display(self):
        """Test filter with default display param value (LIST)."""

        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [
                    {
                        "@template": {
                            "details": {
                                "id": "C123456",
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

        response = self.client.get("/catalogue/search/?")
        form = response.context_data.get("form")
        display_field = response.context_data.get("form").fields[
            FieldsConstant.DISPLAY
        ]

        self.assertTrue(form.is_valid())

        self.assertEqual(display_field.error, {})
        self.assertEqual(display_field.value, Display.LIST)
        self.assertEqual(display_field.cleaned, Display.LIST)

        self.assertEqual(response.context_data.get("selected_filters"), [])

    @responses.activate
    def test_search_with_grid_display(self):
        """Test filter with display param value (GRID)."""

        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [
                    {
                        "@template": {
                            "details": {
                                "id": "C123456",
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

        response = self.client.get("/catalogue/search/?display=grid")
        form = response.context_data.get("form")
        display_field = response.context_data.get("form").fields[
            FieldsConstant.DISPLAY
        ]

        self.assertTrue(form.is_valid())

        self.assertEqual(display_field.error, {})
        self.assertEqual(display_field.value, Display.GRID)
        self.assertEqual(display_field.cleaned, Display.GRID)

        self.assertEqual(response.context_data.get("selected_filters"), [])
        self.assertTrue(response.context_data.get("filters_visible"))

    def test_search_with_invalid_display(self):
        """Tests that an invalid display param returns the form with errors."""

        response = self.client.get("/catalogue/search/?display=INVALID")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        form = response.context_data.get("form")
        display_field = response.context_data.get("form").fields[
            FieldsConstant.DISPLAY
        ]
        html = force_str(response.content)

        self.assertIsInstance(form, CatalogueSearchCommonForm)
        self.assertEqual(form.is_valid(), False)

        self.assertEqual(
            form.errors,
            {
                "display": {
                    "text": "Enter a valid choice. [INVALID] is not one of the available choices. Valid choices are [list, grid]"
                }
            },
        )
        self.assertEqual(form.non_field_errors, [])
        self.assertEqual(display_field.value, "INVALID")
        self.assertEqual(display_field.cleaned, None)
        self.assertEqual(
            display_field.error,
            {
                "text": "Enter a valid choice. [INVALID] is not one of the available choices. Valid choices are [list, grid]"
            },
        )

        self.assertEqual(
            display_field.items,
            [
                {
                    "text": "List view",
                    "value": "list",
                },
                {
                    "text": "Grid view",
                    "value": "grid",
                },
            ],
        )

        self.assertEqual(response.context_data.get("selected_filters"), [])
        self.assertFalse(response.context_data.get("filters_visible"))

        # test for presence of hidden inputs for invalid display param
        self.assertIn(
            """<input type="hidden" name="display" value="INVALID">""", html
        )
        self.assertIn(
            """<input type="hidden" name="group" value="tna">""", html
        )
