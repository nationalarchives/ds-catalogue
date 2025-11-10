from datetime import date
from http import HTTPStatus

import responses
from app.search.forms import CatalogueSearchTnaForm, FieldsConstant
from django.conf import settings
from django.test import TestCase


class CoveringDateFilterTests(TestCase):
    """Tests covering date filter functionality in the CatalogueSearchView
    Tests form, field attributes, data, error handling and filters."""

    def setUp(self):
        self.maxDiff = None

    @responses.activate
    def test_search_with_all_date_parts(self):

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
                    },
                ],
                "aggregations": [],
                "buckets": [
                    {
                        "name": "group",
                        "entries": [
                            {"value": "tna", "count": 200},
                        ],
                    }
                ],
                "stats": {
                    "total": 1,
                    "results": 20,
                },
            },
            status=HTTPStatus.OK,
        )

        self.response = self.client.get(
            "/catalogue/search/?"
            "covering_date_from-year=1999"
            "&covering_date_from-month=01"
            "&covering_date_from-day=1"
            "&covering_date_to-year=2000"
            "&covering_date_to-month=12"
            "&covering_date_to-day=31"
        )

        form = self.response.context_data.get("form")
        valid_status = form.is_valid()
        covering_date_from_field = form.fields.get(
            FieldsConstant.COVERING_DATE_FROM
        )
        covering_date_to_field = form.fields.get(
            FieldsConstant.COVERING_DATE_TO
        )

        self.assertIsInstance(form, CatalogueSearchTnaForm)
        self.assertEqual(valid_status, True)
        self.assertEqual(len(self.response.context_data.get("results")), 1)

        # form
        self.assertEqual(form.errors, {})
        self.assertEqual(form.non_field_errors, [])

        # covering_date_from
        self.assertEqual(covering_date_from_field.required, False)
        self.assertEqual(covering_date_from_field.id, "id_covering_date_from")
        self.assertEqual(covering_date_from_field.name, "covering_date_from")
        self.assertEqual(covering_date_from_field.label, "From")
        self.assertEqual(
            covering_date_from_field.active_filter_label, "Record date from"
        )
        self.assertEqual(covering_date_from_field.progressive, True)
        self.assertEqual(
            covering_date_from_field.value,
            {"year": "1999", "month": "01", "day": "1"},
        )
        self.assertEqual(covering_date_from_field.cleaned, date(1999, 1, 1))
        self.assertEqual(covering_date_from_field.error, {})

        # covering_date_to
        self.assertEqual(covering_date_to_field.required, False)
        self.assertEqual(covering_date_to_field.id, "id_covering_date_to")
        self.assertEqual(covering_date_to_field.name, "covering_date_to")
        self.assertEqual(covering_date_to_field.label, "To")
        self.assertEqual(
            covering_date_to_field.active_filter_label, "Record date to"
        )
        self.assertEqual(covering_date_to_field.progressive, True)
        self.assertEqual(
            covering_date_to_field.value,
            {"year": "2000", "month": "12", "day": "31"},
        )
        self.assertEqual(covering_date_to_field.cleaned, date(2000, 12, 31))
        self.assertEqual(covering_date_to_field.error, {})

        # active filters
        self.assertEqual(
            self.response.context_data.get("selected_filters"),
            [
                {
                    "label": "Record date from: 01-01-1999",
                    "href": "?covering_date_to-year=2000&covering_date_to-month=12&covering_date_to-day=31&group=tna&sort=",
                    "title": "Remove 01-01-1999 record date from",
                },
                {
                    "label": "Record date to: 31-12-2000",
                    "href": "?covering_date_from-year=1999&covering_date_from-month=01&covering_date_from-day=1&group=tna&sort=",
                    "title": "Remove 31-12-2000 record date to",
                },
            ],
        )

    @responses.activate
    def test_search_with_year_date_part(self):

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
                    },
                ],
                "aggregations": [],
                "buckets": [
                    {
                        "name": "group",
                        "entries": [
                            {"value": "tna", "count": 200},
                        ],
                    }
                ],
                "stats": {
                    "total": 1,
                    "results": 20,
                },
            },
            status=HTTPStatus.OK,
        )

        self.response = self.client.get(
            "/catalogue/search/?"
            "covering_date_from-year=1999"
            "&covering_date_to-year=2000"
        )

        form = self.response.context_data.get("form")
        _ = form.is_valid()
        covering_date_from_field = form.fields.get(
            FieldsConstant.COVERING_DATE_FROM
        )
        covering_date_to_field = form.fields.get(
            FieldsConstant.COVERING_DATE_TO
        )

        self.assertEqual(
            covering_date_from_field.value,
            {"year": "1999", "month": "", "day": ""},
        )
        self.assertEqual(covering_date_from_field.cleaned, date(1999, 1, 1))
        self.assertEqual(covering_date_from_field.error, {})

        # covering_date_to
        self.assertEqual(
            covering_date_to_field.value,
            {"year": "2000", "month": "", "day": ""},
        )
        self.assertEqual(covering_date_to_field.cleaned, date(2000, 12, 31))
        self.assertEqual(covering_date_to_field.error, {})

        # active filters
        self.assertEqual(
            self.response.context_data.get("selected_filters"),
            [
                {
                    "label": "Record date from: 01-01-1999",
                    "href": "?covering_date_to-year=2000&group=tna&sort=",
                    "title": "Remove 01-01-1999 record date from",
                },
                {
                    "label": "Record date to: 31-12-2000",
                    "href": "?covering_date_from-year=1999&group=tna&sort=",
                    "title": "Remove 31-12-2000 record date to",
                },
            ],
        )


