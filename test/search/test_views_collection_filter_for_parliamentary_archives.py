from http import HTTPStatus
from unittest.mock import patch

import responses
from django.conf import settings
from django.test import TestCase

from app.search.constants import MAX_FILTER_CHOICES, FieldsConstant


class CatalogueSearchViewNestedCollectionFilterTests(TestCase):
    """Mainly tests the context. Nested Collection filter i.e. Parliamentary Archives is
    only available for tna group."""

    @responses.activate
    def test_search_preserves_parliamentary_archives_parent_within_first_n_entries(
        self,
    ):
        """Test search with no filters preserves parliamentary archives parent collection
        order within the first n entries, removes child entries."""

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
                        # api returns all collections including child collections
                        # child collections are not nested under the parent Y
                        # order of entries should be preserved as returned by the API
                        # Y is within the first 10 entries
                        "entries": [
                            {"value": "BT", "doc_count": 50},
                            {"value": "YHL", "doc_count": 3},
                            {
                                "value": "Y",
                                "doc_count": 15,
                            },  # Y is within the first 10 entries
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

        # Ensure the maximum number of filter choices is within the expected limit
        self.assertLessEqual(MAX_FILTER_CHOICES, 10)

        # child entries for the "Y" collection are attached at this stage
        # order of choices are preserved as returned by the API,
        # with child entries nested under their parent collection
        # "Y" position within the first n entries is preserved
        self.assertEqual(
            collection_field.choices,
            [
                ("BT", "BT - Board of Trade and successors (50)", None),
                # "Y" collection position is preserved with child entries nested under it
                (
                    "Y",
                    "Y - UK Parliament (15)",
                    [
                        (
                            "YHL",
                            "YHL - Records of the House of Commons; Records of the House of Lords (3)",
                            None,
                        ),
                        ("YBBK", "YBBK - The Beaverbrook Papers (1)", None),
                        (
                            "YHNN",
                            "YHNN - Papers of Sir Patrick Joseph Henry Hannon MP (1874-1963) (1)",
                            None,
                        ),
                        (
                            "YFLS",
                            "YFLS - Papers of Frances Stevenson (1888-1972) (1)",
                            None,
                        ),
                        (
                            "YHEA",
                            "YHEA - Papers of Timothy Michael Healy, KC (1)",
                            None,
                        ),
                        ("YWAR", "YWAR - The Wargrave Papers (1)", None),
                        (
                            "YBAL",
                            "YBAL - Papers of Harold Harrington Balfour (1897-1988, 1st Baron Balfour of Inchrye (1)",
                            None,
                        ),
                        ("YBLU", "YBLU - Papers of Ralph David Blumenfeld (1)", None),
                        ("YOWE", "YOWE - The Owen Papers (1)", None),
                        ("YLG", "YLG - The Lloyd George Papers (1)", None),
                        (
                            "YBLK",
                            "YBLK - Papers of Robert Norman William Blake (1916-2003, Baron Blake of Braydeston (1)",
                            None,
                        ),
                    ],
                ),
            ],
        )

        self.assertNotIn("children", collection_field.items[1])

        # child entries are not included in the items list,
        # no sepecific see more link is shown for the parent collection "Y"
        self.assertEqual(
            collection_field.items,
            [
                {"text": "BT - Board of Trade and successors (50)", "value": "BT"},
                # "Y" collection is included as a parent with no child entries under it
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
    def test_search_relocates_parliamentary_archives_parent_within_first_n_entries(
        self,
    ):
        """Test search with no filters with parent outside the first n entries repositions
        the parliamentary archives parent collection within the first n entries,
        removes child entries."""

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
                        # api returns all collections including child collections
                        # child collections are not nested under the parent Y
                        # order of entries should be preserved as returned by the API
                        # Y is outside the first 10 entries
                        "entries": [
                            {"value": "BT", "doc_count": 50},
                            {"value": "WO", "doc_count": 45},
                            {"value": "ADM", "doc_count": 40},
                            {"value": "HO", "doc_count": 40},
                            {"value": "C", "doc_count": 40},
                            {"value": "PROB", "doc_count": 35},
                            {"value": "AIR", "doc_count": 35},
                            {"value": "FO", "doc_count": 35},
                            {"value": "GTI", "doc_count": 35},
                            {"value": "RAIL", "doc_count": 30},
                            {"value": "EF", "doc_count": 20},
                            {"value": "YHL", "doc_count": 3},
                            {"value": "Y", "doc_count": 15},  # outside first 10 entries
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

        # Ensure the maximum number of filter choices is within the expected limit
        self.assertLessEqual(MAX_FILTER_CHOICES, 10)

        # child entries for the "Y" collection are attached at this stage
        # order of choices are preserved as returned by the API,
        # with child entries nested under their parent collection
        # Y is within the first 10 entries
        self.assertEqual(
            collection_field.choices,
            [
                ("BT", "BT - Board of Trade and successors (50)", None),
                (
                    "WO",
                    "WO - War Office, Armed Forces, Judge Advocate General, and related bodies (45)",
                    None,
                ),
                (
                    "ADM",
                    "ADM - Admiralty, Navy, Royal Marines, and Coastguard (40)",
                    None,
                ),
                ("HO", "HO - Home Office (40)", None),
                (
                    "C",
                    "C - Chancery, the Wardrobe, Royal Household, Exchequer and various commissions (40)",
                    None,
                ),
                ("PROB", "PROB - Prerogative Court of Canterbury (35)", None),
                ("AIR", "AIR - Air Ministry and Royal Air Force records (35)", None),
                ("FO", "FO - Foreign Office (35)", None),
                ("GTI", "GTI - Grenfell Tower Inquiry (35)", None),
                # "Y" is repositioned as the 10th entry, with children nested under it
                (
                    "Y",
                    "Y - UK Parliament (15)",
                    [
                        (
                            "YHL",
                            "YHL - Records of the House of Commons; Records of the House of Lords (3)",
                            None,
                        ),
                        ("YBBK", "YBBK - The Beaverbrook Papers (1)", None),
                        (
                            "YHNN",
                            "YHNN - Papers of Sir Patrick Joseph Henry Hannon MP (1874-1963) (1)",
                            None,
                        ),
                        (
                            "YFLS",
                            "YFLS - Papers of Frances Stevenson (1888-1972) (1)",
                            None,
                        ),
                        (
                            "YHEA",
                            "YHEA - Papers of Timothy Michael Healy, KC (1)",
                            None,
                        ),
                        ("YWAR", "YWAR - The Wargrave Papers (1)", None),
                        (
                            "YBAL",
                            "YBAL - Papers of Harold Harrington Balfour (1897-1988, 1st Baron Balfour of Inchrye (1)",
                            None,
                        ),
                        ("YBLU", "YBLU - Papers of Ralph David Blumenfeld (1)", None),
                        ("YOWE", "YOWE - The Owen Papers (1)", None),
                        ("YLG", "YLG - The Lloyd George Papers (1)", None),
                        (
                            "YBLK",
                            "YBLK - Papers of Robert Norman William Blake (1916-2003, Baron Blake of Braydeston (1)",
                            None,
                        ),
                    ],
                ),
                # "RAIL" onwards are positioned after "Y"
                (
                    "RAIL",
                    "RAIL - Pre-nationalisation railway companies, pre-nationalisation canal and related companies (30)",
                    None,
                ),
                ("EF", "EF - Health and Safety Commission and Executive (20)", None),
            ],
        )

        # child entries are not included in the items list,
        # Y is within the first 10 entries
        self.assertEqual(
            collection_field.items,
            [
                {"text": "BT - Board of Trade and successors (50)", "value": "BT"},
                {
                    "text": "WO - War Office, Armed Forces, Judge Advocate General, and related bodies (45)",
                    "value": "WO",
                },
                {
                    "text": "ADM - Admiralty, Navy, Royal Marines, and Coastguard (40)",
                    "value": "ADM",
                },
                {"text": "HO - Home Office (40)", "value": "HO"},
                {
                    "text": "C - Chancery, the Wardrobe, Royal Household, Exchequer and various commissions (40)",
                    "value": "C",
                },
                {
                    "text": "PROB - Prerogative Court of Canterbury (35)",
                    "value": "PROB",
                },
                {
                    "text": "AIR - Air Ministry and Royal Air Force records (35)",
                    "value": "AIR",
                },
                {"text": "FO - Foreign Office (35)", "value": "FO"},
                {"text": "GTI - Grenfell Tower Inquiry (35)", "value": "GTI"},
                # "Y" collection is included as a parent with no child entries under it
                {
                    "text": "Y - UK Parliament (15)",
                    "value": "Y",
                    "is_parent": True,
                    "hint": "select to show more specific collections",
                },
                {
                    "text": "RAIL - Pre-nationalisation railway companies, pre-nationalisation canal and related companies (30)",
                    "value": "RAIL",
                },
                {
                    "text": "EF - Health and Safety Commission and Executive (20)",
                    "value": "EF",
                },
            ],
        )
        self.assertEqual(
            context_data.get("selected_filters"),
            [],
        )
        self.assertEqual(
            collection_field.more_filter_choices_available,
            True,
        )
        self.assertEqual(
            collection_field.more_filter_choices_url, "?filter_list=longCollection"
        )
        self.assertEqual(
            collection_field.more_filter_choices_text, "See more collections"
        )

        self.assertTrue(response.context_data.get("filters_visible"))
        self.assertTrue(collection_field.is_visible)

    @responses.activate
    def test_search_with_non_parliamentary_archives(
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

        # parent choice "Y" is not included because it has 0 hits
        self.assertEqual(
            collection_field.choices,
            [("BT", "BT - Board of Trade and successors (50)", None)],
        )

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
    def test_search_with_parliamentary_archives_parent(
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
                            # more than 10 child entries exist for "Y"
                            # 12 child entries exist for "Y"
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

        self.assertEqual(MAX_FILTER_CHOICES, 10)

        self.assertEqual(
            collection_field.choices,
            [
                (
                    "Y",
                    "Y - UK Parliament (15)",
                    [
                        (
                            "YHL",
                            "YHL - Records of the House of Commons; Records of the House of Lords (10)",
                            None,
                        ),
                        ("YHC", "YHC - Records of the House of Commons (5)", None),
                        ("YBBK", "YBBK - The Beaverbrook Papers (1)", None),
                        (
                            "YHNN",
                            "YHNN - Papers of Sir Patrick Joseph Henry Hannon MP (1874-1963) (1)",
                            None,
                        ),
                        (
                            "YFLS",
                            "YFLS - Papers of Frances Stevenson (1888-1972) (1)",
                            None,
                        ),
                        (
                            "YHEA",
                            "YHEA - Papers of Timothy Michael Healy, KC (1)",
                            None,
                        ),
                        ("YWAR", "YWAR - The Wargrave Papers (1)", None),
                        (
                            "YBAL",
                            "YBAL - Papers of Harold Harrington Balfour (1897-1988, 1st Baron Balfour of Inchrye (1)",
                            None,
                        ),
                        ("YBLU", "YBLU - Papers of Ralph David Blumenfeld (1)", None),
                        ("YOWE", "YOWE - The Owen Papers (1)", None),
                        ("YLG", "YLG - The Lloyd George Papers (1)", None),
                        (
                            "YBLK",
                            "YBLK - Papers of Robert Norman William Blake (1916-2003, Baron Blake of Braydeston (1)",
                            None,
                        ),
                    ],
                )
            ],
        )

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
    def test_search_with_parliamentary_archives_parent_and_child(
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
            collection_field.choices,
            [
                (
                    "Y",
                    "Y - UK Parliament (15)",
                    [
                        (
                            "YHL",
                            "YHL - Records of the House of Commons; Records of the House of Lords (10)",
                            None,
                        ),
                        ("YHC", "YHC - Records of the House of Commons (5)", None),
                    ],
                )
            ],
        )

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
                }
            ],
        )
        self.assertEqual(
            context_data.get("selected_filters"),
            [
                {
                    "label": "Collection: Y - UK Parliament",
                    "href": "?",  # parent/top level removes all parent and child values
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
    def test_search_with_parliamentary_archives_child_without_parent(
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
                            # returns "Y" even though it's not selected in the query
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

        response = self.client.get("/catalogue/search/?collection=YHL&collection=YHC")

        context_data = response.context_data
        form = context_data.get("form")
        collection_field = form.fields[FieldsConstant.COLLECTION]

        self.assertEqual(len(context_data.get("results")), 2)

        self.assertEqual(
            collection_field.value,
            ["YHL", "YHC"],
        )
        self.assertEqual(
            collection_field.cleaned,
            ["YHL", "YHC"],
        )

        self.assertEqual(collection_field.choices_updated, True)

        self.assertEqual(
            collection_field.choices,
            [
                (
                    "Y",
                    "Y - UK Parliament (15)",
                    [
                        (
                            "YHL",
                            "YHL - Records of the House of Commons; Records of the House of Lords (10)",
                            None,
                        ),
                        ("YHC", "YHC - Records of the House of Commons (5)", None),
                    ],
                )
            ],
        )

        # parent "Y" is automatically checked because its children are selected
        self.assertEqual(
            collection_field.items,
            [
                {
                    "text": "Y - UK Parliament (15)",
                    "value": "Y",
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
                    "checked": True,
                }
            ],
        )

        # "Y" active filter is automatically included because its children are selected
        # "Y" removes all child collection values from the current field if it is selected
        self.assertEqual(
            context_data.get("selected_filters"),
            [
                {
                    "label": "Collection: YHL - Records of the House of Commons; Records of the House of Lords",
                    "href": "?collection=YHC",
                    "title": "Remove YHL - Records of the House of Commons; Records of the House of Lords collection",
                },
                {
                    "label": "Collection: YHC - Records of the House of Commons",
                    "href": "?collection=YHL",
                    "title": "Remove YHC - Records of the House of Commons collection",
                },
                {
                    "label": "Collection: Y - UK Parliament",
                    "href": "?",
                    "title": "Remove Y - UK Parliament collection",
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
