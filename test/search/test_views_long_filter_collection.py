from http import HTTPStatus

import responses
from app.search.constants import FieldsConstant
from app.search.forms import DynamicMultipleChoiceField
from django.conf import settings
from django.test import TestCase
from django.utils.encoding import force_str


class CatalogueSearchViewCollectionMoreFilterChoicesTests(TestCase):
    """Collection filter is only available for tna group."""

    @responses.activate
    def test_search_for_more_filter_choices_attributes_without_filters(
        self,
    ):
        """Tests more filter choices attributes are correctly set in context"""

        # data present for input collections
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
                        "name": "collection",
                        "entries": [
                            {"value": "BT", "doc_count": 50},
                            {"value": "WO", "doc_count": 35},
                        ],
                        "total": 100,
                        "other": 50,
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

        response = self.client.get("/catalogue/search/")

        context_data = response.context_data
        form = context_data.get("form")
        collection_field = form.fields[FieldsConstant.COLLECTION]

        # more filter choice field - i.e. collection - used in template

        self.assertEqual(len(context_data.get("results")), 1)
        self.assertEqual(
            collection_field.more_filter_choices_available,
            True,
        )
        self.assertEqual(
            collection_field.more_filter_choices_text, "See more collections"
        )
        self.assertEqual(
            collection_field.more_filter_choices_url,
            "?filter_list=longCollection",
        )

    @responses.activate
    def test_search_for_filter_list_param_without_other_params(
        self,
    ):
        """Tests long filters only - without other params"""

        # 0 results for long filter
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [],
                "aggregations": [
                    {
                        "name": "longCollection",
                        "entries": [
                            {"value": "BT", "doc_count": 50},
                            {"value": "WO", "doc_count": 35},
                        ],
                        "total": 28083703,
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
                    "total": 10000,
                    "results": 0,
                },
            },
            status=HTTPStatus.OK,
        )

        # input long filter without other params
        response = self.client.get(
            "/catalogue/search/?filter_list=longCollection"
        )

        context_data = response.context_data
        form = context_data.get("form")
        html = force_str(response.content)
        # more filter choice field - i.e. collection - used in template
        mfc_field = context_data.get("mfc_field")

        self.assertEqual(len(context_data.get("results")), 0)
        self.assertTrue(form.is_valid())

        self.assertEqual(
            context_data.get("mfc_cancel_and_return_to_search_url"),
            ("?"),
        )
        self.assertIsInstance(
            mfc_field,
            DynamicMultipleChoiceField,
        )
        self.assertEqual(
            mfc_field.name,
            FieldsConstant.COLLECTION,
        )
        self.assertEqual(
            mfc_field.items,
            [
                {
                    "text": "BT - Board of Trade and successors (50)",
                    "value": "BT",
                },
                {
                    "text": "WO - War Office, Armed Forces, Judge Advocate General, and related bodies (35)",
                    "value": "WO",
                },
            ],
        )
        self.assertEqual(
            mfc_field.more_filter_choices_available,
            False,
        )
        self.assertEqual(
            mfc_field.more_filter_choices_url,
            "",
        )

        # test hidden inputs to retain other filters in form
        self.assertIn(
            """<input type="hidden" name="group" value="tna">""", html
        )
        self.assertNotIn("""<input type="hidden" name="q" """, html)
        self.assertNotIn("""<input type="hidden" name="sort" """, html)
        self.assertIn(
            """<input type="hidden" name="display" value="list">""", html
        )
        self.assertNotIn("""<input type="hidden" name="online" """, html)

    @responses.activate
    def test_search_for_filter_list_param_with_other_params(
        self,
    ):
        """Tests long filters are correctly processed with other params"""

        # 0 results for long filter
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [],
                "aggregations": [
                    {
                        "name": "longCollection",
                        "entries": [
                            {"value": "BT", "doc_count": 50},
                            {"value": "WO", "doc_count": 35},
                        ],
                        "total": 28083703,
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
                    "total": 10000,
                    "results": 0,
                },
            },
            status=HTTPStatus.OK,
        )

        # input long filter with other params
        response = self.client.get(
            "/catalogue/search/?"
            "q=ufo"
            "&sort=title:asc"
            "&online=true"
            "&level=Item"
            "&level=Piece"
            "&covering_date_from-year=1940"
            "&filter_list=longCollection"
        )

        context_data = response.context_data
        form = context_data.get("form")
        html = force_str(response.content)
        # more filter choice field - i.e. collection - used in template
        mfc_field = context_data.get("mfc_field")

        self.assertEqual(len(context_data.get("results")), 0)
        self.assertTrue(form.is_valid())

        self.assertEqual(
            context_data.get("mfc_cancel_and_return_to_search_url"),
            (
                "?q=ufo"
                "&sort=title%3Aasc"
                "&online=true"
                "&level=Item"
                "&level=Piece"
                "&covering_date_from-year=1940"
            ),
        )
        self.assertIsInstance(
            mfc_field,
            DynamicMultipleChoiceField,
        )
        self.assertEqual(
            mfc_field.name,
            FieldsConstant.COLLECTION,
        )
        self.assertEqual(
            mfc_field.items,
            [
                {
                    "text": "BT - Board of Trade and successors (50)",
                    "value": "BT",
                },
                {
                    "text": "WO - War Office, Armed Forces, Judge Advocate General, and related bodies (35)",
                    "value": "WO",
                },
            ],
        )
        self.assertEqual(
            mfc_field.more_filter_choices_available,
            False,
        )
        self.assertEqual(
            mfc_field.more_filter_choices_url,
            "",
        )

        # test hidden inputs to retain other filters in form
        self.assertIn(
            """<input type="hidden" name="group" value="tna">""", html
        )
        self.assertIn("""<input type="hidden" name="q" value="ufo">""", html)
        self.assertIn(
            """<input type="hidden" name="sort" value="title:asc">""", html
        )
        self.assertIn(
            """<input type="hidden" name="display" value="list">""", html
        )
        self.assertIn(
            """<input type="hidden" name="online" value="true">""", html
        )
        self.assertIn(
            """<input type="hidden" name="level" value="Item">""", html
        )
        self.assertIn(
            """<input type="hidden" name="level" value="Piece">""", html
        )
        self.assertIn(
            """<input type="hidden" name="covering_date_from-year" value="1940">""",
            html,
        )
        self.assertNotIn(
            """<input type="hidden" name="covering_date_from-month" """, html
        )
        self.assertNotIn(
            """<input type="hidden" name="covering_date_from-day" """, html
        )