class CoveringDateFilterErrorTests(TestCase):
    """Tests covering date filter functionality in the CatalogueSearchView
    Tests field attributes, data, error handling and filters on error."""

    def setUp(self):
        self.maxDiff = None

    @responses.activate
    def test_search_with_invalid_date_range(self):
        """'From' date is after 'to' date.
        Form with error does make api call."""

        self.response = self.client.get(
            "/catalogue/search/?"
            "covering_date_from-year=2000"
            "&covering_date_to-year=1999"
        )

        form = self.response.context_data.get("form")
        covering_date_from_field = form.fields.get(
            FieldsConstant.COVERING_DATE_FROM
        )
        covering_date_to_field = form.fields.get(
            FieldsConstant.COVERING_DATE_TO
        )

        # results
        self.assertEqual(self.response.context_data.get("results"), None)

        # form
        self.assertEqual(
            form.errors,
            {
                "covering_date_from": {
                    "text": "This date must be earlier than or equal to the 'to' date."
                }
            },
        )
        self.assertEqual(
            form.non_field_errors,
            [
                {
                    "text": "Record dates: 'from' date (01-01-2000) cannot be after 'to' date (31-12-1999)."
                }
            ],
        )

        # covering_date_from
        self.assertEqual(
            covering_date_from_field.value,
            {"year": "2000", "month": "", "day": ""},
        )
        # NOTE: cleaned is None because the field has an error
        self.assertEqual(covering_date_from_field.cleaned, None)
        # NOTE: _cleaned remains set to the valid date,
        # to show it was valid before cross_validate and can be used
        # in active filters etc
        self.assertEqual(covering_date_from_field._cleaned, date(2000, 1, 1))
        self.assertEqual(
            covering_date_from_field.error,
            {
                "text": "This date must be earlier than or equal to the 'to' date."
            },
        )

        # covering_date_to
        self.assertEqual(
            covering_date_to_field.value,
            {"year": "1999", "month": "", "day": ""},
        )
        self.assertEqual(covering_date_to_field.cleaned, date(1999, 12, 31))
        self.assertEqual(covering_date_to_field.error, {})

        # active filters
        self.assertEqual(
            self.response.context_data.get("selected_filters"),
            [
                {
                    "label": "Record date to: 31-12-1999",
                    "href": "?covering_date_from-year=2000&group=tna&sort=",
                    "title": "Remove 31-12-1999 record date to",
                }
            ],
        )

    @responses.activate
    def test_search_with_invalid_date_parts(self):
        """'From' date is after 'to' date.
        Form with error does make api call."""

        self.response = self.client.get(
            "/catalogue/search/?"
            "covering_date_from-year=ABC"
            "&covering_date_to-year=PQR"
        )

        form = self.response.context_data.get("form")
        covering_date_from_field = form.fields.get(
            FieldsConstant.COVERING_DATE_FROM
        )
        covering_date_to_field = form.fields.get(
            FieldsConstant.COVERING_DATE_TO
        )

        # results
        self.assertEqual(self.response.context_data.get("results"), None)

        # form
        self.assertEqual(
            form.errors,
            {
                "covering_date_from": {"text": "Year must be an integer."},
                "covering_date_to": {"text": "Year must be an integer."},
            },
        )
        self.assertEqual(form.non_field_errors, [])

        # covering_date_from
        self.assertEqual(
            covering_date_from_field.value,
            {"year": "ABC", "month": "", "day": ""},
        )
        self.assertEqual(covering_date_from_field.cleaned, None)
        self.assertEqual(
            covering_date_from_field.error, {"text": "Year must be an integer."}
        )

        # covering_date_to
        self.assertEqual(
            covering_date_to_field.value,
            {"year": "PQR", "month": "", "day": ""},
        )
        self.assertEqual(covering_date_to_field.cleaned, None)
        self.assertEqual(
            covering_date_to_field.error, {"text": "Year must be an integer."}
        )

        # active filters
        self.assertEqual(
            self.response.context_data.get("selected_filters"),
            [],
        )
