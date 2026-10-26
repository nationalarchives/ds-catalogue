from http import HTTPStatus
from unittest.mock import patch

import responses
from django.conf import settings
from django.test import TestCase

from app.search.constants import FieldsConstant


class CatalogueSearchViewNestedCollectionFilterTests(TestCase):
    """Mainly tests the context. Nested Collection filter i.e. Parliamentary Archives is
    only available for tna group."""

    @responses.activate
    def test_search_with_no_filters_returns_parliamentary_archives_parent_collection_without_children(
        self,
    ):
        """Test search with no filters shows parliamentary archives parent collection."""

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
                    },
                    {
                        "@template": {
                            "details": {
                                "id": "2ed5c89fa72c4c65bcc25d58c2b64c84",
                                "referenceNumber": "YHL/PO/DC/CP/1/6",
                            }
                        }
                    },
                ],
                "aggregations": [
                    {
                        "name": "longCollection",
                        # api returns all collections including nested child collections
                        "entries": [
                            {"value": "BT", "doc_count": 50},
                            {"value": "YHL", "doc_count": 3},
                            {"value": "Y", "doc_count": 15},
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
                        ],
                        "total": 100,
                        "other": 0,
                    }
                ],
                "buckets": [
                    {
                        "name": "group",
                        "entries": [
                            {"value": "tna", "count": 100},
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

        self.assertEqual(len(context_data.get("results")), 2)

        self.assertEqual(
            collection_field.value,
            [],
        )
        self.assertEqual(
            collection_field.cleaned,
            [],
        )
        self.assertEqual(collection_field.choices_updated, True)
        self.assertEqual(
            collection_field.items,
            [
                {"text": "BT - Board of Trade and successors (50)", "value": "BT"},
                {
                    "text": "Y - UK Parliament (15)",
                    "value": "Y",
                    "is_parent": True,
                    "hint": "select to show more specific collections",
                },
            ],
        )
        self.assertEqual(
            context_data.get("selected_filters"),
            [],
        )
        self.assertEqual(
            collection_field.more_filter_choices_available,
            False,
        )
        self.assertEqual(collection_field.more_filter_choices_url, "")
        self.assertEqual(collection_field.more_filter_choices_text, "")

        self.assertTrue(response.context_data.get("filters_visible"))
        self.assertTrue(collection_field.is_visible)

    @responses.activate
    def test_search_with_non_parliamentary_archives_filter_applied_removes_parent_empty_collection(
        self,
    ):
        """Test that applying a non-parliamentary archives filter removes the parent collection since it is returned with 0 hits."""

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
                    },
                ],
                "aggregations": [
                    {
                        "name": "longCollection",
                        "entries": [
                            {"value": "BT", "doc_count": 50},
                            # api returns parent collection with 0 hits
                            {"value": "Y", "doc_count": 0},
                        ],
                        "total": 100,
                        "other": 0,
                    }
                ],
                "buckets": [
                    {
                        "name": "group",
                        "entries": [
                            {"value": "tna", "count": 100},
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

        response = self.client.get("/catalogue/search/?collection=BT")

        context_data = response.context_data
        form = context_data.get("form")
        collection_field = form.fields[FieldsConstant.COLLECTION]

        self.assertEqual(len(context_data.get("results")), 1)

        self.assertEqual(
            collection_field.value,
            ["BT"],
        )
        self.assertEqual(
            collection_field.cleaned,
            ["BT"],
        )
        self.assertEqual(collection_field.choices_updated, True)
        self.assertEqual(
            collection_field.items,
            [
                {
                    "text": "BT - Board of Trade and successors (50)",
                    "value": "BT",
                    "checked": True,
                },
            ],
        )
        self.assertEqual(
            context_data.get("selected_filters"),
            [
                {
                    "label": "Collection: BT - Board of Trade and successors",
                    "href": "?",
                    "title": "Remove BT - Board of Trade and successors collection",
                }
            ],
        )
        self.assertEqual(
            collection_field.more_filter_choices_available,
            False,
        )
        self.assertEqual(collection_field.more_filter_choices_url, "")
        self.assertEqual(collection_field.more_filter_choices_text, "")

        self.assertTrue(response.context_data.get("filters_visible"))
        self.assertTrue(collection_field.is_visible)

    @patch("app.lib.api.logger")
    @responses.activate
    def test_search_with_selected_parliamentary_archives_parent_collection(
        self,
        mock_logger,
    ):
        """Test search with selected parliamentary archives parent collection"""

        # data present for input collections
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [
                    {
                        "@template": {
                            "details": {
                                "id": "6c61ba7c39e84c98a9ca91fe9680737f",
                                "referenceNumber": "YHL/PO/DC/CP/1/1",
                            }
                        }
                    },
                    {
                        "@template": {
                            "details": {
                                "id": "2ed5c89fa72c4c65bcc25d58c2b64c84",
                                "referenceNumber": "YHL/PO/DC/CP/1/6",
                            }
                        }
                    },
                ],
                "aggregations": [
                    {
                        "name": "longCollection",
                        "entries": [
                            {"value": "Y", "doc_count": 15},
                            {"value": "YHL", "doc_count": 10},
                            {"value": "YHC", "doc_count": 5},
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
                        ],
                        "total": 100,
                        "other": 0,
                    }
                ],
                "buckets": [
                    {
                        "name": "group",
                        "entries": [
                            {"value": "tna", "count": 100},
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

        response = self.client.get("/catalogue/search/?collection=Y")

        context_data = response.context_data
        form = context_data.get("form")
        collection_field = form.fields[FieldsConstant.COLLECTION]

        self.assertEqual(len(context_data.get("results")), 2)

        self.assertEqual(
            collection_field.value,
            ["Y"],
        )
        self.assertEqual(
            collection_field.cleaned,
            ["Y"],
        )

        self.assertEqual(collection_field.choices_updated, True)
        self.assertEqual(
            collection_field.items,
            [
                {
                    "text": "Y - UK Parliament (15)",
                    "value": "Y",
                    "checked": True,
                    "is_parent": True,
                    "hint": "select to show more specific collections",
                    "more_filter_choices_available": True,
                    "more_filter_choices_text": "See more UK Parliament collections",
                    "more_filter_choices_url": "?collection=Y&filter_list=longCollection&collection=Y",
                    "children": [
                        {
                            "text": "YHL - Records of the House of Commons; Records of the House of Lords (10)",
                            "value": "YHL",
                            "is_child": True,
                        },
                        {
                            "text": "YHC - Records of the House of Commons (5)",
                            "value": "YHC",
                            "is_child": True,
                        },
                        {
                            "text": "YBBK - The Beaverbrook Papers (1)",
                            "value": "YBBK",
                            "is_child": True,
                        },
                        {
                            "text": "YHNN - Papers of Sir Patrick Joseph Henry Hannon MP (1874-1963) (1)",
                            "value": "YHNN",
                            "is_child": True,
                        },
                        {
                            "text": "YFLS - Papers of Frances Stevenson (1888-1972) (1)",
                            "value": "YFLS",
                            "is_child": True,
                        },
                        {
                            "text": "YHEA - Papers of Timothy Michael Healy, KC (1)",
                            "value": "YHEA",
                            "is_child": True,
                        },
                        {
                            "text": "YWAR - The Wargrave Papers (1)",
                            "value": "YWAR",
                            "is_child": True,
                        },
                        {
                            "text": "YBAL - Papers of Harold Harrington Balfour (1897-1988, 1st Baron Balfour of Inchrye (1)",
                            "value": "YBAL",
                            "is_child": True,
                        },
                        {
                            "text": "YBLU - Papers of Ralph David Blumenfeld (1)",
                            "value": "YBLU",
                            "is_child": True,
                        },
                        {
                            "text": "YOWE - The Owen Papers (1)",
                            "value": "YOWE",
                            "is_child": True,
                        },
                        {
                            "text": "YLG - The Lloyd George Papers (1)",
                            "value": "YLG",
                            "is_child": True,
                        },
                        {
                            "text": "YBLK - Papers of Robert Norman William Blake (1916-2003, Baron Blake of Braydeston (1)",
                            "value": "YBLK",
                            "is_child": True,
                        },
                    ],
                }
            ],
        )
        self.assertEqual(
            context_data.get("selected_filters"),
            [
                {
                    "label": "Collection: Y - UK Parliament",
                    "href": "?",
                    "title": "Remove Y - UK Parliament collection",
                }
            ],
        )
        self.assertEqual(
            collection_field.more_filter_choices_available,
            False,
        )
        self.assertEqual(collection_field.more_filter_choices_url, "")
        self.assertEqual(collection_field.more_filter_choices_text, "")

        self.assertTrue(response.context_data.get("filters_visible"))
        self.assertTrue(collection_field.is_visible)

        mock_logger.debug.assert_called_with(
            "https://rosetta.test/data/search?"
            "filter=group%3Atna"
            "&filter=collection%3AY"
            "&aggs=level"
            "&aggs=longCollection"
            "&aggs=closure"
            "&aggs=longSubject"
            "&aggs=referenceNumber"
            "&q=%2A"
            "&size=20"
            "&from=0"
        )

    @patch("app.lib.api.logger")
    @responses.activate
    def test_search_with_selected_parliamentary_archives_parent_and_child_collection(
        self,
        mock_logger,
    ):
        """Test search with selected parliamentary archives parent and child collection"""

        # data present for input collections
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [
                    {
                        "@template": {
                            "details": {
                                "id": "6c61ba7c39e84c98a9ca91fe9680737f",
                                "referenceNumber": "YHL/PO/DC/CP/1/1",
                            }
                        }
                    },
                    {
                        "@template": {
                            "details": {
                                "id": "2ed5c89fa72c4c65bcc25d58c2b64c84",
                                "referenceNumber": "YHL/PO/DC/CP/1/6",
                            }
                        }
                    },
                ],
                "aggregations": [
                    {
                        "name": "longCollection",
                        "entries": [
                            {"value": "Y", "doc_count": 15},
                            {"value": "YHL", "doc_count": 10},
                            {"value": "YHC", "doc_count": 5},
                        ],
                        "total": 100,
                        "other": 0,
                    }
                ],
                "buckets": [
                    {
                        "name": "group",
                        "entries": [
                            {"value": "tna", "count": 100},
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

        response = self.client.get(
            "/catalogue/search/?collection=Y&collection=YHL&collection=YHC"
        )

        context_data = response.context_data
        form = context_data.get("form")
        collection_field = form.fields[FieldsConstant.COLLECTION]

        self.assertEqual(len(context_data.get("results")), 2)

        self.assertEqual(
            collection_field.value,
            ["Y", "YHL", "YHC"],
        )
        self.assertEqual(
            collection_field.cleaned,
            ["Y", "YHL", "YHC"],
        )

        self.assertEqual(collection_field.choices_updated, True)

        self.assertEqual(
            collection_field.items,
            [
                {
                    "text": "Y - UK Parliament (15)",
                    "value": "Y",
                    "checked": True,
                    "is_parent": True,
                    "children": [
                        {
                            "text": "YHL - Records of the House of Commons; Records of the House of Lords (10)",
                            "value": "YHL",
                            "checked": True,
                            "is_child": True,
                        },
                        {
                            "text": "YHC - Records of the House of Commons (5)",
                            "value": "YHC",
                            "checked": True,
                            "is_child": True,
                        },
                    ],
                    # "hint": "select to show more specific collections",
                    # "more_filter_choices_available": True,
                    # "more_filter_choices_text": "See more UK Parliament collections",
                    # "more_filter_choices_url": "?collection=Y&collection=YHL&collection=YHC&filter_list=longCollection",
                }
            ],
        )
        self.assertEqual(
            context_data.get("selected_filters"),
            [
                {
                    "label": "Collection: Y - UK Parliament",
                    "href": "?collection=YHL&collection=YHC",
                    "title": "Remove Y - UK Parliament collection",
                },
                {
                    "label": "Collection: YHL - Records of the House of Commons; Records of the House of Lords",
                    "href": "?collection=Y&collection=YHC",
                    "title": "Remove YHL - Records of the House of Commons; Records of the House of Lords collection",
                },
                {
                    "label": "Collection: YHC - Records of the House of Commons",
                    "href": "?collection=Y&collection=YHL",
                    "title": "Remove YHC - Records of the House of Commons collection",
                },
            ],
        )
        self.assertEqual(
            collection_field.more_filter_choices_available,
            False,
        )
        self.assertEqual(collection_field.more_filter_choices_url, "")
        self.assertEqual(collection_field.more_filter_choices_text, "")

        self.assertTrue(response.context_data.get("filters_visible"))
        self.assertTrue(collection_field.is_visible)

        # Note: collection:Y is not included when its child collections (YHL and YHC) are selected
        mock_logger.debug.assert_called_with(
            "https://rosetta.test/data/search?"
            "filter=group%3Atna"
            "&filter=collection%3AYHL"
            "&filter=collection%3AYHC"
            "&aggs=level"
            "&aggs=longCollection"
            "&aggs=closure"
            "&aggs=longSubject"
            "&aggs=referenceNumber"
            "&q=%2A"
            "&size=20"
            "&from=0"
        )

    @patch("app.lib.api.logger")
    @responses.activate
    def test_search_with_selected_parliamentary_archives_returns_child_collection_without_parent(
        self,
        mock_logger,
    ):
        """Test search with selected parliamentary archives parent and child collection"""

        # data present for input collections
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [
                    {
                        "@template": {
                            "details": {
                                "id": "6c61ba7c39e84c98a9ca91fe9680737f",
                                "referenceNumber": "YHL/PO/DC/CP/1/1",
                            }
                        }
                    },
                    {
                        "@template": {
                            "details": {
                                "id": "2ed5c89fa72c4c65bcc25d58c2b64c84",
                                "referenceNumber": "YHL/PO/DC/CP/1/6",
                            }
                        }
                    },
                ],
                "aggregations": [
                    {
                        "name": "longCollection",
                        "entries": [
                            {"value": "YHL", "doc_count": 10},
                            {"value": "YHC", "doc_count": 5},
                        ],
                        "total": 100,
                        "other": 0,
                    }
                ],
                "buckets": [
                    {
                        "name": "group",
                        "entries": [
                            {"value": "tna", "count": 100},
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

        response = self.client.get(
            "/catalogue/search/?collection=Y&collection=YHL&collection=YHC"
        )

        context_data = response.context_data
        form = context_data.get("form")
        collection_field = form.fields[FieldsConstant.COLLECTION]

        self.assertEqual(len(context_data.get("results")), 2)

        self.assertEqual(
            collection_field.value,
            ["Y", "YHL", "YHC"],
        )
        self.assertEqual(
            collection_field.cleaned,
            ["Y", "YHL", "YHC"],
        )

        self.assertEqual(collection_field.choices_updated, True)

        self.assertEqual(
            collection_field.items,
            [
                {"text": "Y - UK Parliament (0)", "value": "Y", "checked": True},
                {
                    "text": "YHL - Records of the House of Commons; Records of the House of Lords (0)",
                    "value": "YHL",
                    "checked": True,
                },
                {
                    "text": "YHC - Records of the House of Commons (0)",
                    "value": "YHC",
                    "checked": True,
                },
            ],
        )
        self.assertEqual(
            context_data.get("selected_filters"),
            [
                {
                    "label": "Collection: Y - UK Parliament",
                    "href": "?collection=YHL&collection=YHC",
                    "title": "Remove Y - UK Parliament collection",
                },
                {
                    "label": "Collection: YHL - Records of the House of Commons; Records of the House of Lords",
                    "href": "?collection=Y&collection=YHC",
                    "title": "Remove YHL - Records of the House of Commons; Records of the House of Lords collection",
                },
                {
                    "label": "Collection: YHC - Records of the House of Commons",
                    "href": "?collection=Y&collection=YHL",
                    "title": "Remove YHC - Records of the House of Commons collection",
                },
            ],
        )
        self.assertEqual(
            collection_field.more_filter_choices_available,
            False,
        )
        self.assertEqual(collection_field.more_filter_choices_url, "")
        self.assertEqual(collection_field.more_filter_choices_text, "")

        self.assertTrue(response.context_data.get("filters_visible"))
        self.assertTrue(collection_field.is_visible)

        # Note: collection:Y is not included when its child collections (YHL and YHC) are selected
        mock_logger.debug.assert_called_with(
            "https://rosetta.test/data/search?"
            "filter=group%3Atna"
            "&filter=collection%3AYHL"
            "&filter=collection%3AYHC"
            "&aggs=level"
            "&aggs=longCollection"
            "&aggs=closure"
            "&aggs=longSubject"
            "&aggs=referenceNumber"
            "&q=%2A"
            "&size=20"
            "&from=0"
        )
