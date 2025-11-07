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

        response = self.client.get("/catalogue/search/?group=nonTna")

        form = response.context_data.get("form")
        group_field = form.fields[FieldsConstant.GROUP]

        self.assertEqual(response.status_code, HTTPStatus.OK)

        self.assertIsInstance(form, CatalogueSearchNonTnaForm)
        self.assertEqual(form.errors, {})
        self.assertEqual(len(form.fields), 7)
        non_tna_field_names = [
            FieldsConstant.GROUP,
            FieldsConstant.SORT,
            FieldsConstant.Q,
            FieldsConstant.FILTER_LIST,
            FieldsConstant.COVERING_DATE_FROM,
            FieldsConstant.COVERING_DATE_TO,
            FieldsConstant.HELD_BY,
        ]

        non_tna_form_field_names = list(form.fields.keys())

        self.assertEqual(non_tna_form_field_names, non_tna_field_names)

        self.assertEqual(group_field.name, "group")
        self.assertEqual(
            group_field.value,
            "nonTna",
        )
        self.assertEqual(
            group_field.cleaned,
            "nonTna",
        )

        self.assertEqual(
            group_field.items,
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
        self.assertEqual(response.context_data.get("selected_filters"), [])
