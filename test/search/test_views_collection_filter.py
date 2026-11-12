from http import HTTPStatus

import responses
from django.conf import settings
from django.test import TestCase


class CatalogueSearchViewNestedCollectionFilterTests(TestCase):
    """Mainly tests the context.
    Collection filter is only available for tna group."""

    @responses.activate
    def test_search_with_unknown_filter_returns_no_results_no_aggs(
        self,
    ):
        """Tests configure choices do not appear when no data is returned
        and also no aggregations returned for the input filter value."""

        # no data for input collection, no aggregations returned
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
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
                "aggregations": [
                    {
                        # Special case: api returns single entry for parent "Y" with zero doc_count as dict
                        "name": "longCollection",
                        "total": 0,
                        "other": 0,
                        "entries": {"value": "Y", "doc_count": 0},
                        "Y": {"name": "Y", "total": 0},
                    }
                ],
            },
            status=HTTPStatus.OK,
        )

        response = self.client.get(
            "/catalogue/search/?collection=DOESNOTEXIST",
        )

        context_data = response.context_data
        form = context_data.get("form")
        collection_field = form.fields["collection"]
        level_field = form.fields["level"]

        self.assertEqual(len(context_data.get("results")), 0)

        self.assertEqual(
            collection_field.value,
            ["DOESNOTEXIST"],
        )
        self.assertEqual(
            collection_field.cleaned,
            ["DOESNOTEXIST"],
        )

        self.assertEqual(collection_field.choices_updated, True)
        self.assertEqual(
            collection_field.choices,
            [("DOESNOTEXIST", "DOESNOTEXIST (0)", None)],
        )

        # should not reflect configured choices
        self.assertEqual(len(collection_field.items), 1)
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

        self.assertEqual(level_field.choices_updated, True)
        # should not reflect configured choices
        self.assertEqual(len(level_field.items), 0)
        self.assertEqual(
            collection_field.more_filter_choices_available,
            False,
        )

        self.assertTrue(response.context_data.get("filters_visible"))
        self.assertTrue(collection_field.is_visible)

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
