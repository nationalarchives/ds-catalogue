from http import HTTPStatus

import responses
from app.search.forms import (
    CatalogueSearchNonTnaForm,
    FieldsConstant,
)
from django.conf import settings
from django.test import TestCase


class CatalogueSearchViewGroupParamTests(TestCase):
    """Mainly tests the context.
    Group param decides which form to use."""

    @responses.activate
    def test_catalogue_search_context_with_non_tna_group(self):

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
                "aggregations": [],
                "buckets": [
                    {
                        "name": "group",
                        "entries": [
                            {"value": "nonTna", "count": 1},
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

        self.response = self.client.get("/catalogue/search/?group=nonTna")
        self.assertEqual(self.response.status_code, HTTPStatus.OK)

        self.assertIsInstance(
            self.response.context_data.get("form"), CatalogueSearchNonTnaForm
        )
        self.assertEqual(self.response.context_data.get("form").errors, {})
        self.assertEqual(len(self.response.context_data.get("form").fields), 4)
        non_tna_field_names = [
            FieldsConstant.GROUP,
            FieldsConstant.SORT,
            FieldsConstant.Q,
            FieldsConstant.HELD_BY,
        ]
        non_tna_form_field_names = set(
            self.response.context_data.get("form").fields.keys()
        )
        self.assertTrue(
            set(non_tna_field_names) == set(non_tna_form_field_names)
        )

        self.assertEqual(
            self.response.context_data.get("form").fields["group"].name, "group"
        )
        self.assertEqual(
            self.response.context_data.get("form").fields["group"].value,
            "nonTna",
        )
        self.assertEqual(
            self.response.context_data.get("form").fields["group"].cleaned,
            "nonTna",
        )

        self.assertEqual(
            self.response.context_data.get("form").fields["group"].items,
            [
                {
                    "text": "Records at the National Archives",
                    "value": "tna",
                },
                {
                    "text": "Records at other UK archives",
                    "value": "nonTna",
                    "checked": True,
                },
            ],
        )
        self.assertEqual(self.response.context_data.get("selected_filters"), [])
