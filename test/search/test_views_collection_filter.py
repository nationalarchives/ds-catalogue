from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase


class CatalogueSearchViewNestedCollectionFilterTests(TestCase):
    """Mainly tests the context.
    Collection filter is only available for tna group."""

    def setUp(self):
        print("Setting up test case")
        cache.clear()

    def tearDown(self):
        print("Tearing down test case")
        cache.clear()

    @patch(
        "app.search.forms.get_all_collection_choices",
        return_value=(("AMD", "AMD Collection"),),
    )
    def test_search_with_unknown_filter_returns_error(
        self, mock_get_all_collection_choices
    ):
        """Tests search with an unknown collection filter."""

        response = self.client.get(
            "/catalogue/search/?collection=DOESNOTEXIST",
        )

        context_data = response.context_data
        form = context_data.get("form")
        collection_field = form.fields["collection"]

        self.assertEqual(
            collection_field.value,
            ["DOESNOTEXIST"],
        )
        self.assertEqual(
            collection_field.cleaned,
            None,
        )

        self.assertEqual(collection_field.choices_updated, True)
        self.assertEqual(
            collection_field.choices,
            [],
        )

        self.assertEqual(
            collection_field.error,
            {
                "text": "Enter a valid choice. Value(s) [DOESNOTEXIST] do not belong to the available choices. Valid choices are [AMD]"
            },
        )

        # should not reflect configured choices
        self.assertEqual(len(collection_field.items), 0)
        self.assertEqual(
            context_data.get("selected_filters"),
            [
                {
                    "label": "Collection: DOESNOTEXIST",
                    "href": "?",
                    "title": "Remove DOESNOTEXIST collection",
                },
            ],
        )

        self.assertTrue(response.context_data.get("filters_visible"))
        self.assertFalse(collection_field.is_visible)

    # TODO: FILTER_CHOICES_LIMIT: discuss limit with team
    # @responses.activate
    # def test_search_with_exceeding_limit_returns_error_with_no_results(
    #     self,
    # ):
    #     """Tests filter with exceeding param values."""

    #     # with valid and invalid param values
    #     response = self.client.get(
    #         "/catalogue/search/?collection=value1"
    #         "&collection=value2"
    #         "&collection=value3"
    #         "&collection=value4"
    #         "&collection=value5"
    #         "&collection=value6"
    #     )

    #     form = response.context_data.get("form")
    #     context_data = response.context_data
    #     collection_field = response.context_data.get("form").fields[
    #         "collection"
    #     ]

    #     self.assertFalse(form.is_valid())

    #     # returns None when errors present
    #     self.assertEqual(context_data.get("results"), None)

    #     self.assertEqual(
    #         form.errors,
    #         {
    #             "collection": {
    #                 "text": "Maximum filter choices exceeded. Must be 5 or fewer.",
    #             }
    #         },
    #     )
    #     self.assertEqual(
    #         collection_field.value,
    #         [
    #             "value1",
    #             "value2",
    #             "value3",
    #             "value4",
    #             "value5",
    #             "value6",
    #         ],
    #     )
    #     self.assertEqual(collection_field.cleaned, None)
    #     self.assertEqual(collection_field.choices_updated, True)
    #     # invalid inputs are not shown, so items is empty
    #     self.assertEqual(
    #         collection_field.items,
    #         [],
    #     )
    #     # all inputs including invalid are shown in selected filters
    #     print(context_data.get("selected_filters"))
    #     self.assertEqual(
    #         context_data.get("selected_filters"),
    #         [
    #             {
    #                 "label": "Collection: value1",
    #                 "href": "?collection=value2"
    #                 "&collection=value3"
    #                 "&collection=value4"
    #                 "&collection=value5"
    #                 "&collection=value6",
    #                 "title": "Remove value1 collection",
    #             },
    #             {
    #                 "label": "Collection: value2",
    #                 "href": "?collection=value1"
    #                 "&collection=value3"
    #                 "&collection=value4"
    #                 "&collection=value5"
    #                 "&collection=value6",
    #                 "title": "Remove value2 collection",
    #             },
    #             {
    #                 "label": "Collection: value3",
    #                 "href": "?collection=value1"
    #                 "&collection=value2"
    #                 "&collection=value4"
    #                 "&collection=value5"
    #                 "&collection=value6",
    #                 "title": "Remove value3 collection",
    #             },
    #             {
    #                 "label": "Collection: value4",
    #                 "href": "?collection=value1"
    #                 "&collection=value2"
    #                 "&collection=value3"
    #                 "&collection=value5"
    #                 "&collection=value6",
    #                 "title": "Remove value4 collection",
    #             },
    #             {
    #                 "label": "Collection: value5",
    #                 "href": "?collection=value1"
    #                 "&collection=value2"
    #                 "&collection=value3"
    #                 "&collection=value4"
    #                 "&collection=value6",
    #                 "title": "Remove value5 collection",
    #             },
    #             {
    #                 "label": "Collection: value6",
    #                 "href": "?collection=value1"
    #                 "&collection=value2"
    #                 "&collection=value3"
    #                 "&collection=value4"
    #                 "&collection=value5",
    #                 "title": "Remove value6 collection",
    #             },
    #         ],
    #     )
