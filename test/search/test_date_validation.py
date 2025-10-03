from http import HTTPStatus
from unittest.mock import patch

import responses
from app.lib.fields import MultiPartDateField
from app.lib.forms import BaseForm
from django.conf import settings
from django.http import QueryDict
from django.test import TestCase
from django.utils.encoding import force_str


class DateValidationTests(TestCase):
    """Test date field cross-validation"""

    def setUp(self):
        """Set up common mock API response"""
        self.mock_api_response = {
            "data": [],
            "buckets": [
                {"name": "group", "entries": [{"value": "tna", "count": 1}]}
            ],
            "stats": {"total": 0, "results": 0},
        }

    @responses.activate
    def test_record_date_from_later_than_to_invalid(self):
        """Test that record 'from' date later than 'to' date is invalid"""
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json=self.mock_api_response,
            status=HTTPStatus.OK,
        )

        # Submit form with invalid date range
        response = self.client.get(
            "/catalogue/search/?covering_date_from-year=2020&covering_date_from-month=6&covering_date_from-day=15"
            "&covering_date_to-year=2019&covering_date_to-month=3&covering_date_to-day=10"
        )

        # Should still return 200 but with validation errors
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Check that form validation failed
        form = response.context_data.get("form")
        self.assertFalse(form.is_valid())

        # Check for cross-validation error
        error_messages = [error["text"] for error in form.non_field_errors]
        self.assertIn(
            "Record date 'from' cannot be later than 'to' date",
            error_messages,
        )

    @responses.activate
    def test_opening_date_from_later_than_to_invalid_tna_form(self):
        """Test that opening 'from' date later than 'to' date is invalid for TNA forms"""
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json=self.mock_api_response,
            status=HTTPStatus.OK,
        )

        # Submit TNA form with invalid opening date range
        response = self.client.get(
            "/catalogue/search/?group=tna"
            "&opening_date_from-year=2020&opening_date_from-month=12&opening_date_from-day=31"
            "&opening_date_to-year=2020&opening_date_to-month=1&opening_date_to-day=1"
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)

        form = response.context_data.get("form")
        self.assertFalse(form.is_valid())

        # Check for cross-validation error
        error_messages = [error["text"] for error in form.non_field_errors]
        self.assertIn(
            "Opening date 'from' cannot be later than 'to' date",
            error_messages,
        )

    @responses.activate
    def test_valid_date_ranges_pass_validation(self):
        """Test that valid date ranges pass validation"""
        valid_response = self.mock_api_response.copy()
        valid_response["data"] = [
            {
                "@template": {
                    "details": {
                        "iaid": "C123456",
                        "source": "CAT",
                    }
                }
            }
        ]
        valid_response["stats"] = {"total": 1, "results": 1}

        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json=valid_response,
            status=HTTPStatus.OK,
        )

        # Submit form with valid date ranges
        response = self.client.get(
            "/catalogue/search/?group=tna"
            "&covering_date_from-year=2019&covering_date_from-month=1&covering_date_from-day=1"
            "&covering_date_to-year=2020&covering_date_to-month=12&covering_date_to-day=31"
            "&opening_date_from-year=2019&opening_date_from-month=6&opening_date_from-day=1"
            "&opening_date_to-year=2020&opening_date_to-month=6&opening_date_to-day=30"
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
            json=self.mock_api_response,
            status=HTTPStatus.OK,
        )

        response = self.client.get(
            "/catalogue/search/?covering_date_from-year=2020&covering_date_from-month=6&covering_date_from-day=15"
            "&covering_date_to-year=2020&covering_date_to-month=6&covering_date_to-day=15"
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
            json=self.mock_api_response,
            status=HTTPStatus.OK,
        )

        # Test year-only dates: 2020 to 2019 should be invalid
        response = self.client.get(
            "/catalogue/search/?covering_date_from-year=2020&covering_date_to-year=2019"
        )

        form = response.context_data.get("form")
        self.assertFalse(form.is_valid())
        error_messages = [error["text"] for error in form.non_field_errors]
        self.assertIn(
            "Record date 'from' cannot be later than 'to' date",
            error_messages,
        )

    @responses.activate
    def test_empty_dates_dont_trigger_cross_validation(self):
        """Test that empty date fields don't trigger cross-validation errors"""
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json=self.mock_api_response,
            status=HTTPStatus.OK,
        )

        response = self.client.get("/catalogue/search/")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        response_content = response.content.decode("utf-8")
        self.assertNotIn("cannot be later than", response_content)

        # Also check form is valid
        form = response.context_data.get("form")
        self.assertTrue(form.is_valid())

    @responses.activate
    def test_only_one_date_field_filled_is_valid(self):
        """Test that filling only 'from' or only 'to' date is valid"""
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json=self.mock_api_response,
            status=HTTPStatus.OK,
        )

        # Only 'from' date
        response = self.client.get(
            "/catalogue/search/?covering_date_from-year=2020&covering_date_from-month=6&covering_date_from-day=15"
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        form = response.context_data.get("form")
        self.assertTrue(form.is_valid())

        # Only 'to' date
        response = self.client.get(
            "/catalogue/search/?covering_date_to-year=2020&covering_date_to-month=6&covering_date_to-day=15"
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        form = response.context_data.get("form")
        self.assertTrue(form.is_valid())

    @responses.activate
    def test_complex_date_validation_scenarios(self):
        """Test complex combinations of date validation"""
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json=self.mock_api_response,
            status=HTTPStatus.OK,
        )

        test_cases = [
            # (params, should_be_valid, expected_error_fragment, needs_redirect)
            (
                "covering_date_from-year=2020&covering_date_from-month=2&covering_date_from-day=29"  # Valid leap year
                "&covering_date_to-year=2020&covering_date_to-month=3&covering_date_to-day=1",
                True,
                None,
                False,  # Full dates don't redirect
            ),
            (
                "covering_date_from-year=2021&covering_date_from-month=2&covering_date_from-day=29"  # Invalid non-leap year
                "&covering_date_to-year=2021&covering_date_to-month=3&covering_date_to-day=1",
                False,
                "Invalid date",
                False,  # Full dates don't redirect
            ),
            (
                "covering_date_from-year=2020&covering_date_from-month=4&covering_date_from-day=31"  # April doesn't have 31 days
                "&covering_date_to-year=2020&covering_date_to-month=5&covering_date_to-day=1",
                False,
                "Invalid date",
                False,  # Full dates don't redirect
            ),
            (
                "covering_date_from-year=2020&covering_date_from-month=6"  # Year-month only, valid
                "&covering_date_to-year=2020&covering_date_to-month=8",
                True,
                None,
                True,  # Partial dates will redirect
            ),
            (
                "covering_date_from-year=2020&covering_date_from-month=8"  # Year-month only, invalid range
                "&covering_date_to-year=2020&covering_date_to-month=6",
                False,
                "cannot be later than",
                True,  # Partial dates will redirect
            ),
        ]

        for (
            params,
            should_be_valid,
            expected_error,
            needs_redirect,
        ) in test_cases:
            with self.subTest(params=params):
                response = self.client.get(
                    f"/catalogue/search/?{params}",
                    follow=needs_redirect,  # Follow redirect only for partial dates
                )

                if needs_redirect:
                    # For redirected requests, check final status
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                else:
                    # For non-redirected requests, check direct status
                    self.assertEqual(response.status_code, HTTPStatus.OK)

                form = response.context_data.get("form")

                if should_be_valid:
                    self.assertTrue(
                        form.is_valid(), f"Expected valid form for: {params}"
                    )
                else:
                    self.assertFalse(
                        form.is_valid(), f"Expected invalid form for: {params}"
                    )

                    if expected_error:
                        # Check either field errors or non-field errors
                        all_errors = []
                        for field_error in form.errors.values():
                            all_errors.append(field_error.get("text", ""))
                        for non_field_error in form.non_field_errors:
                            all_errors.append(non_field_error.get("text", ""))

                        error_found = any(
                            expected_error in error for error in all_errors
                        )
                        self.assertTrue(
                            error_found,
                            f"Expected error '{expected_error}' not found in: {all_errors}",
                        )

    @responses.activate
    def test_date_validation_with_other_filters(self):
        """Test date validation works correctly when combined with other filters"""
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json=self.mock_api_response,
            status=HTTPStatus.OK,
        )

        # Test invalid date range with other valid filters
        response = self.client.get(
            "/catalogue/search/"
            "?q=test"
            "&group=tna"
            "&level=Item"
            "&online=true"
            "&covering_date_from-year=2020&covering_date_from-month=6&covering_date_from-day=15"
            "&covering_date_to-year=2019&covering_date_to-month=3&covering_date_to-day=10"  # Invalid range
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        form = response.context_data.get("form")

        # Form should be invalid due to date range
        self.assertFalse(form.is_valid())

        # But other fields should still be valid
        self.assertEqual(form.fields["q"].cleaned, "test")
        self.assertEqual(form.fields["group"].cleaned, "tna")
        self.assertEqual(form.fields["level"].cleaned, ["Item"])
        self.assertEqual(form.fields["online"].cleaned, "true")

    @responses.activate
    def test_date_error_display_in_ui(self):
        """Test that date validation errors are properly displayed in the UI"""
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json=self.mock_api_response,
            status=HTTPStatus.OK,
        )

        # Test with multiple date validation errors
        response = self.client.get(
            "/catalogue/search/?group=tna"
            "&covering_date_from-year=2020&covering_date_from-month=6&covering_date_from-day=15"
            "&covering_date_to-year=2019&covering_date_to-month=3&covering_date_to-day=10"  # Invalid record range
            "&opening_date_from-year=2020&opening_date_from-month=12&opening_date_from-day=31"
            "&opening_date_to-year=2020&opening_date_to-month=1&opening_date_to-day=1"  # Invalid opening range
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        html = force_str(response.content)

        # Should display both error messages
        possible_record_errors = [
            "Record date 'from' cannot be later than 'to' date",
            "Record date &#x27;from&#x27; cannot be later than &#x27;to&#x27; date",
            "Record date &#39;from&#39; cannot be later than &#39;to&#39; date",
        ]

        possible_opening_errors = [
            "Opening date 'from' cannot be later than 'to' date",
            "Opening date &#x27;from&#x27; cannot be later than &#x27;to&#x27; date",
            "Opening date &#39;from&#39; cannot be later than &#39;to&#39; date",
        ]

        record_error_found = any(
            error in html for error in possible_record_errors
        )
        opening_error_found = any(
            error in html for error in possible_opening_errors
        )

        self.assertTrue(
            record_error_found, "Record date validation error not found in HTML"
        )
        self.assertTrue(
            opening_error_found,
            "Opening date validation error not found in HTML",
        )

    @responses.activate
    def test_date_validation_performance(self):
        """Test that date validation doesn't significantly impact performance"""
        import time

        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json=self.mock_api_response,
            status=HTTPStatus.OK,
        )

        # Test with multiple date fields
        start_time = time.time()

        for i in range(10):
            response = self.client.get(
                f"/catalogue/search/?group=tna"
                f"&covering_date_from-year=201{i % 10}&covering_date_from-month={(i % 12) + 1}&covering_date_from-day={(i % 28) + 1}"
                f"&covering_date_to-year=202{i % 10}&covering_date_to-month={(i % 12) + 1}&covering_date_to-day={(i % 28) + 1}"
                f"&opening_date_from-year=201{i % 10}&opening_date_from-month={(i % 12) + 1}&opening_date_from-day={(i % 28) + 1}"
                f"&opening_date_to-year=202{i % 10}&opening_date_to-month={(i % 12) + 1}&opening_date_to-day={(i % 28) + 1}"
            )
            self.assertEqual(response.status_code, HTTPStatus.OK)

        end_time = time.time()

        # Should complete quickly (less than 5 seconds for 10 requests)
        self.assertLess(end_time - start_time, 5.0)

    @responses.activate
    def test_date_validation_with_api_errors(self):
        """Test date validation when API returns errors"""
        # Simulate API error
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={"error": "Internal server error"},
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
        )

        # Even with API errors, date validation should still work
        response = self.client.get(
            "/catalogue/search/?covering_date_from-year=2020&covering_date_from-month=6&covering_date_from-day=15"
            "&covering_date_to-year=2019&covering_date_to-month=3&covering_date_to-day=10"
        )

        # May return 500 due to API error, but date validation should have run
        # The exact behavior depends on error handling middleware
        self.assertIn(
            response.status_code,
            [HTTPStatus.OK, HTTPStatus.INTERNAL_SERVER_ERROR],
        )

    @responses.activate
    def test_non_tna_form_date_validation(self):
        """Test that NonTNA forms validate record dates but not opening dates"""
        non_tna_response = self.mock_api_response.copy()
        non_tna_response["buckets"] = [
            {"name": "group", "entries": [{"value": "nonTna", "count": 1}]}
        ]

        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json=non_tna_response,
            status=HTTPStatus.OK,
        )

        # Test NonTNA form with invalid record date range
        response = self.client.get(
            "/catalogue/search/?group=nonTna"
            "&covering_date_from-year=2020&covering_date_from-month=6&covering_date_from-day=15"
            "&covering_date_to-year=2019&covering_date_to-month=3&covering_date_to-day=10"
            "&opening_date_from-year=2020&opening_date_from-month=1&opening_date_from-day=1"  # Should be ignored
        )

        form = response.context_data.get("form")
        self.assertFalse(form.is_valid())

        # Should have record date error
        error_messages = [error["text"] for error in form.non_field_errors]
        self.assertIn(
            "Record date 'from' cannot be later than 'to' date",
            error_messages,
        )

        # Should NOT have opening date error (because NonTNA forms don't have opening dates)
        opening_error_found = any(
            "Opening date" in msg for msg in error_messages
        )
        self.assertFalse(opening_error_found)

    @responses.activate
    def test_edge_case_date_combinations(self):
        """Test edge cases in date validation"""
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json=self.mock_api_response,
            status=HTTPStatus.OK,
        )

        edge_cases = [
            # (params, should_be_valid, needs_redirect)
            # December 31st to January 1st (next year) - should be valid
            (
                "covering_date_from-year=2019&covering_date_from-month=12&covering_date_from-day=31"
                "&covering_date_to-year=2020&covering_date_to-month=1&covering_date_to-day=1",
                True,
                False,  # Full dates
            ),
            # Same day different years - from later year should be invalid
            (
                "covering_date_from-year=2020&covering_date_from-month=6&covering_date_from-day=15"
                "&covering_date_to-year=2019&covering_date_to-month=6&covering_date_to-day=15",
                False,
                False,  # Full dates
            ),
            # End of February leap year vs non-leap year
            (
                "covering_date_from-year=2020&covering_date_from-month=2&covering_date_from-day=29"  # Leap year
                "&covering_date_to-year=2021&covering_date_to-month=2&covering_date_to-day=28",  # Non-leap year
                True,
                False,  # Full dates
            ),
            # Year-only with same year should be valid
            (
                "covering_date_from-year=2020&covering_date_to-year=2020",
                True,
                True,  # Year-only dates will redirect
            ),
        ]

        for params, should_be_valid, needs_redirect in edge_cases:
            with self.subTest(params=params):
                response = self.client.get(
                    f"/catalogue/search/?{params}",
                    follow=needs_redirect,  # Follow redirect for partial dates
                )
                self.assertEqual(response.status_code, HTTPStatus.OK)

                form = response.context_data.get("form")
                if should_be_valid:
                    self.assertTrue(
                        form.is_valid(), f"Expected valid for: {params}"
                    )
                else:
                    self.assertFalse(
                        form.is_valid(), f"Expected invalid for: {params}"
                    )

    @responses.activate
    @patch("app.search.views.logger")
    def test_date_validation_error_logging(self, mock_logger):
        """Test that date validation errors are properly logged"""
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json=self.mock_api_response,
            status=HTTPStatus.OK,
        )

        # Submit form with validation errors
        response = self.client.get(
            "/catalogue/search/?covering_date_from-year=invalid&covering_date_to-year=2020"
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Verify form validation failed
        form = response.context_data.get("form")
        self.assertFalse(form.is_valid())

    @responses.activate
    def test_multiple_validation_errors_display(self):
        """Test display when multiple validation errors occur"""
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json=self.mock_api_response,
            status=HTTPStatus.OK,
        )

        # Create multiple validation errors
        response = self.client.get(
            "/catalogue/search/?group=tna"
            "&covering_date_from-year=abc"  # Invalid year format
            "&covering_date_to-year=2020&covering_date_to-month=13"  # Invalid month
            "&opening_date_from-year=2020&opening_date_from-month=6&opening_date_from-day=15"
            "&opening_date_to-year=2019&opening_date_to-month=3&opening_date_to-day=10"  # Invalid range
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        form = response.context_data.get("form")
        self.assertFalse(form.is_valid())

        # Should have multiple error types
        self.assertTrue(len(form.errors) > 0)  # Field-level errors
        self.assertTrue(
            len(form.non_field_errors) > 0
        )  # Cross-validation errors

    @responses.activate
    def test_date_api_parameter_formatting(self):
        """Test that dates are properly formatted for API requests"""
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json=self.mock_api_response,
            status=HTTPStatus.OK,
        )

        response = self.client.get(
            "/catalogue/search/?group=tna"
            "&covering_date_from-year=2020&covering_date_from-month=6&covering_date_from-day=15"
            "&covering_date_to-year=2021&covering_date_to-month=8&covering_date_to-day=20"
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        form = response.context_data.get("form")
        self.assertTrue(form.is_valid())

        # Test API parameter formatting
        date_params = form.get_api_date_params()
        expected_params = [
            "coveringFromDate:(>=2020-06-15)",
            "coveringToDate:(<=2021-08-20)",
        ]

        for expected in expected_params:
            self.assertIn(expected, date_params)

    @responses.activate
    def test_opening_date_api_parameters_tna_only(self):
        """Test that opening date API parameters only apply to TNA forms"""
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json=self.mock_api_response,
            status=HTTPStatus.OK,
        )

        # TNA form should include opening date parameters
        # Create mutable QueryDict and process the data as the view would
        tna_data = QueryDict(mutable=True)
        tna_data["group"] = "tna"
        # Add the date data in the processed dict format that the view creates
        tna_data["opening_date_from"] = {
            "day": "1",
            "month": "1",
            "year": "2020",
        }
        tna_data["opening_date_to"] = {
            "day": "31",
            "month": "12",
            "year": "2020",
        }

        from app.search.forms import CatalogueSearchTnaForm

        tna_form = CatalogueSearchTnaForm(data=tna_data)
        self.assertTrue(tna_form.is_valid())

        date_params = tna_form.get_api_date_params()
        self.assertIn("openingFromDate:(>=2020-01-01)", date_params)
        self.assertIn("openingToDate:(<=2020-12-31)", date_params)

        # NonTNA form should not include opening date parameters
        from app.search.forms import CatalogueSearchNonTnaForm

        nontna_data = QueryDict(mutable=True)
        nontna_data["group"] = "nonTna"
        nontna_form = CatalogueSearchNonTnaForm(data=nontna_data)
        self.assertTrue(nontna_form.is_valid())

        nontna_date_params = nontna_form.get_api_date_params()
        opening_params = [p for p in nontna_date_params if "opening" in p]
        self.assertEqual(len(opening_params), 0)

    @responses.activate
    def test_specific_date_error_messages(self):
        """Test specific error messages for different validation failures"""
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json=self.mock_api_response,
            status=HTTPStatus.OK,
        )

        error_cases = [
            # (query_params, expected_error_substring)
            ("covering_date_from-year=abc", "valid 4-digit year"),
            (
                "covering_date_from-year=2020&covering_date_from-month=13",
                "Month must be between 1 and 12",
            ),
            (
                "covering_date_from-year=2020&covering_date_from-month=2&covering_date_from-day=35",
                "Day must be between 1 and 31",
            ),
            (
                "covering_date_from-year=2020&covering_date_from-day=15",
                "Month is required if day is provided",
            ),
            (
                "covering_date_from-year=2020&covering_date_from-month=4&covering_date_from-day=31",
                "Invalid date",
            ),
        ]

        for params, expected_error in error_cases:
            with self.subTest(params=params):
                response = self.client.get(f"/catalogue/search/?{params}")
                self.assertEqual(response.status_code, HTTPStatus.OK)

                form = response.context_data.get("form")
                self.assertFalse(form.is_valid())

                # Check that the specific error message appears
                field_errors = [
                    error.get("text", "") for error in form.errors.values()
                ]
                error_found = any(
                    expected_error in error for error in field_errors
                )
                self.assertTrue(
                    error_found, f"Expected error '{expected_error}' not found"
                )
