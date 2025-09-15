from http import HTTPStatus

import responses
from django.conf import settings
from django.test import TestCase


class DateValidationTests(TestCase):
    """Test date field cross-validation"""

    @responses.activate
    def test_record_date_from_later_than_to_invalid(self):
        """Test that record 'from' date later than 'to' date is invalid"""

        # Mock API response (won't be called due to validation error)
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [],
                "buckets": [],
                "stats": {"total": 0, "results": 0},
            },
            status=HTTPStatus.OK,
        )

        # Submit form with invalid date range
        response = self.client.get(
            "/catalogue/search/?rd_from-year=2020&rd_from-month=6&rd_from-day=15"
            "&rd_to-year=2019&rd_to-month=3&rd_to-day=10"
        )

        # Should still return 200 but with validation errors
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Check that form validation failed
        form = response.context_data.get("form")
        self.assertFalse(form.is_valid())

        # Check for cross-validation error
        self.assertIn(
            "Record date 'from' cannot be later than 'to' date",
            [error["text"] for error in form.non_field_errors],
        )

    @responses.activate
    def test_opening_date_from_later_than_to_invalid_tna_form(self):
        """Test that opening 'from' date later than 'to' date is invalid for TNA forms"""

        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [],
                "buckets": [],
                "stats": {"total": 0, "results": 0},
            },
            status=HTTPStatus.OK,
        )

        # Submit TNA form with invalid opening date range
        response = self.client.get(
            "/catalogue/search/?group=tna"
            "&od_from-year=2020&od_from-month=12&od_from-day=31"
            "&od_to-year=2020&od_to-month=1&od_to-day=1"
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)

        form = response.context_data.get("form")
        self.assertFalse(form.is_valid())

        # Check for cross-validation error
        self.assertIn(
            "Opening date 'from' cannot be later than 'to' date",
            [error["text"] for error in form.non_field_errors],
        )

    @responses.activate
    def test_valid_date_ranges_pass_validation(self):
        """Test that valid date ranges pass validation"""

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

        # Submit form with valid date ranges
        response = self.client.get(
            "/catalogue/search/?group=tna"
            "&rd_from-year=2019&rd_from-month=1&rd_from-day=1"
            "&rd_to-year=2020&rd_to-month=12&rd_to-day=31"
            "&od_from-year=2019&od_from-month=6&od_from-day=1"
            "&od_to-year=2020&od_to-month=6&od_to-day=30"
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)

        form = response.context_data.get("form")
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.non_field_errors), 0)

    @responses.activate
    def test_same_dates_are_valid(self):
        """Test that same 'from' and 'to' dates are valid"""

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

        response = self.client.get(
            "/catalogue/search/?rd_from-year=2020&rd_from-month=6&rd_from-day=15"
            "&rd_to-year=2020&rd_to-month=6&rd_to-day=15"
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)

        form = response.context_data.get("form")
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.non_field_errors), 0)

    @responses.activate
    def test_partial_dates_cross_validation(self):
        """Test cross-validation works with partial dates (year only, year-month)"""

        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [],
                "buckets": [],
                "stats": {"total": 0, "results": 0},
            },
            status=HTTPStatus.OK,
        )

        # Test year-only dates: 2020 to 2019 should be invalid
        response = self.client.get(
            "/catalogue/search/?rd_from-year=2020&rd_to-year=2019"
        )

        form = response.context_data.get("form")
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Record date 'from' cannot be later than 'to' date",
            [error["text"] for error in form.non_field_errors],
        )

    @responses.activate
    def test_empty_dates_dont_trigger_cross_validation(self):
        """Test that empty date fields don't trigger cross-validation errors"""

        # Mock the API response
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

        response = self.client.get("/catalogue/search/")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        response_content = response.content.decode("utf-8")
        self.assertNotIn("cannot be later than", response_content)

    @responses.activate
    def test_only_one_date_field_filled_is_valid(self):
        """Test that filling only 'from' or only 'to' date is valid"""

        # Mock the API response
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

        # Only 'from' date
        response = self.client.get(
            "/catalogue/search/?rd_from-year=2020&rd_from-month=6&rd_from-day=15"
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)

        response_content = response.content.decode("utf-8")
        self.assertNotIn("cannot be later than", response_content)
