from datetime import date

from app.lib.fields import CustomValidationError, DateComponentField
from app.lib.forms import BaseForm
from app.search.forms import CatalogueSearchForm, FieldsConstant
from django.http import QueryDict
from django.test import TestCase


class DateComponentFieldTest(TestCase):
    """Test the DateComponentField in isolation"""

    def test_field_initialisation(self):
        """Test field initialises with correct defaults"""
        field_from = DateComponentField(is_from_date=True, label="Start Date")
        self.assertTrue(field_from.is_from_date)
        self.assertEqual(field_from.label, "Start Date")

        field_to = DateComponentField(is_from_date=False, label="End Date")
        self.assertFalse(field_to.is_from_date)
        self.assertEqual(field_to.label, "End Date")

    def test_field_binding_determines_from_or_to(self):
        """Test that field name determines if it's a from or to date"""
        field = DateComponentField()
        field.bind("test_from", "")
        self.assertTrue(field.is_from_date)

        field2 = DateComponentField()
        field2.bind("test_to", "")
        self.assertFalse(field2.is_from_date)

        field3 = DateComponentField()
        field3.bind("other_field", "")
        self.assertFalse(field3.is_from_date)  # Default when 'from' not in name

    def test_empty_date_is_valid_when_optional(self):
        """Test that completely empty date fields are valid when not required"""
        field = DateComponentField(required=False)
        field.bind("test_date", "")
        field.day = ""
        field.month = ""
        field.year = ""

        self.assertTrue(field.is_valid())
        self.assertIsNone(field.cleaned)
        self.assertEqual(field.error, {})

    def test_complete_date_validation(self):
        """Test validation of complete dates"""
        field = DateComponentField()
        field.bind("test_date", "")
        field.day = "15"
        field.month = "6"
        field.year = "2023"

        self.assertTrue(field.is_valid())
        self.assertEqual(field.cleaned, date(2023, 6, 15))

    def test_invalid_date_validation(self):
        """Test validation catches invalid dates"""
        field = DateComponentField()
        field.bind("test_date", "")

        # Invalid day for month (Feb 30)
        field.day = "30"
        field.month = "2"
        field.year = "2023"

        self.assertFalse(field.is_valid())
        self.assertIn("Invalid day for the given month", field.error["text"])

    def test_leap_year_validation(self):
        """Test leap year handling"""
        field = DateComponentField()
        field.bind("test_date", "")

        # Valid leap year date
        field.day = "29"
        field.month = "2"
        field.year = "2012"

        self.assertTrue(field.is_valid())
        self.assertEqual(field.cleaned, date(2012, 2, 29))

        # Invalid non-leap year date
        field.day = "29"
        field.month = "2"
        field.year = "2013"

        self.assertFalse(field.is_valid())
        self.assertIn("Invalid day for the given month", field.error["text"])

    def test_year_only_from_date(self):
        """Test year-only input for from date defaults to Jan 1"""
        field = DateComponentField(is_from_date=True)
        field.bind("test_from", "")
        field.year = "2022"
        field.month = ""
        field.day = ""

        self.assertTrue(field.is_valid())
        self.assertEqual(field.cleaned, date(2022, 1, 1))
        # Check computed values
        self.assertEqual(field.day, "1")
        self.assertEqual(field.month, "1")
        self.assertEqual(field.year, "2022")

    def test_year_only_to_date(self):
        """Test year-only input for to date defaults to Dec 31"""
        field = DateComponentField(is_from_date=False)
        field.bind("test_to", "")
        field.year = "2022"
        field.month = ""
        field.day = ""

        self.assertTrue(field.is_valid())
        self.assertEqual(field.cleaned, date(2022, 12, 31))
        # Check computed values
        self.assertEqual(field.day, "31")
        self.assertEqual(field.month, "12")
        self.assertEqual(field.year, "2022")

    def test_year_month_from_date(self):
        """Test year-month input for from date defaults to 1st of month"""
        field = DateComponentField(is_from_date=True)
        field.bind("test_from", "")
        field.year = "2022"
        field.month = "3"
        field.day = ""

        self.assertTrue(field.is_valid())
        self.assertEqual(field.cleaned, date(2022, 3, 1))
        # Check computed values
        self.assertEqual(field.day, "1")
        self.assertEqual(field.month, "3")
        self.assertEqual(field.year, "2022")

    def test_year_month_to_date_various_months(self):
        """Test year-month input for to date defaults to last day of month"""
        test_cases = [
            ("2022", "1", "31"),  # January - 31 days
            ("2022", "2", "28"),  # February non-leap - 28 days
            ("2012", "2", "29"),  # February leap year - 29 days
            ("2022", "4", "30"),  # April - 30 days
            ("2022", "12", "31"),  # December - 31 days
        ]

        for year, month, expected_day in test_cases:
            field = DateComponentField(is_from_date=False)
            field.bind("test_to", "")
            field.year = year
            field.month = month
            field.day = ""

            self.assertTrue(field.is_valid(), f"Failed for {year}-{month}")
            self.assertEqual(
                field.day, expected_day, f"Wrong day for {year}-{month}"
            )
            self.assertEqual(field.cleaned.day, int(expected_day))

    def test_partial_date_missing_year(self):
        """Test that missing year with other components raises error"""
        field = DateComponentField()
        field.bind("test_date", "")
        field.year = ""
        field.month = "6"
        field.day = "15"

        self.assertFalse(field.is_valid())
        self.assertIn("Year is required", field.error["text"])

    def test_partial_date_missing_month_with_day(self):
        """Test that having day without month raises error"""
        field = DateComponentField()
        field.bind("test_date", "")
        field.year = "2022"
        field.month = ""
        field.day = "15"

        self.assertFalse(field.is_valid())
        self.assertIn(
            "Month is required if day is provided", field.error["text"]
        )

    def test_invalid_month_range(self):
        """Test month validation (1-12)"""
        field = DateComponentField()
        field.bind("test_date", "")
        field.year = "2022"
        field.month = "13"
        field.day = "1"

        self.assertFalse(field.is_valid())
        self.assertIn("Month must be between 1 and 12", field.error["text"])

        field.month = "0"
        self.assertFalse(field.is_valid())
        self.assertIn("Month must be between 1 and 12", field.error["text"])

    def test_invalid_day_range(self):
        """Test day validation (1-31)"""
        field = DateComponentField()
        field.bind("test_date", "")
        field.year = "2022"
        field.month = "1"
        field.day = "32"

        self.assertFalse(field.is_valid())
        self.assertIn("Day must be between 1 and 31", field.error["text"])

        field.day = "0"
        self.assertFalse(field.is_valid())
        self.assertIn("Day must be between 1 and 31", field.error["text"])

    def test_invalid_year_range(self):
        """Test year validation (1000-9999)"""
        field = DateComponentField()
        field.bind("test_date", "")
        field.year = "999"
        field.month = "1"
        field.day = "1"

        self.assertFalse(field.is_valid())
        self.assertIn("valid 4-digit year", field.error["text"])

        field.year = "10000"
        self.assertFalse(field.is_valid())
        self.assertIn("valid 4-digit year", field.error["text"])

    def test_format_for_api(self):
        """Test API formatting returns YYYY-MM-DD"""
        field = DateComponentField()
        field.bind("test_date", "")
        field.year = "2023"
        field.month = "6"
        field.day = "15"

        self.assertTrue(field.is_valid())
        self.assertEqual(field.format_for_api(), "2023-06-15")

        # Test with None cleaned value
        field2 = DateComponentField()
        field2.bind("test_date2", "")
        field2.year = ""
        field2.month = ""
        field2.day = ""
        field2.is_valid()

        self.assertIsNone(field2.format_for_api())

    def test_get_computed_components(self):
        """Test getting computed components for URL building"""
        field = DateComponentField(is_from_date=False)
        field.name = "rd_to"
        field.bind("rd_to", "")
        field.year = "2012"
        field.month = "2"
        field.day = ""

        self.assertTrue(field.is_valid())

        components = field.get_computed_components()
        self.assertEqual(components["rd_to-year"], "2012")
        self.assertEqual(components["rd_to-month"], "2")
        self.assertEqual(components["rd_to-day"], "29")  # Leap year Feb


