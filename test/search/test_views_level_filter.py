from http import HTTPStatus

import responses
from django.conf import settings
from django.test import TestCase
from django.utils.encoding import force_str


class CatalogueSearchViewLevelFilterTests(TestCase):
    """Mainly tests the context.
    Level filter is only available for tna group."""

    @responses.activate
    def test_search_with_valid_level_filters(self):
        """Test level filter with valid param value."""

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

        # valid level params, Department->Lettercode replacement
        response = self.client.get(
            "/catalogue/search/?q=ufo&level=Department&level=Division"
        )
        form = response.context_data.get("form")
        level_field = response.context_data.get("form").fields["level"]

        self.assertEqual(form.is_valid(), True)

        self.assertEqual(level_field.value, ["Department", "Division"])
        self.assertEqual(
            level_field.cleaned,
            ["Department", "Division"],
        )
        self.assertEqual(level_field.choices_updated, True)
        # queried valid values without their response have a count of 0
        # shows Lettercode to Deparment replacement
        self.assertEqual(
            level_field.items,
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
            response.context_data.get("selected_filters"),
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
        self.assertEqual(
            level_field.more_filter_choices_available,
            False,
        )
        self.assertEqual(level_field.more_filter_choices_url, "")
        self.assertEqual(level_field.more_filter_choices_text, "")

    def test_search_with_invalid_level_filters_returns_error_with_no_results(
        self,
    ):
        """Test level filter with invalid param value.
        No response mocking as we are testing invalid param handling only.
        Also tests collection filter configured choices update based on level filter.
        """

        # with valid and invalid param values
        response = self.client.get(
            "/catalogue/search/?q=ufo&level=Item&level=Division&level=invalid"
        )

        form = response.context_data.get("form")
        context_data = response.context_data
        level_field = context_data.get("form").fields["level"]
        collection_field = response.context_data.get("form").fields[
            "collection"
        ]

        html = force_str(response.content)

        self.assertEqual(form.is_valid(), False)

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

        # returns None when errors present
        self.assertEqual(context_data.get("results"), None)

        self.assertEqual(
            form.errors,
            {
                "level": {
                    "text": "Enter a valid choice. Value(s) [Item, Division, invalid] "
                    "do not belong to the available choices. Valid choices are "
                    "[Department, Division, Series, Sub-series, Sub-sub-series, "
                    "Piece, Item]"
                }
            },
        )
        self.assertEqual(
            level_field.value,
            ["Item", "Division", "invalid"],
        )
        self.assertEqual(level_field.cleaned, None)
        self.assertEqual(level_field.choices_updated, True)
        # invalid inputs are not shown, so items is empty
        self.assertEqual(
            level_field.items,
            [],
        )
        # all inputs including invalid are shown in selected filters
        self.assertEqual(
            response.context_data.get("selected_filters"),
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

        # collection field configured choices should be empty
        self.assertEqual(collection_field.choices_updated, True)
        self.assertEqual(
            collection_field.items,
            [],
        )
        self.assertEqual(
            level_field.more_filter_choices_available,
            False,
        )
