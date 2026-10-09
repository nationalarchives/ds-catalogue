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
    def test_search_with_no_filters_shows_parliamentary_archives_parent_collection(
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
                        "name": "collection",
                        "entries": [
                            {"value": "BT", "doc_count": 50},
                            {"value": "Y", "doc_count": 15},
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
                {
                    "text": "BT - Board of Trade and successors (50)",
                    "value": "BT",
                },
                {
                    "text": "Y - UK Parliament (15)",
                    "value": "Y",
                    "is_parent": True,
                    "hint": "select to show more specific collections",
                    "more_filter_choices_available": False,
                    "more_filter_choices_url": "",
                    "more_filter_choices_text": "",
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
                        "name": "collection",
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
                    "more_filter_choices_available": False,
                    "more_filter_choices_text": "",
                    "more_filter_choices_url": "",
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
            "&aggs=collection"
            "&aggs=closure"
            "&aggs=subject"
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
                        "name": "collection",
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
                    "hint": "select to show more specific collections",
                    "more_filter_choices_available": False,
                    "more_filter_choices_text": "",
                    "more_filter_choices_url": "",
                    "children": [
                        {
                            "text": "YHL - Records of the House of Commons; Records of the House of Lords (10)",
                            "value": "YHL",
                            "is_child": True,
                            "checked": True,
                        },
                        {
                            "text": "YHC - Records of the House of Commons (5)",
                            "value": "YHC",
                            "is_child": True,
                            "checked": True,
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
            "&aggs=collection"
            "&aggs=closure"
            "&aggs=subject"
            "&aggs=referenceNumber"
            "&q=%2A"
            "&size=20"
            "&from=0"
        )
