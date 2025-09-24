from datetime import date
from http import HTTPStatus
from unittest.mock import patch

import responses
from app.records.models import Record
from app.search.buckets import BucketKeys
from app.search.forms import (
    CatalogueSearchNonTnaForm,
    CatalogueSearchTnaForm,
    FieldsConstant,
)
from django.conf import settings
from django.test import TestCase


class CatalogueSearchViewTests(TestCase):
    """Mainly tests the context."""

    @responses.activate
    def test_catalogue_search_context_without_params(self):

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
                            {"value": "Item", "doc_count": 100},
                            {"value": "Division", "doc_count": 5},
                        ],
                    },
                    {
                        "name": "collection",
                        "entries": [
                            {"value": "BT", "doc_count": 50},
                            {"value": "WO", "doc_count": 35},
                        ],
                    },
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

        self.response = self.client.get("/catalogue/search/")
        self.assertEqual(self.response.status_code, HTTPStatus.OK)

        self.assertIsInstance(self.response.context_data.get("results"), list)
        self.assertEqual(len(self.response.context_data.get("results")), 1)
        self.assertIsInstance(
            self.response.context_data.get("results")[0], Record
        )
        self.assertEqual(
            self.response.context_data.get("stats"),
            {"total": 26008838, "results": 20},
        )

        self.assertEqual(
            self.response.context_data.get("results_range"),
            {"from": 1, "to": 20},
        )

        self.assertEqual(self.response.context_data.get("selected_filters"), [])

        self.assertEqual(
            self.response.context_data.get("pagination"),
            {
                "items": [
                    {"number": "1", "href": "?page=1", "current": True},
                    {"number": "2", "href": "?page=2", "current": False},
                    {"ellipsis": True},
                    {"number": "500", "href": "?page=500", "current": False},
                ],
                "next": {"href": "?page=2", "title": "Next page of results"},
            },
        )

        self.assertEqual(
            self.response.context_data.get("bucket_list").items,
            [
                {
                    "name": "Records at the National Archives (1)",
                    "href": "?group=tna",
                    "current": True,
                },
                {
                    "name": "Records at other UK archives (0)",
                    "href": "?group=nonTna",
                    "current": False,
                },
            ],
        )
        self.assertEqual(
            self.response.context_data.get("bucket_keys"), BucketKeys
        )

        # ### form ###
        self.assertIsInstance(
            self.response.context_data.get("form"), CatalogueSearchTnaForm
        )
        self.assertEqual(self.response.context_data.get("form").errors, {})
        self.assertEqual(len(self.response.context_data.get("form").fields), 10)
        tna_field_names = [
            FieldsConstant.GROUP,
            FieldsConstant.SORT,
            FieldsConstant.Q,
            FieldsConstant.LEVEL,
            FieldsConstant.COLLECTION,
            FieldsConstant.ONLINE,
            FieldsConstant.RECORD_DATE_FROM,
            FieldsConstant.RECORD_DATE_TO,
            FieldsConstant.OPENING_DATE_FROM,
            FieldsConstant.OPENING_DATE_TO,
        ]
        tna_form_field_names = set(
            self.response.context_data.get("form").fields.keys()
        )
        self.assertTrue(set(tna_field_names) == set(tna_form_field_names))

        # ### form fields ###

        self.assertEqual(
            self.response.context_data.get("form").fields["q"].name, "q"
        )
        self.assertEqual(
            self.response.context_data.get("form").fields["q"].value, ""
        )
        self.assertEqual(
            self.response.context_data.get("form").fields["q"].cleaned, ""
        )

        self.assertEqual(
            self.response.context_data.get("form").fields["group"].name, "group"
        )
        self.assertEqual(
            self.response.context_data.get("form").fields["group"].value, "tna"
        )
        self.assertEqual(
            self.response.context_data.get("form").fields["group"].cleaned,
            "tna",
        )
        self.assertEqual(
            self.response.context_data.get("form").fields["group"].items,
            [
                {
                    "text": "Records at the National Archives",
                    "value": "tna",
                    "checked": True,
                },
                {"text": "Records at other UK archives", "value": "nonTna"},
            ],
        )

        self.assertEqual(
            self.response.context_data.get("form").fields["sort"].name, "sort"
        )
        self.assertEqual(
            self.response.context_data.get("form").fields["sort"].value, ""
        )
        self.assertEqual(
            self.response.context_data.get("form").fields["sort"].cleaned, ""
        )
        self.assertEqual(
            self.response.context_data.get("form").fields["sort"].items,
            [
                {"text": "Relevance", "value": "", "checked": True},
                {"text": "Date (newest first)", "value": "date:desc"},
                {"text": "Date (oldest first)", "value": "date:asc"},
                {"text": "Title (A–Z)", "value": "title:asc"},
                {"text": "Title (Z–A)", "value": "title:desc"},
            ],
        )

        self.assertEqual(
            self.response.context_data.get("form").fields["level"].name, "level"
        )
        self.assertEqual(
            self.response.context_data.get("form").fields["level"].label,
            "Filter by levels",
        )
        self.assertEqual(
            self.response.context_data.get("form").fields["level"].value, []
        )
        self.assertEqual(
            self.response.context_data.get("form").fields["level"].cleaned, []
        )
        self.assertEqual(
            self.response.context_data.get("form").fields["level"].items,
            [
                {"text": "Item (100)", "value": "Item"},
                {"text": "Division (5)", "value": "Division"},
            ],
        )
        self.assertEqual(
            self.response.context_data.get("form").fields["collection"].items,
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

    @responses.activate
    def test_catalogue_search_context_with_query_param(self):

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

        self.response = self.client.get("/catalogue/search/?q=ufo")
        self.assertEqual(self.response.status_code, HTTPStatus.OK)
        self.assertEqual(
            self.response.context_data.get("form").fields["q"].name, "q"
        )
        self.assertEqual(
            self.response.context_data.get("form").fields["q"].value,
            "ufo",
        )
        self.assertEqual(self.response.context_data.get("selected_filters"), [])

    @responses.activate
    def test_catalogue_search_context_with_sort_param(self):

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

        self.response = self.client.get("/catalogue/search/?sort=title:asc")
        self.assertEqual(self.response.status_code, HTTPStatus.OK)
        self.assertEqual(
            self.response.context_data.get("form").fields["sort"].name, "sort"
        )
        self.assertEqual(
            self.response.context_data.get("form").fields["sort"].value,
            "title:asc",
        )
        self.assertEqual(
            self.response.context_data.get("form").fields["sort"].cleaned,
            "title:asc",
        )
        self.assertEqual(
            self.response.context_data.get("form").fields["sort"].items,
            [
                {
                    "text": "Relevance",
                    "value": "",
                },
                {
                    "text": "Date (newest first)",
                    "value": "date:desc",
                },
                {"text": "Date (oldest first)", "value": "date:asc"},
                {"text": "Title (A–Z)", "value": "title:asc", "checked": True},
                {"text": "Title (Z–A)", "value": "title:desc"},
            ],
        )
        self.assertEqual(self.response.context_data.get("selected_filters"), [])

    @responses.activate
    def test_catalogue_search_context_with_group_param(self):

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

        self.response = self.client.get("/catalogue/search/?group=nonTna")
        self.assertEqual(self.response.status_code, HTTPStatus.OK)

        self.assertIsInstance(
            self.response.context_data.get("form"), CatalogueSearchNonTnaForm
        )
        self.assertEqual(self.response.context_data.get("form").errors, {})
        self.assertEqual(len(self.response.context_data.get("form").fields), 6)
        non_tna_field_names = [
            FieldsConstant.GROUP,
            FieldsConstant.SORT,
            FieldsConstant.Q,
            FieldsConstant.HELD_BY,
            FieldsConstant.RECORD_DATE_FROM,
            FieldsConstant.RECORD_DATE_TO,
        ]
        non_tna_form_field_names = set(
            self.response.context_data.get("form").fields.keys()
        )
        self.assertTrue(
            set(non_tna_field_names) == set(non_tna_form_field_names)
        )

        self.assertEqual(
            self.response.context_data.get("form").fields["group"].name, "group"
        )
        self.assertEqual(
            self.response.context_data.get("form").fields["group"].value,
            "nonTna",
        )
        self.assertEqual(
            self.response.context_data.get("form").fields["group"].cleaned,
            "nonTna",
        )

        self.assertEqual(
            self.response.context_data.get("form").fields["group"].items,
            [
                {
                    "text": "Records at the National Archives",
                    "value": "tna",
                },
                {
                    "text": "Records at other UK archives",
                    "value": "nonTna",
                    "checked": True,
                },
            ],
        )
        self.assertEqual(self.response.context_data.get("selected_filters"), [])


class CatalogueSearchViewDebugAPITnaBucketTests(TestCase):
    """Tests API calls (url) made by the catalogue search view for CatalogueSearchTnaForm"""

    @patch("app.lib.api.logger")
    @responses.activate
    def test_catalogue_debug_api(self, mock_logger):

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
                # Note: api response is not checked for these values
                "aggregations": [
                    {
                        "name": "level",
                        "entries": [
                            {"value": "somevalue", "doc_count": 100},
                        ],
                    },
                    {
                        "name": "collection",
                        "entries": [
                            {"value": "somevalue", "doc_count": 100},
                        ],
                    },
                ],
                "buckets": [
                    {
                        "name": "group",
                        "entries": [
                            # Note: api response is not checked for these values
                            {"value": "somevalue", "count": 1},
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

        # default query
        self.response = self.client.get("/catalogue/search/")
        self.assertEqual(self.response.status_code, HTTPStatus.OK)
        mock_logger.debug.assert_called_with(
            "https://rosetta.test/data/search?aggs=level&aggs=collection&filter=group%3Atna&q=%2A&size=20"
        )

        # with group=tna param
        self.response = self.client.get("/catalogue/search/?group=tna")
        self.assertEqual(self.response.status_code, HTTPStatus.OK)
        mock_logger.debug.assert_called_with(
            "https://rosetta.test/data/search?aggs=level&aggs=collection&filter=group%3Atna&q=%2A&size=20"
        )

        # query with held_by param (should be ignored for tna group)
        self.response = self.client.get(
            "/catalogue/search/?group=tna&held_by=somearchive"
        )
        self.assertEqual(self.response.status_code, HTTPStatus.OK)
        mock_logger.debug.assert_called_with(
            "https://rosetta.test/data/search?aggs=level&aggs=collection&filter=group%3Atna&q=%2A&size=20"
        )

        # query with search term, non tna records
        self.response = self.client.get("/catalogue/search/?group=nonTna&q=ufo")
        self.assertEqual(self.response.status_code, HTTPStatus.OK)
        mock_logger.debug.assert_called_with(
            "https://rosetta.test/data/search?aggs=heldBy&filter=group%3AnonTna&filter=datatype%3Arecord&q=ufo&size=20"
        )

        #
        self.response = self.client.get(
            "/catalogue/search/?group=nonTna&q=ufo&collection=BT"
        )
        self.assertEqual(self.response.status_code, HTTPStatus.OK)
        mock_logger.debug.assert_called_with(
            "https://rosetta.test/data/search?aggs=heldBy&filter=group%3AnonTna&filter=datatype%3Arecord&q=ufo&size=20"
        )

    @responses.activate
    def test_catalogue_search_context_with_record_date_params(self):
        """Test that record date parameters are handled correctly"""

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
                "buckets": [
                    {
                        "name": "group",
                        "entries": [{"value": "tna", "count": 1}],
                    }
                ],
                "stats": {"total": 1, "results": 1},
            },
            status=HTTPStatus.OK,
        )

        # Test with record date parameters
        response = self.client.get(
            "/catalogue/search/?record_date_from-year=2019&record_date_from-month=1&record_date_from-day=1"
            "&record_date_to-year=2020&record_date_to-month=12&record_date_to-day=31"
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        form = response.context_data.get("form")

        # Check that date fields have cleaned values
        self.assertEqual(
            form.fields["record_date_from"].cleaned, date(2019, 1, 1)
        )
        self.assertEqual(
            form.fields["record_date_to"].cleaned, date(2020, 12, 31)
        )

        # Check that selected filters include date filters
        selected_filters = response.context_data.get("selected_filters")
        filter_labels = [f["label"] for f in selected_filters]

        self.assertIn("Record date from: 01 January 2019", filter_labels)
        self.assertIn("Record date to: 31 December 2020", filter_labels)

    @responses.activate
    def test_catalogue_search_context_with_opening_date_params_tna_only(self):
        """Test that opening date parameters only work for TNA forms"""

        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [],
                "buckets": [
                    {"name": "group", "entries": [{"value": "tna", "count": 1}]}
                ],
                "stats": {"total": 0, "results": 0},
            },
            status=HTTPStatus.OK,
        )

        # Test TNA form with opening dates
        response = self.client.get(
            "/catalogue/search/?group=tna"
            "&opening_date_from-year=2019&opening_date_from-month=6&opening_date_from-day=1"
            "&opening_date_to-year=2020&opening_date_to-month=6&opening_date_to-day=30"
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        form = response.context_data.get("form")

        # TNA form should have opening date fields
        self.assertIn("opening_date_from", form.fields)
        self.assertIn("opening_date_to", form.fields)
        self.assertEqual(
            form.fields["opening_date_from"].cleaned, date(2019, 6, 1)
        )
        self.assertEqual(
            form.fields["opening_date_to"].cleaned, date(2020, 6, 30)
        )

        # Test NonTNA form should not have opening date fields
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [],
                "buckets": [
                    {
                        "name": "group",
                        "entries": [{"value": "nonTna", "count": 1}],
                    }
                ],
                "stats": {"total": 0, "results": 0},
            },
            status=HTTPStatus.OK,
        )

        response_nontna = self.client.get(
            "/catalogue/search/?group=nonTna"
            "&opening_date_from-year=2019&opening_date_from-month=6&opening_date_from-day=1"
        )

        form_nontna = response_nontna.context_data.get("form")
        # NonTNA form should not have opening date fields
        self.assertNotIn("opening_date_from", form_nontna.fields)
        self.assertNotIn("opening_date_to", form_nontna.fields)

    @responses.activate
    def test_catalogue_search_with_partial_dates(self):
        """Test that partial dates (year-only, year-month) work correctly"""

        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [],
                "buckets": [
                    {"name": "group", "entries": [{"value": "tna", "count": 1}]}
                ],
                "stats": {"total": 0, "results": 0},
            },
            status=HTTPStatus.OK,
        )

        # Test year-only dates - should redirect with expanded parameters
        response = self.client.get(
            "/catalogue/search/?record_date_from-year=2019&record_date_to-year=2020",
            follow=True,  # Follow the redirect to get the final response
        )

        # Now we can access context_data from the final response
        form = response.context_data.get("form")
        # Year-only from date should default to Jan 1
        self.assertEqual(
            form.fields["record_date_from"].cleaned, date(2019, 1, 1)
        )
        # Year-only to date should default to Dec 31
        self.assertEqual(
            form.fields["record_date_to"].cleaned, date(2020, 12, 31)
        )

        # Test year-month dates
        response = self.client.get(
            "/catalogue/search/?record_date_from-year=2019&record_date_from-month=6"
            "&record_date_to-year=2020&record_date_to-month=6",
            follow=True,  # Follow the redirect
        )

        form = response.context_data.get("form")
        # Year-month from date should default to 1st of month
        self.assertEqual(
            form.fields["record_date_from"].cleaned, date(2019, 6, 1)
        )
        # Year-month to date should default to last day of month
        self.assertEqual(
            form.fields["record_date_to"].cleaned, date(2020, 6, 30)
        )