class DateComponentFieldHelperTest(TestCase):
    """Directly test DateComponentField helper methods"""

    def setUp(self):
        self.field = DateComponentField()

    def test_validate_year_accepts_valid(self):
        self.field.year = "2023"
        result = self.field._validate_year()
        self.assertEqual(result, 2023)
        self.assertEqual(self.field.year, "2023")

    def test_validate_year_rejects_invalid(self):
        self.field.year = "999"
        with self.assertRaises(CustomValidationError) as cm:
            self.field._validate_year()
        self.assertEqual(str(cm.exception), "Please enter a valid 4-digit year")

        self.field.year = "abcd"
        with self.assertRaises(CustomValidationError) as cm:
            self.field._validate_year()
        self.assertEqual(str(cm.exception), "Please enter a valid 4-digit year")

    def test_validate_month(self):
        self.field._validate_month(1)  # should not raise
        with self.assertRaises(CustomValidationError) as cm:
            self.field._validate_month(0)
        self.assertEqual(str(cm.exception), "Month must be between 1 and 12")

    def test_validate_day(self):
        self.field._validate_day(1)  # should not raise
        with self.assertRaises(CustomValidationError) as cm:
            self.field._validate_day(0)
        self.assertEqual(str(cm.exception), "Day must be between 1 and 31")

    def test_fill_year_only_start(self):
        result = self.field._fill_year_only(2020)
        self.assertEqual(result, date(2020, 1, 1))
        self.assertEqual((self.field.month, self.field.day), ("1", "1"))

    def test_fill_year_only_end(self):
        self.field.is_from_date = False
        result = self.field._fill_year_only(2020)
        self.assertEqual(result, date(2020, 12, 31))
        self.assertEqual((self.field.month, self.field.day), ("12", "31"))

    def test_fill_year_month_only_start(self):
        self.field.is_from_date = True
        self.field.month = "3"
        result = self.field._fill_year_month_only(2020)
        self.assertEqual(result, date(2020, 3, 1))
        self.assertEqual(self.field.day, "1")

    def test_fill_year_month_only_end(self):
        self.field.is_from_date = False
        self.field.month = "2"
        result = self.field._fill_year_month_only(2020)
        self.assertEqual(result, date(2020, 2, 29))  # Leap year
        self.assertEqual(self.field.day, "29")

    def test_fill_full_date_valid(self):
        self.field.month = "12"
        self.field.day = "25"
        result = self.field._fill_full_date(2020)
        self.assertEqual(result, date(2020, 12, 25))

    def test_fill_full_date_invalid_day_for_month(self):
        self.field.month = "2"
        self.field.day = "30"
        with self.assertRaises(CustomValidationError) as cm:
            self.field._fill_full_date(2020)
        self.assertEqual(str(cm.exception), "Invalid day for the given month")


