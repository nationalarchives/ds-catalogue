from http import HTTPStatus

import responses
from django.conf import settings
from django.test import TestCase
from django.utils.encoding import force_str

from app.search.constants import MAX_FILTER_CHOICES, FieldsConstant
from app.search.forms import DynamicMultipleChoiceField


class CatalogueSearchViewCollectionMoreFilterChoicesTests(TestCase):
    """Collection filter is only available for tna group."""

    @responses.activate
    def test_search_for_more_filter_choices_available_above_limit(
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
                                "id": "C123456",
                                "source": "CAT",
                            }
                        }
                    }
                ],
                "aggregations": [
                    {
                        "name": "longCollection",
                        "entries": [
                            {"value": "BT", "doc_count": 50},
                            {"value": "WO", "doc_count": 35},
                            {"value": "ADM", "doc_count": 5},
                            {"value": "HO", "doc_count": 5},
                            {"value": "C", "doc_count": 5},
                            {"value": "AIR", "doc_count": 5},
                            {"value": "FO", "doc_count": 5},
                            {"value": "GTI", "doc_count": 5},
                            {"value": "E", "doc_count": 5},
                            {"value": "VC", "doc_count": 5},
                            {"value": "ZJ", "doc_count": 5},
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

        response = self.client.get("/catalogue/search/")

        context_data = response.context_data
        form = context_data.get("form")
        collection_field = form.fields[FieldsConstant.COLLECTION]

        # more filter choice field - i.e. collection - used in template

        self.assertEqual(len(context_data.get("results")), 1)
        self.assertEqual(MAX_FILTER_CHOICES, 10)
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
    def test_search_for_more_filter_choices_unavailable_at_limit(
        self,
    ):
        """Tests more filter choices attributes are correctly set in context when below limit"""

        # data present for input collections
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [
                    {
                        "@template": {
                            "details": {
                                "id": "C123456",
                                "source": "CAT",
                            }
                        }
                    }
                ],
                "aggregations": [
                    {
                        "name": "longCollection",
                        "entries": [
                            {"value": "BT", "doc_count": 50},
                            {"value": "WO", "doc_count": 35},
                            {"value": "ADM", "doc_count": 5},
                            {"value": "HO", "doc_count": 5},
                            {"value": "C", "doc_count": 5},
                            {"value": "AIR", "doc_count": 5},
                            {"value": "FO", "doc_count": 5},
                            {"value": "GTI", "doc_count": 5},
                            {"value": "E", "doc_count": 5},
                            {"value": "VC", "doc_count": 5},
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

        response = self.client.get("/catalogue/search/")

        context_data = response.context_data
        form = context_data.get("form")
        collection_field = form.fields[FieldsConstant.COLLECTION]

        # more filter choice field - i.e. collection - used in template

        self.assertEqual(len(context_data.get("results")), 1)
        self.assertEqual(MAX_FILTER_CHOICES, 10)
        self.assertEqual(
            collection_field.more_filter_choices_available,
            False,
        )
        self.assertEqual(collection_field.more_filter_choices_text, "")
        self.assertEqual(
            collection_field.more_filter_choices_url,
            "",
        )

    @responses.activate
    def test_search_for_more_filter_choices_unavailable_below_limit(
        self,
    ):
        """Tests more filter choices attributes are correctly set in context when below limit"""

        # data present for input collections
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [
                    {
                        "@template": {
                            "details": {
                                "id": "C123456",
                                "source": "CAT",
                            }
                        }
                    }
                ],
                "aggregations": [
                    {
                        "name": "longCollection",
                        "entries": [
                            {"value": "BT", "doc_count": 50},
                            {"value": "WO", "doc_count": 35},
                            {"value": "ADM", "doc_count": 5},
                            {"value": "HO", "doc_count": 5},
                            {"value": "C", "doc_count": 5},
                            {"value": "AIR", "doc_count": 5},
                            {"value": "FO", "doc_count": 5},
                            {"value": "GTI", "doc_count": 5},
                            {"value": "E", "doc_count": 5},
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

        response = self.client.get("/catalogue/search/")

        context_data = response.context_data
        form = context_data.get("form")
        collection_field = form.fields[FieldsConstant.COLLECTION]

        # more filter choice field - i.e. collection - used in template

        self.assertEqual(len(context_data.get("results")), 1)
        self.assertEqual(MAX_FILTER_CHOICES, 10)
        self.assertEqual(
            collection_field.more_filter_choices_available,
            False,
        )
        self.assertEqual(collection_field.more_filter_choices_text, "")
        self.assertEqual(
            collection_field.more_filter_choices_url,
            "",
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
                "aggregations": [
                    {
                        "name": "longCollection",
                        "entries": [
                            {"value": "BT", "doc_count": 50},
                            {"value": "WO", "doc_count": 35},
                            {"value": "ADM", "doc_count": 20},
                            {"value": "CO", "doc_count": 15},
                            {"value": "Y", "doc_count": 15},
                            {"value": "YHC", "doc_count": 1},
                            {"value": "YHL", "doc_count": 1},
                            {"value": "YBBK", "doc_count": 1},
                            {"value": "YHNN", "doc_count": 1},
                            {"value": "YFLS", "doc_count": 1},
                            {"value": "YHEA", "doc_count": 1},
                            {"value": "YWAR", "doc_count": 1},
                            {"value": "YBAL", "doc_count": 1},
                            {"value": "YBLU", "doc_count": 1},
                            {"value": "YOWE", "doc_count": 1},
                            {"value": "YLG", "doc_count": 1},
                            {"value": "YBLK", "doc_count": 1},
                            {"value": "CSPR", "doc_count": 10},
                            {"value": "J", "doc_count": 5},
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
        response = self.client.get("/catalogue/search/?filter_list=longCollection")

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
                {"text": "BT - Board of Trade and successors (50)", "value": "BT"},
                {
                    "text": "WO - War Office, Armed Forces, Judge Advocate General, and related bodies (35)",
                    "value": "WO",
                },
                {
                    "text": "ADM - Admiralty, Navy, Royal Marines, and Coastguard (20)",
                    "value": "ADM",
                },
                {
                    "text": "CO - Colonial Office, Commonwealth and Foreign and Commonwealth Offices (15)",
                    "value": "CO",
                },
                {
                    "text": "Y - UK Parliament (15)",
                    "value": "Y",
                },
                {
                    "text": "CSPR - Civil Service Pay Research Unit (10)",
                    "value": "CSPR",
                },
                {"text": "J - Supreme Court of Judicature (5)", "value": "J"},
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
        self.assertIn("""<input type="hidden" name="group" value="tna">""", html)
        self.assertNotIn("""<input type="hidden" name="q" """, html)
        self.assertNotIn("""<input type="hidden" name="sort" """, html)
        self.assertIn("""<input type="hidden" name="display" value="list">""", html)
        self.assertNotIn("""<input type="hidden" name="online" """, html)
        self.assertNotIn("""<input type="hidden" name="collection" """, html)
        self.assertNotIn(
            """<div class="tna-checkboxes__item tna-checkboxes__item--parent">""", html
        )
        self.assertIn(
            """<input type="checkbox" id="id_collection-Y" value="Y" name="collection">""",
            html,
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
            "&subject=Army"
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
                "&subject=Army"
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
        self.assertIn("""<input type="hidden" name="group" value="tna">""", html)
        self.assertIn("""<input type="hidden" name="q" value="ufo">""", html)
        self.assertIn("""<input type="hidden" name="sort" value="title:asc">""", html)
        self.assertIn("""<input type="hidden" name="display" value="list">""", html)
        self.assertIn("""<input type="hidden" name="online" value="true">""", html)
        self.assertIn("""<input type="hidden" name="level" value="Item">""", html)
        self.assertIn("""<input type="hidden" name="level" value="Piece">""", html)
        self.assertIn("""<input type="hidden" name="subject" value="Army">""", html)
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

    @responses.activate
    def test_search_for_filter_list_param_with_collection_param(
        self,
    ):
        """Tests search for filter list param with collection param"""

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
                            # Special case: api returns parent entry "Y" with zero doc_count
                            {"value": "Y", "doc_count": 0},
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

        response = self.client.get(
            "/catalogue/search/?filter_list=longCollection&collection=BT"
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
            ("?collection=BT"),
        )
        self.assertIsInstance(
            mfc_field,
            DynamicMultipleChoiceField,
        )
        self.assertEqual(
            mfc_field.name,
            FieldsConstant.COLLECTION,
        )

        # Special case: api response that includes parent with doc_count 0 is removed
        self.assertEqual(
            mfc_field.items,
            [
                {
                    "text": "BT - Board of Trade and successors (50)",
                    "value": "BT",
                    "checked": True,
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

        # test hidden inputs
        self.assertNotIn("""<input type="hidden" name="collection" """, html)

    @responses.activate
    def test_search_for_filter_list_param_with_parent_parliament_archive(
        self,
    ):
        """Test search for filter list param with parent parliament archive 'Y'"""

        # 0 results for long filter
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "aggregations": [
                    {
                        "name": "longCollection",
                        "entries": [
                            {"value": "Y", "doc_count": 100},
                            {"value": "YHC", "doc_count": 50},
                            {"value": "YHL", "doc_count": 50},
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

        response = self.client.get(
            "/catalogue/search/?filter_list=longCollection&collection=Y"
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
            ("?collection=Y"),
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
                {"text": "YHC - Records of the House of Commons (50)", "value": "YHC"},
                {
                    "text": "YHL - Records of the House of Commons; Records of the House of Lords (50)",
                    "value": "YHL",
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

        # test hidden inputs
        # parent collection filter for parliamentary archives is not visible for selection, show it as hidden
        self.assertIn("""<input type="hidden" name="collection" value="Y">""", html)

    @responses.activate
    def test_search_for_filter_list_param_with_child_parliament_archive_without_parent(
        self,
    ):
        """Test search for filter list param with child parliament archive without parent"""

        # 0 results for long filter
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "aggregations": [
                    {
                        "name": "longCollection",
                        "entries": [
                            {"value": "Y", "doc_count": 100},
                            {"value": "YHC", "doc_count": 50},
                            {"value": "YHL", "doc_count": 50},
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

        response = self.client.get(
            "/catalogue/search/?filter_list=longCollection&collection=YHC&collection=YHL"
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
            ("?collection=YHC&collection=YHL"),
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
                    "text": "YHC - Records of the House of Commons (50)",
                    "value": "YHC",
                    "checked": True,
                },
                {
                    "text": "YHL - Records of the House of Commons; Records of the House of Lords (50)",
                    "value": "YHL",
                    "checked": True,
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

        # test hidden inputs
        # parent collection filter for parliamentary archives is not visible for selection, show it as hidden
        self.assertIn("""<input type="hidden" name="collection" value="Y">""", html)
