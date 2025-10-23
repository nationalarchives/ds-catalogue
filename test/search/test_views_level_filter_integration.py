"""Integration tests covers testing ouput HTML."""

from django.test import TestCase
from django.utils.encoding import force_str


class CatalogueSearchViewLevelFilterIntegrationTests(TestCase):
    """Tests context with hidden level filter inputs in the template output."""

    def test_catalogue_search_context_with_invalid_level_param(self):
        """Test level filter with invalid param value.
        No response mocking as we are testing invalid param handling only."""

        # with valid and invalid param values
        self.response = self.client.get(
            "/catalogue/search/?q=ufo&level=Item&level=Division&level=invalid"
        )

        self.form = self.response.context_data.get("form")
        self.level_field = self.response.context_data.get("form").fields[
            "level"
        ]

        html = force_str(self.response.content)

        self.assertEqual(self.form.is_valid(), False)

        # test for presence of hidden inputs for invalid level params
        self.assertIn(
            """<input type="hidden" name="level" value="Item">""", html
        )
        self.assertIn(
            """<input type="hidden" name="level" value="Division">""", html
        )
        self.assertIn(
            """<input type="hidden" name="level" value="invalid">""", html
        )

        self.assertEqual(
            self.form.errors,
            {
                "level": {
                    "text": "Enter a valid choice. Value(s) [Item, Division, invalid] "
                    "do not belong to the available choices. Valid choices are "
                    "[Department, Division, Series, Sub-series, Sub-sub-series, "
                    "Piece, Item]"
                }
            },
        )
        self.assertEqual(self.level_field.choices_updated, True)
        self.assertEqual(
            self.level_field.value,
            ["Item", "Division", "invalid"],
        )
        self.assertEqual(self.level_field.cleaned, None)
        # invalid inputs are not shown, so items is empty
        self.assertEqual(
            self.level_field.items,
            [],
        )
        # all inputs including invalid are shown in selected filters
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