class CatalogueSearchViewLoggerDebugAPITests(TestCase):
    """Tests API calls (url) made by the catalogue search view."""

    @patch("app.lib.api.logger")
    @responses.activate
    def test_catalogue_debug_api(self, mock_logger):

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
                # Note: api response is not checked for these values
                "aggregations": [
                    {
                        "name": "level",
                        "entries": [
                            {"value": "somevalue", "doc_count": 100},
                        ],
                    },
                    {
                        "name": "collection",
                        "entries": [
                            {"value": "somevalue", "doc_count": 100},
                        ],
                    },
                ],
                "buckets": [
                    {
                        "name": "group",
                        "entries": [
                            # Note: api response is not checked for these values
                            {"value": "somevalue", "count": 1},
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

        # default query
        self.response = self.client.get("/catalogue/search/")
        self.assertEqual(self.response.status_code, HTTPStatus.OK)
        mock_logger.debug.assert_called_with(
            "https://rosetta.test/data/search?aggs=level&aggs=collection&filter=group%3Atna&q=%2A&size=20"
        )

        # with non default group=tna param
        self.response = self.client.get("/catalogue/search/?group=tna")
        self.assertEqual(self.response.status_code, HTTPStatus.OK)
        mock_logger.debug.assert_called_with(
            "https://rosetta.test/data/search?aggs=level&aggs=collection&filter=group%3Atna&q=%2A&size=20"
        )

        # with filter not belonging to tna group (should be ignored)
        self.response = self.client.get(
            "/catalogue/search/?group=tna&held_by=somearchive"
        )
        self.assertEqual(self.response.status_code, HTTPStatus.OK)
        mock_logger.debug.assert_called_with(
            "https://rosetta.test/data/search?aggs=level&aggs=collection&filter=group%3Atna&q=%2A&size=20"
        )

        # query with search term, non tna records
        self.response = self.client.get("/catalogue/search/?group=nonTna&q=ufo")
        self.assertEqual(self.response.status_code, HTTPStatus.OK)
        mock_logger.debug.assert_called_with(
            "https://rosetta.test/data/search?aggs=heldBy&filter=group%3AnonTna&filter=datatype%3Arecord&q=ufo&size=20"
        )

        # with filter not belonging to nontna group (should be ignored)
        self.response = self.client.get(
            "/catalogue/search/?group=nonTna&q=ufo&collection=somcollection&online=true&level=somelevel"
        )
        self.assertEqual(self.response.status_code, HTTPStatus.OK)
        mock_logger.debug.assert_called_with(
            "https://rosetta.test/data/search?aggs=heldBy&filter=group%3AnonTna&filter=datatype%3Arecord&q=ufo&size=20"
        )