class CatalogueSearchFormDateTest(TestCase):
    """Test date fields within the CatalogueSearchForm"""

    def test_form_with_complete_dates(self):
        """Test form with all date components provided"""
        data = QueryDict(
            "q=test&group=tna&"
            "rd_from-year=2020&rd_from-month=1&rd_from-day=1&"
            "rd_to-year=2023&rd_to-month=12&rd_to-day=31"
        )
        form = CatalogueSearchForm(data)

        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.fields[FieldsConstant.RECORD_DATE_FROM].cleaned,
            date(2020, 1, 1),
        )
        self.assertEqual(
            form.fields[FieldsConstant.RECORD_DATE_TO].cleaned,
            date(2023, 12, 31),
        )

    def test_form_with_partial_dates(self):
        """Test form with year-only dates"""
        data = QueryDict(
            "q=test&group=tna&"
            "rd_from-year=2020&rd_from-month=&rd_from-day=&"
            "rd_to-year=2023&rd_to-month=&rd_to-day="
        )
        form = CatalogueSearchForm(data)

        self.assertTrue(form.is_valid())

        # Check computed values
        from_field = form.fields[FieldsConstant.RECORD_DATE_FROM]
        self.assertEqual(from_field.cleaned, date(2020, 1, 1))
        self.assertEqual(from_field.day, "1")
        self.assertEqual(from_field.month, "1")

        to_field = form.fields[FieldsConstant.RECORD_DATE_TO]
        self.assertEqual(to_field.cleaned, date(2023, 12, 31))
        self.assertEqual(to_field.day, "31")
        self.assertEqual(to_field.month, "12")

    def test_form_with_year_month_dates(self):
        """Test form with year-month dates"""
        data = QueryDict(
            "q=test&group=tna&"
            "rd_from-year=2020&rd_from-month=3&rd_from-day=&"
            "rd_to-year=2020&rd_to-month=3&rd_to-day="
        )
        form = CatalogueSearchForm(data)

        self.assertTrue(form.is_valid())

        from_field = form.fields[FieldsConstant.RECORD_DATE_FROM]
        self.assertEqual(from_field.cleaned, date(2020, 3, 1))
        self.assertEqual(from_field.day, "1")

        to_field = form.fields[FieldsConstant.RECORD_DATE_TO]
        self.assertEqual(to_field.cleaned, date(2020, 3, 31))
        self.assertEqual(to_field.day, "31")

    def test_form_date_range_validation_invalid(self):
        """Test that from date > to date fails validation"""
        data = QueryDict(
            "q=test&group=tna&"
            "rd_from-year=2023&rd_from-month=6&rd_from-day=15&"
            "rd_to-year=2020&rd_to-month=1&rd_to-day=1"
        )
        form = CatalogueSearchForm(data)

        self.assertFalse(form.is_valid())
        self.assertIn(
            "Document 'from' date must be before or equal to 'to' date",
            [error["text"] for error in form.non_field_errors],
        )

    def test_form_date_range_validation_valid(self):
        """Test that from date <= to date passes validation"""
        # Test from < to
        data = QueryDict(
            "q=test&group=tna&"
            "rd_from-year=2020&rd_from-month=1&rd_from-day=1&"
            "rd_to-year=2023&rd_to-month=12&rd_to-day=31"
        )
        form = CatalogueSearchForm(data)
        self.assertTrue(form.is_valid())

        # Test from == to
        data2 = QueryDict(
            "q=test&group=tna&"
            "rd_from-year=2022&rd_from-month=6&rd_from-day=15&"
            "rd_to-year=2022&rd_to-month=6&rd_to-day=15"
        )
        form2 = CatalogueSearchForm(data2)
        self.assertTrue(form2.is_valid())

    def test_form_with_only_from_date(self):
        """Test form with only from date provided"""
        data = QueryDict(
            "q=test&group=tna&"
            "rd_from-year=2020&rd_from-month=6&rd_from-day=15&"
            "rd_to-year=&rd_to-month=&rd_to-day="
        )
        form = CatalogueSearchForm(data)

        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.fields[FieldsConstant.RECORD_DATE_FROM].cleaned,
            date(2020, 6, 15),
        )
        self.assertIsNone(form.fields[FieldsConstant.RECORD_DATE_TO].cleaned)

    def test_form_with_only_to_date(self):
        """Test form with only to date provided"""
        data = QueryDict(
            "q=test&group=tna&"
            "rd_from-year=&rd_from-month=&rd_from-day=&"
            "rd_to-year=2023&rd_to-month=6&rd_to-day=15"
        )
        form = CatalogueSearchForm(data)

        self.assertTrue(form.is_valid())
        self.assertIsNone(form.fields[FieldsConstant.RECORD_DATE_FROM].cleaned)
        self.assertEqual(
            form.fields[FieldsConstant.RECORD_DATE_TO].cleaned,
            date(2023, 6, 15),
        )

    def test_both_date_ranges(self):
        """Test form with both record and opening dates"""
        data = QueryDict(
            "q=test&group=tna&"
            "rd_from-year=2020&rd_from-month=1&rd_from-day=1&"
            "rd_to-year=2021&rd_to-month=12&rd_to-day=31&"
            "od_from-year=2022&od_from-month=1&od_from-day=1&"
            "od_to-year=2023&od_to-month=12&od_to-day=31"
        )
        form = CatalogueSearchForm(data)

        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.fields[FieldsConstant.RECORD_DATE_FROM].cleaned,
            date(2020, 1, 1),
        )
        self.assertEqual(
            form.fields[FieldsConstant.RECORD_DATE_TO].cleaned,
            date(2021, 12, 31),
        )
        self.assertEqual(
            form.fields[FieldsConstant.OPENING_DATE_FROM].cleaned,
            date(2022, 1, 1),
        )
        self.assertEqual(
            form.fields[FieldsConstant.OPENING_DATE_TO].cleaned,
            date(2023, 12, 31),
        )

    def test_opening_date_range_validation(self):
        """Test opening date range validation"""
        data = QueryDict(
            "q=test&group=tna&"
            "od_from-year=2023&od_from-month=6&od_from-day=15&"
            "od_to-year=2020&od_to-month=1&od_to-day=1"
        )
        form = CatalogueSearchForm(data)

        self.assertFalse(form.is_valid())
        self.assertIn(
            "Opening 'from' date must be before or equal to 'to' date",
            [error["text"] for error in form.non_field_errors],
        )

    def test_get_api_date_params(self):
        """Test getting formatted date parameters for API"""
        data = QueryDict(
            "q=test&group=tna&"
            "rd_from-year=2020&rd_from-month=3&rd_from-day=15&"
            "rd_to-year=2023&rd_to-month=9&rd_to-day=30&"
            "od_from-year=2022&od_from-month=&od_from-day=&"
            "od_to-year=&od_to-month=&od_to-day="
        )
        form = CatalogueSearchForm(data)

        self.assertTrue(form.is_valid())

        api_params = form.get_api_date_params()

        expected_filters = [
            "coveringFromDate:(>=2020-03-15)",
            "coveringToDate:(<=2023-09-30)",
            "openingFromDate:(>=2022-01-01)",
        ]

        self.assertEqual(len(api_params), 3)
        for expected_filter in expected_filters:
            self.assertIn(expected_filter, api_params)

    def test_get_cleaned_query_dict(self):
        """Test getting cleaned query dict with computed date values"""
        data = QueryDict(
            "q=test&group=tna&sort=&"
            "rd_from-year=2020&rd_from-month=&rd_from-day=&"
            "rd_to-year=2023&rd_to-month=2&rd_to-day="
        )
        form = CatalogueSearchForm(data)

        self.assertTrue(form.is_valid())

        cleaned_qs = form.get_cleaned_query_dict()

        # Check computed values are in the cleaned query dict
        self.assertEqual(cleaned_qs.get("rd_from-year"), "2020")
        self.assertEqual(cleaned_qs.get("rd_from-month"), "1")
        self.assertEqual(cleaned_qs.get("rd_from-day"), "1")

        self.assertEqual(cleaned_qs.get("rd_to-year"), "2023")
        self.assertEqual(cleaned_qs.get("rd_to-month"), "2")
        self.assertEqual(cleaned_qs.get("rd_to-day"), "28")  # Non-leap year Feb

    def test_leap_year_february_computation(self):
        """Test correct computation of February last day for leap/non-leap years"""
        # Leap year
        data_leap = QueryDict(
            "q=test&group=tna&" "rd_to-year=2012&rd_to-month=2&rd_to-day="
        )
        form_leap = CatalogueSearchForm(data_leap)
        self.assertTrue(form_leap.is_valid())

        to_field_leap = form_leap.fields[FieldsConstant.RECORD_DATE_TO]
        self.assertEqual(to_field_leap.cleaned, date(2012, 2, 29))
        self.assertEqual(to_field_leap.day, "29")

        # Non-leap year
        data_non_leap = QueryDict(
            "q=test&group=tna&" "rd_to-year=2013&rd_to-month=2&rd_to-day="
        )
        form_non_leap = CatalogueSearchForm(data_non_leap)
        self.assertTrue(form_non_leap.is_valid())

        to_field_non_leap = form_non_leap.fields[FieldsConstant.RECORD_DATE_TO]
        self.assertEqual(to_field_non_leap.cleaned, date(2013, 2, 28))
        self.assertEqual(to_field_non_leap.day, "28")

    def test_invalid_date_in_form(self):
        """Test that invalid dates are caught at form level"""
        data = QueryDict(
            "q=test&group=tna&"
            "rd_from-year=2023&rd_from-month=2&rd_from-day=30"  # Invalid date
        )
        form = CatalogueSearchForm(data)

        self.assertFalse(form.is_valid())
        self.assertIn("rd_from", form.errors)
        self.assertIn(
            "Invalid day for the given month", form.errors["rd_from"]["text"]
        )

    def test_mixed_partial_and_complete_dates(self):
        """Test form with mix of partial and complete dates"""
        data = QueryDict(
            "q=test&group=tna&"
            "rd_from-year=2020&rd_from-month=&rd_from-day=&"  # Year only
            "rd_to-year=2023&rd_to-month=6&rd_to-day=15&"  # Complete date
            "od_from-year=2022&od_from-month=3&od_from-day=&"  # Year-month
            "od_to-year=2024&od_to-month=&od_to-day="  # Year only
        )
        form = CatalogueSearchForm(data)

        self.assertTrue(form.is_valid())

        # Check all computed/provided values
        self.assertEqual(
            form.fields[FieldsConstant.RECORD_DATE_FROM].cleaned,
            date(2020, 1, 1),
        )
        self.assertEqual(
            form.fields[FieldsConstant.RECORD_DATE_TO].cleaned,
            date(2023, 6, 15),
        )
        self.assertEqual(
            form.fields[FieldsConstant.OPENING_DATE_FROM].cleaned,
            date(2022, 3, 1),
        )
        self.assertEqual(
            form.fields[FieldsConstant.OPENING_DATE_TO].cleaned,
            date(2024, 12, 31),
        )
