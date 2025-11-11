from http import HTTPStatus

import responses
from app.search.constants import FieldsConstant
from app.search.forms import DynamicMultipleChoiceField
from django.conf import settings
from django.test import TestCase
from django.utils.encoding import force_str


class CatalogueSearchViewHeldByMoreFilterChoicesTests(TestCase):
    """HeldBy filter is only available for Non Tna group."""

    @responses.activate
    def test_search_for_more_filter_choices_attributes_without_filters(
        self,
    ):
        """Tests more filter choices attributes are correctly set in context"""

        # data present for input held by values
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
                        "name": "heldBy",
                        "entries": [
                            {"value": "Lancashire Archives", "doc_count": 50},
                            {"value": "Freud Museum", "doc_count": 35},
                        ],
                        "total": 100,
                        "other": 50,
                    }
                ],
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

        context_data = response.context_data
        form = context_data.get("form")
        held_by_field = form.fields[FieldsConstant.HELD_BY]

        # more filter choice field - i.e. held by - used in template

        self.assertEqual(len(context_data.get("results")), 1)
        self.assertEqual(
            held_by_field.more_filter_choices_available,
            True,
        )
        self.assertEqual(
            held_by_field.more_filter_choices_text, "See more held by"
        )
        self.assertEqual(
            held_by_field.more_filter_choices_url,
            "?group=nonTna&filter_list=longHeldBy",
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
                        "name": "longHeldBy",
                        "entries": [
                            {"value": "Lancashire Archives", "doc_count": 50},
                            {"value": "Freud Museum", "doc_count": 35},
                        ],
                        "total": 28083703,
                        "other": 0,
                    }
                ],
                "buckets": [
                    {
                        "name": "group",
                        "entries": [
                            {"value": "nonTna", "count": 1},
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
            "/catalogue/search/?group=nonTna&filter_list=longHeldBy"
        )

        context_data = response.context_data
        form = context_data.get("form")
        html = force_str(response.content)
        # more filter choice field - i.e. held by - used in template
        mfc_field = context_data.get("mfc_field")

        self.assertEqual(len(context_data.get("results")), 0)
        self.assertTrue(form.is_valid())

        self.assertEqual(
            context_data.get("mfc_cancel_and_return_to_search_url"),
            ("?group=nonTna"),
        )
        self.assertIsInstance(
            mfc_field,
            DynamicMultipleChoiceField,
        )
        self.assertEqual(
            mfc_field.name,
            FieldsConstant.HELD_BY,
        )
        self.assertEqual(
            mfc_field.items,
            [
                {
                    "text": "Lancashire Archives (50)",
                    "value": "Lancashire Archives",
                },
                {
                    "text": "Freud Museum (35)",
                    "value": "Freud Museum",
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
            """<input type="hidden" name="group" value="nonTna">""", html
        )
        self.assertNotIn("""<input type="hidden" name="q" """, html)
        self.assertNotIn("""<input type="hidden" name="sort" """, html)
        self.assertIn(
            """<input type="hidden" name="display" value="list">""", html
        )

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
                        "name": "longHeldBy",
                        "entries": [
                            {"value": "Lancashire Archives", "doc_count": 50},
                            {"value": "Freud Museum", "doc_count": 35},
                        ],
                        "total": 28083703,
                        "other": 0,
                    }
                ],
                "buckets": [
                    {
                        "name": "group",
                        "entries": [
                            {"value": "nonTna", "count": 1},
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
            "/catalogue/search/?group=nonTna"
            "&q=ufo"
            "&sort=title:asc"
            "&covering_date_from-year=1940"
            "&filter_list=longHeldBy"
        )

        context_data = response.context_data
        form = context_data.get("form")
        html = force_str(response.content)
        # more filter choice field - i.e. held by - used in template
        mfc_field = context_data.get("mfc_field")

        self.assertEqual(len(context_data.get("results")), 0)
        self.assertTrue(form.is_valid())

        self.assertEqual(
            context_data.get("mfc_cancel_and_return_to_search_url"),
            (
                "?group=nonTna"
                "&q=ufo"
                "&sort=title%3Aasc"
                "&covering_date_from-year=1940"
            ),
        )
        self.assertIsInstance(
            mfc_field,
            DynamicMultipleChoiceField,
        )
        self.assertEqual(
            mfc_field.name,
            FieldsConstant.HELD_BY,
        )
        self.assertEqual(
            mfc_field.items,
            [
                {
                    "text": "Lancashire Archives (50)",
                    "value": "Lancashire Archives",
                },
                {
                    "text": "Freud Museum (35)",
                    "value": "Freud Museum",
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
            """<input type="hidden" name="group" value="nonTna">""", html
        )
        self.assertIn("""<input type="hidden" name="q" value="ufo">""", html)
        self.assertIn(
            """<input type="hidden" name="sort" value="title:asc">""", html
        )
        self.assertIn(
            """<input type="hidden" name="display" value="list">""", html
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
