from http import HTTPStatus

import responses
from django.conf import settings
from django.test import TestCase
from django.utils.encoding import force_str

from app.search.constants import MAX_FILTER_CHOICES, FieldsConstant


class CatalogueSearchViewAboveNEntriesCollectionFilterTests(TestCase):
    """Tests selections above the first N entries."""

    @responses.activate
    def test_search_selection_above_first_n_entries_y_inside_first_n(
        self,
    ):
        """Test selections above the first N entries."""

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
                        # Entries more than MAX_FILTER_CHOICES
                        # Y parent+child (1+11) = 12
                        # Non-Y entries = 10
                        # TOTAL entries = 12 + 10 = 22
                        "entries": [
                            {"value": "BT", "doc_count": 200},
                            {"value": "YHL", "doc_count": 3},
                            {
                                "value": "Y",
                                "doc_count": 500,
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
                            {"value": "WO", "doc_count": 300},
                            {"value": "ADM", "doc_count": 400},
                            {"value": "HO", "doc_count": 250},
                            {"value": "C", "doc_count": 500},
                            {"value": "AIR", "doc_count": 50},
                            {"value": "GTI", "doc_count": 75},
                            {"value": "E", "doc_count": 300},
                            {"value": "RAIL", "doc_count": 200},
                            {"value": "LEV", "doc_count": 700},
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

        # select "Y" parent only along with 10 other collections
        response = self.client.get(
            "/catalogue/search/?collection=Y"
            "&collection=LEV&collection=ADM&collection=BT&collection=WO&collection=HO&collection=E&collection=C&collection=AIR&collection=GTI&collection=RAIL"
            "&collection=YHL&&collection=YBBK&collection=YHNN&collection=YFLS&collection=YHEA&collection=YWAR&collection=YBAL&collection=YBLU&collection=YOWE&collection=YLG&collection=YBLK"
        )

        context_data = response.context_data
        form = context_data.get("form")
        collection_field = form.fields[FieldsConstant.COLLECTION]

        self.assertEqual(len(context_data.get("results")), 2)

        self.assertEqual(
            collection_field.value,
            [
                "Y",
                "LEV",
                "ADM",
                "BT",
                "WO",
                "HO",
                "E",
                "C",
                "AIR",
                "GTI",
                "RAIL",
                "YHL",
                "YBBK",
                "YHNN",
                "YFLS",
                "YHEA",
                "YWAR",
                "YBAL",
                "YBLU",
                "YOWE",
                "YLG",
                "YBLK",
            ],
        )
        self.assertEqual(
            collection_field.cleaned,
            [
                "Y",
                "LEV",
                "ADM",
                "BT",
                "WO",
                "HO",
                "E",
                "C",
                "AIR",
                "GTI",
                "RAIL",
                "YHL",
                "YBBK",
                "YHNN",
                "YFLS",
                "YHEA",
                "YWAR",
                "YBAL",
                "YBLU",
                "YOWE",
                "YLG",
                "YBLK",
            ],
        )
        self.assertEqual(collection_field.choices_updated, True)

        # Ensure the maximum number of filter choices is within the expected limit
        self.assertLessEqual(MAX_FILTER_CHOICES, 10)
        self.assertEqual(len(collection_field.choices), 11)
        self.assertEqual(len(collection_field.choices[1][2]), 11)

        self.assertEqual(
            collection_field.choices,
            [
                ("BT", "BT - Board of Trade and successors (200)", None),
                (
                    "Y",
                    "Y - UK Parliament (500)",
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
                (
                    "WO",
                    "WO - War Office, Armed Forces, Judge Advocate General, and related bodies (300)",
                    None,
                ),
                (
                    "ADM",
                    "ADM - Admiralty, Navy, Royal Marines, and Coastguard (400)",
                    None,
                ),
                ("HO", "HO - Home Office (250)", None),
                (
                    "C",
                    "C - Chancery, the Wardrobe, Royal Household, Exchequer and various commissions (500)",
                    None,
                ),
                ("AIR", "AIR - Air Ministry and Royal Air Force records (50)", None),
                ("GTI", "GTI - Grenfell Tower Inquiry (75)", None),
                (
                    "E",
                    "E - Exchequer, Office of First Fruits and Tenths, and the Court of Augmentations (300)",
                    None,
                ),
                (
                    "RAIL",
                    "RAIL - Pre-nationalisation railway companies, pre-nationalisation canal and related companies (200)",
                    None,
                ),
                (
                    "LEV",
                    "LEV - Inquiry into the Culture, Practices and Ethics of the Press (Leveson Inquiry) (700)",
                    None,
                ),
            ],
        )

        self.assertGreater(len(collection_field.items), MAX_FILTER_CHOICES)
        self.assertGreater(
            len(collection_field.items[1]["children"]), MAX_FILTER_CHOICES
        )
        self.assertEqual(
            collection_field.items,
            [
                {
                    "text": "BT - Board of Trade and successors (200)",
                    "value": "BT",
                    "checked": True,
                },
                {
                    "text": "Y - UK Parliament (500)",
                    "value": "Y",
                    "checked": True,
                    "is_parent": True,
                    "hint": "select to show more specific collections",
                    "children": [
                        {
                            "text": "YHL - Records of the House of Commons; Records of the House of Lords (3)",
                            "value": "YHL",
                            "checked": True,
                            "is_child": True,
                        },
                        {
                            "text": "YBBK - The Beaverbrook Papers (1)",
                            "value": "YBBK",
                            "checked": True,
                            "is_child": True,
                        },
                        {
                            "text": "YHNN - Papers of Sir Patrick Joseph Henry Hannon MP (1874-1963) (1)",
                            "value": "YHNN",
                            "checked": True,
                            "is_child": True,
                        },
                        {
                            "text": "YFLS - Papers of Frances Stevenson (1888-1972) (1)",
                            "value": "YFLS",
                            "checked": True,
                            "is_child": True,
                        },
                        {
                            "text": "YHEA - Papers of Timothy Michael Healy, KC (1)",
                            "value": "YHEA",
                            "checked": True,
                            "is_child": True,
                        },
                        {
                            "text": "YWAR - The Wargrave Papers (1)",
                            "value": "YWAR",
                            "checked": True,
                            "is_child": True,
                        },
                        {
                            "text": "YBAL - Papers of Harold Harrington Balfour (1897-1988, 1st Baron Balfour of Inchrye (1)",
                            "value": "YBAL",
                            "checked": True,
                            "is_child": True,
                        },
                        {
                            "text": "YBLU - Papers of Ralph David Blumenfeld (1)",
                            "value": "YBLU",
                            "checked": True,
                            "is_child": True,
                        },
                        {
                            "text": "YOWE - The Owen Papers (1)",
                            "value": "YOWE",
                            "checked": True,
                            "is_child": True,
                        },
                        {
                            "text": "YLG - The Lloyd George Papers (1)",
                            "value": "YLG",
                            "checked": True,
                            "is_child": True,
                        },
                        {
                            "text": "YBLK - Papers of Robert Norman William Blake (1916-2003, Baron Blake of Braydeston (1)",
                            "value": "YBLK",
                            "checked": True,
                            "is_child": True,
                        },
                    ],
                    "more_filter_choices_available": True,
                    "more_filter_choices_text": "See more UK Parliament collections",
                    "more_filter_choices_url": "?collection=Y"
                    "&collection=LEV&collection=ADM&collection=BT&collection=WO&collection=HO&collection=E&collection=C&collection=AIR&collection=GTI&collection=RAIL"
                    "&collection=YHL&collection=YBBK&collection=YHNN&collection=YFLS&collection=YHEA&collection=YWAR&collection=YBAL&collection=YBLU&collection=YOWE&collection=YLG&collection=YBLK"
                    "&filter_list=longCollection",
                },
                {
                    "text": "WO - War Office, Armed Forces, Judge Advocate General, and related bodies (300)",
                    "value": "WO",
                    "checked": True,
                },
                {
                    "text": "ADM - Admiralty, Navy, Royal Marines, and Coastguard (400)",
                    "value": "ADM",
                    "checked": True,
                },
                {"text": "HO - Home Office (250)", "value": "HO", "checked": True},
                {
                    "text": "C - Chancery, the Wardrobe, Royal Household, Exchequer and various commissions (500)",
                    "value": "C",
                    "checked": True,
                },
                {
                    "text": "AIR - Air Ministry and Royal Air Force records (50)",
                    "value": "AIR",
                    "checked": True,
                },
                {
                    "text": "GTI - Grenfell Tower Inquiry (75)",
                    "value": "GTI",
                    "checked": True,
                },
                {
                    "text": "E - Exchequer, Office of First Fruits and Tenths, and the Court of Augmentations (300)",
                    "value": "E",
                    "checked": True,
                },
                {
                    "text": "RAIL - Pre-nationalisation railway companies, pre-nationalisation canal and related companies (200)",
                    "value": "RAIL",
                    "checked": True,
                },
                {
                    "text": "LEV - Inquiry into the Culture, Practices and Ethics of the Press (Leveson Inquiry) (700)",
                    "value": "LEV",
                    "checked": True,
                },
            ],
        )

        self.assertEqual(
            collection_field.more_filter_choices_available,
            True,
        )
        self.assertEqual(
            collection_field.more_filter_choices_url,
            "?collection=Y"
            "&collection=LEV&collection=ADM&collection=BT&collection=WO&collection=HO&collection=E&collection=C&collection=AIR&collection=GTI&collection=RAIL"
            "&collection=YHL&collection=YBBK&collection=YHNN&collection=YFLS&collection=YHEA&collection=YWAR&collection=YBAL&collection=YBLU&collection=YOWE&collection=YLG&collection=YBLK"
            "&filter_list=longCollection",
        )
        self.assertEqual(
            collection_field.more_filter_choices_text, "See more collections"
        )

        # entries above first 10 are preserved/hidden as hidden selected filters
        self.assertEqual(
            context_data.get("hidden_selected_filters"),
            [{"name": "collection", "values": ["LEV", "YBLK"]}],
        )
        html = force_str(response.content)
        self.assertIn("""<input type="hidden" name="collection" value="LEV">""", html)
        self.assertIn("""<input type="hidden" name="collection" value="YBLK">""", html)

        self.assertEqual(
            len(context_data.get("selected_filters")),
            22,
        )

        self.assertTrue(response.context_data.get("filters_visible"))
        self.assertTrue(collection_field.is_visible)

    @responses.activate
    def test_search_selection_above_first_n_entries_y_outside_first_n_not_last(
        self,
    ):
        """Test selections above the first N entries with Y outside the first N but not last"""

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
                        # Entries more than MAX_FILTER_CHOICES
                        # Y parent+child (1+11) = 12
                        # Non-Y entries = 10
                        # TOTAL entries = 12 + 10 = 22
                        # Y is outside the first 10 entries
                        "entries": [
                            {"value": "YHL", "doc_count": 3},
                            {"value": "BT", "doc_count": 200},
                            {"value": "WO", "doc_count": 300},
                            {"value": "ADM", "doc_count": 400},
                            {"value": "HO", "doc_count": 250},
                            {"value": "C", "doc_count": 500},
                            {"value": "AIR", "doc_count": 50},
                            {"value": "GTI", "doc_count": 75},
                            {"value": "E", "doc_count": 300},
                            {"value": "RAIL", "doc_count": 200},
                            {"value": "LEV", "doc_count": 700},
                            {
                                "value": "Y",
                                "doc_count": 500,
                            },  # Y is within the outside the first 10 entries, but not last
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

        # select "Y" parent only along with 10 other collections
        response = self.client.get(
            "/catalogue/search/?collection=Y"
            "&collection=LEV&collection=ADM&collection=BT&collection=WO&collection=HO&collection=E&collection=C&collection=AIR&collection=GTI&collection=RAIL"
            "&collection=YHL&&collection=YBBK&collection=YHNN&collection=YFLS&collection=YHEA&collection=YWAR&collection=YBAL&collection=YBLU&collection=YOWE&collection=YLG&collection=YBLK"
        )

        context_data = response.context_data
        form = context_data.get("form")
        collection_field = form.fields[FieldsConstant.COLLECTION]

        self.assertEqual(len(context_data.get("results")), 2)

        self.assertEqual(
            collection_field.value,
            [
                "Y",
                "LEV",
                "ADM",
                "BT",
                "WO",
                "HO",
                "E",
                "C",
                "AIR",
                "GTI",
                "RAIL",
                "YHL",
                "YBBK",
                "YHNN",
                "YFLS",
                "YHEA",
                "YWAR",
                "YBAL",
                "YBLU",
                "YOWE",
                "YLG",
                "YBLK",
            ],
        )
        self.assertEqual(
            collection_field.cleaned,
            [
                "Y",
                "LEV",
                "ADM",
                "BT",
                "WO",
                "HO",
                "E",
                "C",
                "AIR",
                "GTI",
                "RAIL",
                "YHL",
                "YBBK",
                "YHNN",
                "YFLS",
                "YHEA",
                "YWAR",
                "YBAL",
                "YBLU",
                "YOWE",
                "YLG",
                "YBLK",
            ],
        )
        self.assertEqual(collection_field.choices_updated, True)

        # Ensure the maximum number of filter choices is within the expected limit
        self.assertLessEqual(MAX_FILTER_CHOICES, 10)
        self.assertEqual(len(collection_field.choices), 11)

        # Y is at the 10th position (index 9) in the choices list
        self.assertEqual(len(collection_field.choices[9][2]), 11)

        self.assertEqual(
            collection_field.choices,
            [
                ("BT", "BT - Board of Trade and successors (200)", None),
                (
                    "WO",
                    "WO - War Office, Armed Forces, Judge Advocate General, and related bodies (300)",
                    None,
                ),
                (
                    "ADM",
                    "ADM - Admiralty, Navy, Royal Marines, and Coastguard (400)",
                    None,
                ),
                ("HO", "HO - Home Office (250)", None),
                (
                    "C",
                    "C - Chancery, the Wardrobe, Royal Household, Exchequer and various commissions (500)",
                    None,
                ),
                ("AIR", "AIR - Air Ministry and Royal Air Force records (50)", None),
                ("GTI", "GTI - Grenfell Tower Inquiry (75)", None),
                (
                    "E",
                    "E - Exchequer, Office of First Fruits and Tenths, and the Court of Augmentations (300)",
                    None,
                ),
                (
                    "RAIL",
                    "RAIL - Pre-nationalisation railway companies, pre-nationalisation canal and related companies (200)",
                    None,
                ),
                # 10th position for the parent "Y" if it is outside the first 10 entries
                (
                    "Y",
                    "Y - UK Parliament (500)",
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
                (
                    "LEV",
                    "LEV - Inquiry into the Culture, Practices and Ethics of the Press (Leveson Inquiry) (700)",
                    None,
                ),
            ],
        )

        self.assertGreater(len(collection_field.items), MAX_FILTER_CHOICES)

        # Assert that the 10th item (index 9) has children and their count is greater than MAX_FILTER_CHOICES
        self.assertGreater(
            len(collection_field.items[9]["children"]), MAX_FILTER_CHOICES
        )

        # 10th position for the parent "Y" if it is outside the first 10 entries
        self.assertEqual(
            collection_field.items,
            [
                {
                    "text": "BT - Board of Trade and successors (200)",
                    "value": "BT",
                    "checked": True,
                },
                {
                    "text": "WO - War Office, Armed Forces, Judge Advocate General, and related bodies (300)",
                    "value": "WO",
                    "checked": True,
                },
                {
                    "text": "ADM - Admiralty, Navy, Royal Marines, and Coastguard (400)",
                    "value": "ADM",
                    "checked": True,
                },
                {"text": "HO - Home Office (250)", "value": "HO", "checked": True},
                {
                    "text": "C - Chancery, the Wardrobe, Royal Household, Exchequer and various commissions (500)",
                    "value": "C",
                    "checked": True,
                },
                {
                    "text": "AIR - Air Ministry and Royal Air Force records (50)",
                    "value": "AIR",
                    "checked": True,
                },
                {
                    "text": "GTI - Grenfell Tower Inquiry (75)",
                    "value": "GTI",
                    "checked": True,
                },
                {
                    "text": "E - Exchequer, Office of First Fruits and Tenths, and the Court of Augmentations (300)",
                    "value": "E",
                    "checked": True,
                },
                {
                    "text": "RAIL - Pre-nationalisation railway companies, pre-nationalisation canal and related companies (200)",
                    "value": "RAIL",
                    "checked": True,
                },
                {
                    "text": "Y - UK Parliament (500)",
                    "value": "Y",
                    "checked": True,
                    "is_parent": True,
                    "hint": "select to show more specific collections",
                    "children": [
                        {
                            "text": "YHL - Records of the House of Commons; Records of the House of Lords (3)",
                            "value": "YHL",
                            "checked": True,
                            "is_child": True,
                        },
                        {
                            "text": "YBBK - The Beaverbrook Papers (1)",
                            "value": "YBBK",
                            "checked": True,
                            "is_child": True,
                        },
                        {
                            "text": "YHNN - Papers of Sir Patrick Joseph Henry Hannon MP (1874-1963) (1)",
                            "value": "YHNN",
                            "checked": True,
                            "is_child": True,
                        },
                        {
                            "text": "YFLS - Papers of Frances Stevenson (1888-1972) (1)",
                            "value": "YFLS",
                            "checked": True,
                            "is_child": True,
                        },
                        {
                            "text": "YHEA - Papers of Timothy Michael Healy, KC (1)",
                            "value": "YHEA",
                            "checked": True,
                            "is_child": True,
                        },
                        {
                            "text": "YWAR - The Wargrave Papers (1)",
                            "value": "YWAR",
                            "checked": True,
                            "is_child": True,
                        },
                        {
                            "text": "YBAL - Papers of Harold Harrington Balfour (1897-1988, 1st Baron Balfour of Inchrye (1)",
                            "value": "YBAL",
                            "checked": True,
                            "is_child": True,
                        },
                        {
                            "text": "YBLU - Papers of Ralph David Blumenfeld (1)",
                            "value": "YBLU",
                            "checked": True,
                            "is_child": True,
                        },
                        {
                            "text": "YOWE - The Owen Papers (1)",
                            "value": "YOWE",
                            "checked": True,
                            "is_child": True,
                        },
                        {
                            "text": "YLG - The Lloyd George Papers (1)",
                            "value": "YLG",
                            "checked": True,
                            "is_child": True,
                        },
                        {
                            "text": "YBLK - Papers of Robert Norman William Blake (1916-2003, Baron Blake of Braydeston (1)",
                            "value": "YBLK",
                            "checked": True,
                            "is_child": True,
                        },
                    ],
                    "more_filter_choices_available": True,
                    "more_filter_choices_text": "See more UK Parliament collections",
                    "more_filter_choices_url": "?collection=Y&collection=LEV&collection=ADM&collection=BT&collection=WO&collection=HO&collection=E&collection=C&collection=AIR&collection=GTI&collection=RAIL&collection=YHL&collection=YBBK&collection=YHNN&collection=YFLS&collection=YHEA&collection=YWAR&collection=YBAL&collection=YBLU&collection=YOWE&collection=YLG&collection=YBLK&filter_list=longCollection",
                },
                {
                    "text": "LEV - Inquiry into the Culture, Practices and Ethics of the Press (Leveson Inquiry) (700)",
                    "value": "LEV",
                    "checked": True,
                },
            ],
        )

        self.assertEqual(
            collection_field.more_filter_choices_available,
            True,
        )
        self.assertEqual(
            collection_field.more_filter_choices_url,
            "?collection=Y"
            "&collection=LEV&collection=ADM&collection=BT&collection=WO&collection=HO&collection=E&collection=C&collection=AIR&collection=GTI&collection=RAIL"
            "&collection=YHL&collection=YBBK&collection=YHNN&collection=YFLS&collection=YHEA&collection=YWAR&collection=YBAL&collection=YBLU&collection=YOWE&collection=YLG&collection=YBLK"
            "&filter_list=longCollection",
        )
        self.assertEqual(
            collection_field.more_filter_choices_text, "See more collections"
        )

        # entries above first 10 are preserved/hidden as hidden selected filters
        self.assertEqual(
            context_data.get("hidden_selected_filters"),
            [{"name": "collection", "values": ["LEV", "YBLK"]}],
        )
        html = force_str(response.content)
        self.assertIn("""<input type="hidden" name="collection" value="LEV">""", html)
        self.assertIn("""<input type="hidden" name="collection" value="YBLK">""", html)

        self.assertEqual(
            len(context_data.get("selected_filters")),
            22,
        )

        self.assertTrue(response.context_data.get("filters_visible"))
        self.assertTrue(collection_field.is_visible)

    @responses.activate
    def test_search_selection_above_first_n_entries_y_outside_first_n_is_last(
        self,
    ):
        """Test selections above the first N entries with Y outside the first N is last"""

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
                        # Entries more than MAX_FILTER_CHOICES
                        # Y parent+child (1+11) = 12
                        # Non-Y entries = 10
                        # TOTAL entries = 12 + 10 = 22
                        # Y is outside the first 10 entries
                        "entries": [
                            {"value": "YHL", "doc_count": 3},
                            {"value": "BT", "doc_count": 200},
                            {"value": "WO", "doc_count": 300},
                            {"value": "ADM", "doc_count": 400},
                            {"value": "HO", "doc_count": 250},
                            {"value": "C", "doc_count": 500},
                            {"value": "AIR", "doc_count": 50},
                            {"value": "GTI", "doc_count": 75},
                            {"value": "E", "doc_count": 300},
                            {"value": "RAIL", "doc_count": 200},
                            {"value": "LEV", "doc_count": 700},
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
                            {
                                "value": "Y",
                                "doc_count": 500,
                            },  # Y is within the first 10 entries, and is last
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

        # select "Y" parent only along with 10 other collections
        response = self.client.get(
            "/catalogue/search/?collection=Y"
            "&collection=LEV&collection=ADM&collection=BT&collection=WO&collection=HO&collection=E&collection=C&collection=AIR&collection=GTI&collection=RAIL"
            "&collection=YHL&&collection=YBBK&collection=YHNN&collection=YFLS&collection=YHEA&collection=YWAR&collection=YBAL&collection=YBLU&collection=YOWE&collection=YLG&collection=YBLK"
        )

        context_data = response.context_data
        form = context_data.get("form")
        collection_field = form.fields[FieldsConstant.COLLECTION]

        self.assertEqual(len(context_data.get("results")), 2)

        self.assertEqual(
            collection_field.value,
            [
                "Y",
                "LEV",
                "ADM",
                "BT",
                "WO",
                "HO",
                "E",
                "C",
                "AIR",
                "GTI",
                "RAIL",
                "YHL",
                "YBBK",
                "YHNN",
                "YFLS",
                "YHEA",
                "YWAR",
                "YBAL",
                "YBLU",
                "YOWE",
                "YLG",
                "YBLK",
            ],
        )
        self.assertEqual(
            collection_field.cleaned,
            [
                "Y",
                "LEV",
                "ADM",
                "BT",
                "WO",
                "HO",
                "E",
                "C",
                "AIR",
                "GTI",
                "RAIL",
                "YHL",
                "YBBK",
                "YHNN",
                "YFLS",
                "YHEA",
                "YWAR",
                "YBAL",
                "YBLU",
                "YOWE",
                "YLG",
                "YBLK",
            ],
        )
        self.assertEqual(collection_field.choices_updated, True)

        # Ensure the maximum number of filter choices is within the expected limit
        self.assertLessEqual(MAX_FILTER_CHOICES, 10)
        self.assertEqual(len(collection_field.choices), 11)

        # Y is at the 10th position (index 9) in the choices list
        self.assertEqual(len(collection_field.choices[9][2]), 11)

        self.assertEqual(
            collection_field.choices,
            [
                ("BT", "BT - Board of Trade and successors (200)", None),
                (
                    "WO",
                    "WO - War Office, Armed Forces, Judge Advocate General, and related bodies (300)",
                    None,
                ),
                (
                    "ADM",
                    "ADM - Admiralty, Navy, Royal Marines, and Coastguard (400)",
                    None,
                ),
                ("HO", "HO - Home Office (250)", None),
                (
                    "C",
                    "C - Chancery, the Wardrobe, Royal Household, Exchequer and various commissions (500)",
                    None,
                ),
                ("AIR", "AIR - Air Ministry and Royal Air Force records (50)", None),
                ("GTI", "GTI - Grenfell Tower Inquiry (75)", None),
                (
                    "E",
                    "E - Exchequer, Office of First Fruits and Tenths, and the Court of Augmentations (300)",
                    None,
                ),
                (
                    "RAIL",
                    "RAIL - Pre-nationalisation railway companies, pre-nationalisation canal and related companies (200)",
                    None,
                ),
                # 10th position for the parent "Y" if it is outside the first 10 entries
                (
                    "Y",
                    "Y - UK Parliament (500)",
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
                (
                    "LEV",
                    "LEV - Inquiry into the Culture, Practices and Ethics of the Press (Leveson Inquiry) (700)",
                    None,
                ),
            ],
        )

        self.assertGreater(len(collection_field.items), MAX_FILTER_CHOICES)

        # Assert that the 10th item (index 9) has children and their count is greater than MAX_FILTER_CHOICES
        self.assertGreater(
            len(collection_field.items[9]["children"]), MAX_FILTER_CHOICES
        )

        # 10th position for the parent "Y" if it is outside the first 10 entries
        self.assertEqual(
            collection_field.items,
            [
                {
                    "text": "BT - Board of Trade and successors (200)",
                    "value": "BT",
                    "checked": True,
                },
                {
                    "text": "WO - War Office, Armed Forces, Judge Advocate General, and related bodies (300)",
                    "value": "WO",
                    "checked": True,
                },
                {
                    "text": "ADM - Admiralty, Navy, Royal Marines, and Coastguard (400)",
                    "value": "ADM",
                    "checked": True,
                },
                {"text": "HO - Home Office (250)", "value": "HO", "checked": True},
                {
                    "text": "C - Chancery, the Wardrobe, Royal Household, Exchequer and various commissions (500)",
                    "value": "C",
                    "checked": True,
                },
                {
                    "text": "AIR - Air Ministry and Royal Air Force records (50)",
                    "value": "AIR",
                    "checked": True,
                },
                {
                    "text": "GTI - Grenfell Tower Inquiry (75)",
                    "value": "GTI",
                    "checked": True,
                },
                {
                    "text": "E - Exchequer, Office of First Fruits and Tenths, and the Court of Augmentations (300)",
                    "value": "E",
                    "checked": True,
                },
                {
                    "text": "RAIL - Pre-nationalisation railway companies, pre-nationalisation canal and related companies (200)",
                    "value": "RAIL",
                    "checked": True,
                },
                {
                    "text": "Y - UK Parliament (500)",
                    "value": "Y",
                    "checked": True,
                    "is_parent": True,
                    "hint": "select to show more specific collections",
                    "children": [
                        {
                            "text": "YHL - Records of the House of Commons; Records of the House of Lords (3)",
                            "value": "YHL",
                            "checked": True,
                            "is_child": True,
                        },
                        {
                            "text": "YBBK - The Beaverbrook Papers (1)",
                            "value": "YBBK",
                            "checked": True,
                            "is_child": True,
                        },
                        {
                            "text": "YHNN - Papers of Sir Patrick Joseph Henry Hannon MP (1874-1963) (1)",
                            "value": "YHNN",
                            "checked": True,
                            "is_child": True,
                        },
                        {
                            "text": "YFLS - Papers of Frances Stevenson (1888-1972) (1)",
                            "value": "YFLS",
                            "checked": True,
                            "is_child": True,
                        },
                        {
                            "text": "YHEA - Papers of Timothy Michael Healy, KC (1)",
                            "value": "YHEA",
                            "checked": True,
                            "is_child": True,
                        },
                        {
                            "text": "YWAR - The Wargrave Papers (1)",
                            "value": "YWAR",
                            "checked": True,
                            "is_child": True,
                        },
                        {
                            "text": "YBAL - Papers of Harold Harrington Balfour (1897-1988, 1st Baron Balfour of Inchrye (1)",
                            "value": "YBAL",
                            "checked": True,
                            "is_child": True,
                        },
                        {
                            "text": "YBLU - Papers of Ralph David Blumenfeld (1)",
                            "value": "YBLU",
                            "checked": True,
                            "is_child": True,
                        },
                        {
                            "text": "YOWE - The Owen Papers (1)",
                            "value": "YOWE",
                            "checked": True,
                            "is_child": True,
                        },
                        {
                            "text": "YLG - The Lloyd George Papers (1)",
                            "value": "YLG",
                            "checked": True,
                            "is_child": True,
                        },
                        {
                            "text": "YBLK - Papers of Robert Norman William Blake (1916-2003, Baron Blake of Braydeston (1)",
                            "value": "YBLK",
                            "checked": True,
                            "is_child": True,
                        },
                    ],
                    "more_filter_choices_available": True,
                    "more_filter_choices_text": "See more UK Parliament collections",
                    "more_filter_choices_url": "?collection=Y&collection=LEV&collection=ADM&collection=BT&collection=WO&collection=HO&collection=E&collection=C&collection=AIR&collection=GTI&collection=RAIL&collection=YHL&collection=YBBK&collection=YHNN&collection=YFLS&collection=YHEA&collection=YWAR&collection=YBAL&collection=YBLU&collection=YOWE&collection=YLG&collection=YBLK&filter_list=longCollection",
                },
                {
                    "text": "LEV - Inquiry into the Culture, Practices and Ethics of the Press (Leveson Inquiry) (700)",
                    "value": "LEV",
                    "checked": True,
                },
            ],
        )

        self.assertEqual(
            collection_field.more_filter_choices_available,
            True,
        )
        self.assertEqual(
            collection_field.more_filter_choices_url,
            "?collection=Y"
            "&collection=LEV&collection=ADM&collection=BT&collection=WO&collection=HO&collection=E&collection=C&collection=AIR&collection=GTI&collection=RAIL"
            "&collection=YHL&collection=YBBK&collection=YHNN&collection=YFLS&collection=YHEA&collection=YWAR&collection=YBAL&collection=YBLU&collection=YOWE&collection=YLG&collection=YBLK"
            "&filter_list=longCollection",
        )
        self.assertEqual(
            collection_field.more_filter_choices_text, "See more collections"
        )

        # entries above first 10 are preserved/hidden as hidden selected filters
        self.assertEqual(
            context_data.get("hidden_selected_filters"),
            [{"name": "collection", "values": ["LEV", "YBLK"]}],
        )
        html = force_str(response.content)
        self.assertIn("""<input type="hidden" name="collection" value="LEV">""", html)
        self.assertIn("""<input type="hidden" name="collection" value="YBLK">""", html)

        self.assertEqual(
            len(context_data.get("selected_filters")),
            22,
        )

        self.assertTrue(response.context_data.get("filters_visible"))
        self.assertTrue(collection_field.is_visible)
