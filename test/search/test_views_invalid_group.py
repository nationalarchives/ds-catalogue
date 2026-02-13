from http import HTTPStatus

from app.search.constants import FieldsConstant
from app.search.forms import CatalogueSearchBaseForm
from django.test import TestCase
from django.utils.encoding import force_str


class CatalogueSearchViewInvalidViewTests(TestCase):
    """Tests for invalid group param handling in catalogue search view."""

    def test_search_with_invalid_group(self):
        """Tests that an invalid group param returns the base form with errors."""

        response = self.client.get("/catalogue/search/?group=INVALID")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        form = response.context_data.get("form")
        group_field = response.context_data.get("form").fields[
            FieldsConstant.GROUP
        ]
        html = force_str(response.content)

        self.assertIsInstance(form, CatalogueSearchBaseForm)
        self.assertEqual(form.is_valid(), False)

        self.assertEqual(
            form.errors,
            {
                "group": {
                    "text": "Enter a valid choice. [INVALID] is not one of the available choices. Valid choices are [tna, nonTna]"
                }
            },
        )
        self.assertEqual(form.non_field_errors, [])
        self.assertEqual(group_field.value, "INVALID")
        self.assertEqual(group_field.cleaned, None)
        self.assertEqual(
            group_field.error,
            {
                "text": "Enter a valid choice. [INVALID] is not one of the available choices. Valid choices are [tna, nonTna]"
            },
        )

        self.assertEqual(len(form.fields), 2)
        field_names = [
            FieldsConstant.GROUP,
            FieldsConstant.Q,
        ]
        form_field_names = list(form.fields.keys())
        self.assertEqual(form_field_names, field_names)

        # unchecked values for group field
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
                },
            ],
        )

        self.assertEqual(response.context_data.get("selected_filters"), [])

        self.assertFalse(response.context_data.get("filters_visible"))
        self.assertFalse(hasattr(group_field, "is_visible"))

        # test for presence of hidden inputs for invalid group param
        self.assertIn(
            """<input type="hidden" name="display" value="list">""", html
        )
        self.assertIn(
            """<input type="hidden" name="group" value="INVALID">""", html
        )

        self.assertEqual(
            response.context_data.get("show_banner_for_filters_not_applied"),
            False,
        )
