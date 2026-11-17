from http import HTTPStatus

from django.test import TestCase

from app.search.constants import FieldsConstant
from app.search.forms import CatalogueSearchBaseForm


class CatalogueSearchViewFilterListTests(TestCase):
    """Test for filter list parameter handling in catalogue search view."""

    def test_filter_list_choices(self):
        """Tests that an invalid filter_list parameter returns the base form with errors."""

        response = self.client.get("/catalogue/search/?filter_list=INVALID")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        form = response.context_data.get("form")
        filter_list_field = response.context_data.get("form").fields[
            FieldsConstant.FILTER_LIST
        ]

        self.assertIsInstance(form, CatalogueSearchBaseForm)
        self.assertFalse(form.is_valid())

        self.assertEqual(
            form.errors,
            {
                "filter_list": {
                    "text": "Enter a valid choice. [INVALID] is not one of the available choices. Valid choices are [, longCollection, longHeldBy, longSubject, longCollectionY]"
                }
            },
        )
        self.assertEqual(form.non_field_errors, [])
        self.assertEqual(filter_list_field.value, "INVALID")
        self.assertEqual(filter_list_field.cleaned, None)
        self.assertEqual(
            filter_list_field.error,
            {
                "text": "Enter a valid choice. [INVALID] is not one of the available choices. Valid choices are [, longCollection, longHeldBy, longSubject, longCollectionY]"
            },
        )

        self.assertEqual(
            filter_list_field.items,
            [
                {"text": "No filter", "value": ""},
                {"text": "collection", "value": "longCollection"},
                {"text": "held_by", "value": "longHeldBy"},
                {"text": "subject", "value": "longSubject"},
                {"text": "collection", "value": "longCollectionY"},
            ],
        )
