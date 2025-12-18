from http import HTTPStatus

import responses
from app.search.constants import FieldsConstant
from django.conf import settings
from django.test import TestCase
from django.utils.encoding import force_str


class CatalogueSearchViewOnlineFilterTests(TestCase):
    """Mainly tests the context.
    Online filter is only available for tna group."""

    @responses.activate
    def test_search_with_valid_input(self):
        """Test filter with valid param value."""

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

        response = self.client.get("/catalogue/search/?online=true")
        form = response.context_data.get("form")
        online_field = response.context_data.get("form").fields[
            FieldsConstant.ONLINE
        ]

        self.assertTrue(form.is_valid())

        self.assertEqual(online_field.error, {})
        self.assertEqual(online_field.value, "true")
        self.assertEqual(online_field.cleaned, "true")

        self.assertEqual(
            response.context_data.get("selected_filters"),
            [
                {
                    "label": "Online only",
                    "href": "?",
                    "title": "Remove online only",
                }
            ],
        )

        self.assertTrue(response.context_data.get("filters_visible"))
        self.assertTrue(online_field.is_visible)

    def test_search_with_invalid_input(self):
        """Test filter with invalid param value."""

        response = self.client.get("/catalogue/search/?online=INVALID")
        form = response.context_data.get("form")
        online_field = response.context_data.get("form").fields[
            FieldsConstant.ONLINE
        ]

        self.assertFalse(form.is_valid())

        self.assertEqual(
            online_field.error,
            {
                "text": "Enter a valid choice. [INVALID] is not one of the available choices. Valid choices are [, true]"
            },
        )
        self.assertEqual(online_field.value, "INVALID")
        self.assertEqual(online_field.cleaned, None)

        self.assertEqual(response.context_data.get("selected_filters"), [])

        self.assertFalse(response.context_data.get("filters_visible"))
        self.assertFalse(online_field.is_visible)

        # other fields visibility
        self.assertFalse(
            form.fields.get(FieldsConstant.COVERING_DATE_FROM).is_visible
        )
        self.assertFalse(
            form.fields.get(FieldsConstant.COVERING_DATE_TO).is_visible
        )
        self.assertFalse(form.fields.get(FieldsConstant.COLLECTION).is_visible)
        self.assertFalse(form.fields.get(FieldsConstant.LEVEL).is_visible)
        self.assertFalse(form.fields.get(FieldsConstant.SUBJECT).is_visible)
        self.assertFalse(form.fields.get(FieldsConstant.CLOSURE).is_visible)
        self.assertFalse(
            form.fields.get(FieldsConstant.OPENING_DATE_FROM).is_visible
        )
        self.assertFalse(
            form.fields.get(FieldsConstant.OPENING_DATE_TO).is_visible
        )
