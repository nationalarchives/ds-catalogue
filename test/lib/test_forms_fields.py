from datetime import date, datetime

from app.lib.fields import (
    CharField,
    ChoiceField,
    CustomValidationError,
    DynamicMultipleChoiceField,
    MultiPartDateField,
)
from app.lib.forms import BaseForm
from django.http import QueryDict
from django.test import TestCase


class BaseFormWithDateComponentFieldTest(TestCase):

    def _process_date_components_for_form(self, query_dict):
        """
        Helper method to process date component data like the view's get_form_kwargs() does.
        This simulates the view's data processing for direct form creation in tests.
        """
        # Create a mutable copy
        processed_data = QueryDict(mutable=True)

        # Copy all existing data
        for key, values in query_dict.lists():
            for value in values:
                processed_data.appendlist(key, value)

        # Process date component data for date fields
        date_field_names = [
            "date_field",
            "from_date",
            "to_date",  # Add field names used in tests
        ]

        for field_name in date_field_names:
            day = processed_data.get(f"{field_name}-day", "")
            month = processed_data.get(f"{field_name}-month", "")
            year = processed_data.get(f"{field_name}-year", "")

            if any([day, month, year]):  # If any component exists
                # Set the field value as a dict of components
                processed_data[field_name] = {
                    "day": day,
                    "month": month,
                    "year": year,
                }

                # Remove the individual component params
                for component in ["day", "month", "year"]:
                    if f"{field_name}-{component}" in processed_data:
                        del processed_data[f"{field_name}-{component}"]

        return processed_data

    def get_form_with_date_field(self, data=None, padding_strategy=None):

        class MyTestForm(BaseForm):
            def __init__(self, data=None):
                super().__init__(data)
                # No longer need to call set_form_data() - refactored architecture handles this differently

            def add_fields(self):
                return {
                    "date_field": MultiPartDateField(
                        label="Test Date",
                        padding_strategy=padding_strategy,
                        required=False,
                    )
                }

        # Process data if provided
        processed_data = None
        if data:
            processed_data = self._process_date_components_for_form(data)

        form = MyTestForm(processed_data)
        return form

    def test_date_field_initial_attrs(self):
        form = self.get_form_with_date_field()
        self.assertEqual(form.fields["date_field"].name, "date_field")
        self.assertEqual(form.fields["date_field"].label, "Test Date")
        self.assertIsNotNone(form.fields["date_field"].padding_strategy)

    def test_date_field_empty_is_valid(self):
        data = QueryDict("")
        form = self.get_form_with_date_field(data)
        valid_status = form.is_valid()
        self.assertTrue(valid_status)
        self.assertEqual(form.fields["date_field"].cleaned, None)
        self.assertEqual(form.fields["date_field"].error, {})

    def test_date_field_full_date_valid(self):
        data = QueryDict(
            "date_field-year=2020&date_field-month=6&date_field-day=15"
        )
        form = self.get_form_with_date_field(data)
        valid_status = form.is_valid()
        self.assertTrue(valid_status)
        self.assertEqual(form.fields["date_field"].cleaned, date(2020, 6, 15))
        self.assertEqual(form.fields["date_field"].error, {})

    def test_date_field_year_only_start_strategy(self):
        data = QueryDict("date_field-year=2020")
        form = self.get_form_with_date_field(
            data, padding_strategy=MultiPartDateField.start_of_period_strategy
        )
        valid_status = form.is_valid()
        self.assertTrue(valid_status)
        # Start strategy should default to January 1st
        self.assertEqual(form.fields["date_field"].cleaned, date(2020, 1, 1))
        self.assertEqual(form.fields["date_field"].error, {})

    def test_date_field_year_only_end_strategy(self):
        data = QueryDict("date_field-year=2020")
        form = self.get_form_with_date_field(
            data, padding_strategy=MultiPartDateField.end_of_period_strategy
        )
        valid_status = form.is_valid()
        self.assertTrue(valid_status)
        # End strategy should default to December 31st
        self.assertEqual(form.fields["date_field"].cleaned, date(2020, 12, 31))
        self.assertEqual(form.fields["date_field"].error, {})

    def test_date_field_year_month_start_strategy(self):
        data = QueryDict("date_field-year=2020&date_field-month=6")
        form = self.get_form_with_date_field(
            data, padding_strategy=MultiPartDateField.start_of_period_strategy
        )
        valid_status = form.is_valid()
        self.assertTrue(valid_status)
        # Start strategy should default to 1st of month
        self.assertEqual(form.fields["date_field"].cleaned, date(2020, 6, 1))

    def test_date_field_year_month_end_strategy(self):
        data = QueryDict("date_field-year=2020&date_field-month=6")
        form = self.get_form_with_date_field(
            data, padding_strategy=MultiPartDateField.end_of_period_strategy
        )
        valid_status = form.is_valid()
        self.assertTrue(valid_status)
        # End strategy should default to last day of month (June has 30 days)
        self.assertEqual(form.fields["date_field"].cleaned, date(2020, 6, 30))

    def test_date_field_year_only_no_strategy_fails(self):
        """Test that year-only input fails without a padding strategy"""
        data = QueryDict("date_field-year=2020")
        form = self.get_form_with_date_field(data)  # No strategy provided
        valid_status = form.is_valid()
        self.assertFalse(valid_status)
        self.assertEqual(form.fields["date_field"].cleaned, None)
        self.assertEqual(
            form.fields["date_field"].error["text"],
            "Month and day are required",
        )

    def test_date_field_year_month_no_strategy_fails(self):
        """Test that year-month input fails without a padding strategy"""
        data = QueryDict("date_field-year=2020&date_field-month=6")
        form = self.get_form_with_date_field(data)  # No strategy provided
        valid_status = form.is_valid()
        self.assertFalse(valid_status)
        self.assertEqual(form.fields["date_field"].cleaned, None)
        self.assertEqual(
            form.fields["date_field"].error["text"],
            "Day is required",
        )

    def test_date_field_invalid_year(self):
        data = QueryDict("date_field-year=abc")
        form = self.get_form_with_date_field(data)
        valid_status = form.is_valid()
        self.assertFalse(valid_status)
        self.assertEqual(form.fields["date_field"].cleaned, None)
        self.assertEqual(
            form.fields["date_field"].error["text"],
            "Please enter a valid 4-digit year",
        )

    def test_date_field_invalid_month(self):
        data = QueryDict(
            "date_field-year=2020&date_field-month=13&date_field-day=1"
        )
        form = self.get_form_with_date_field(data)

        # First check the components are extracted correctly
        field = form.fields["date_field"]
        self.assertEqual(field.month, "13")  # Should be extracted as string

        valid_status = form.is_valid()

        self.assertFalse(valid_status)
        self.assertIsNone(field.cleaned)
        self.assertEqual(
            form.fields["date_field"].error["text"],
            "Month must be between 1 and 12",
        )

    def test_date_field_invalid_day_for_month(self):
        # February doesn't have 30 days
        data = QueryDict(
            "date_field-year=2020&date_field-month=2&date_field-day=30"
        )
        form = self.get_form_with_date_field(data)
        valid_status = form.is_valid()
        self.assertFalse(valid_status)
        self.assertEqual(
            form.fields["date_field"].error["text"],
            "Invalid date - please check the day is valid for the given month",
        )

    def test_date_field_day_without_month_invalid(self):
        data = QueryDict("date_field-year=2020&date_field-day=15")
        form = self.get_form_with_date_field(data)
        valid_status = form.is_valid()
        self.assertFalse(valid_status)
        self.assertEqual(
            form.fields["date_field"].error["text"],
            "Month is required if day is provided",
        )

    def test_date_field_format_for_api(self):
        data = QueryDict(
            "date_field-year=2020&date_field-month=6&date_field-day=15"
        )
        form = self.get_form_with_date_field(data)
        form.is_valid()
        # Should format as ISO date string
        self.assertEqual(
            form.fields["date_field"].format_for_api(), "2020-06-15"
        )

    def test_date_field_format_for_api_none_when_empty(self):
        data = QueryDict("")
        form = self.get_form_with_date_field(data)
        form.is_valid()
        self.assertIsNone(form.fields["date_field"].format_for_api())

    def test_date_component_field_edge_cases(self):
        """Test edge cases in MultiPartDateField validation"""

        # Test boundary years
        data = QueryDict("date_field-year=999")  # Below minimum
        form = self.get_form_with_date_field(data)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "valid 4-digit year", form.fields["date_field"].error["text"]
        )

        data = QueryDict("date_field-year=10000")  # Above maximum
        form = self.get_form_with_date_field(data)
        self.assertFalse(form.is_valid())
        self.assertIn(
            "valid 4-digit year", form.fields["date_field"].error["text"]
        )

    def test_date_component_field_february_edge_cases(self):
        """Test February edge cases including leap years"""

        # Valid leap year Feb 29
        data = QueryDict(
            "date_field-year=2020&date_field-month=2&date_field-day=29"
        )
        form = self.get_form_with_date_field(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.fields["date_field"].cleaned, date(2020, 2, 29))

        # Invalid non-leap year Feb 29
        data = QueryDict(
            "date_field-year=2021&date_field-month=2&date_field-day=29"
        )
        form = self.get_form_with_date_field(data)
        self.assertFalse(form.is_valid())
        self.assertIn("Invalid date", form.fields["date_field"].error["text"])

    def test_date_field_component_properties(self):
        """Test that component properties work correctly with dict values"""
        data = QueryDict(
            "date_field-year=2020&date_field-month=6&date_field-day=15"
        )
        form = self.get_form_with_date_field(data)
        form.is_valid()

        field = form.fields["date_field"]

        # Test that the field value is a dict
        self.assertEqual(
            field.value, {"day": "15", "month": "6", "year": "2020"}
        )

        # Test that component properties work
        self.assertEqual(field.day, "15")
        self.assertEqual(field.month, "6")
        self.assertEqual(field.year, "2020")


class BaseFormWithCrossValidationDateTest(TestCase):
    """Test cross-validation between date fields"""

    def _process_date_components_for_form(self, query_dict):
        """Helper method to process date component data"""
        processed_data = QueryDict(mutable=True)

        for key, values in query_dict.lists():
            for value in values:
                processed_data.appendlist(key, value)

        date_field_names = ["from_date", "to_date"]

        for field_name in date_field_names:
            day = processed_data.get(f"{field_name}-day", "")
            month = processed_data.get(f"{field_name}-month", "")
            year = processed_data.get(f"{field_name}-year", "")

            if any([day, month, year]):
                processed_data[field_name] = {
                    "day": day,
                    "month": month,
                    "year": year,
                }

                for component in ["day", "month", "year"]:
                    if f"{field_name}-{component}" in processed_data:
                        del processed_data[f"{field_name}-{component}"]

        return processed_data

    def get_form_with_date_range_fields(self, data=None):

        class MyTestForm(BaseForm):
            def __init__(self, data=None):
                super().__init__(data)
                # No longer need special date field handling

            def add_fields(self):
                return {
                    "from_date": MultiPartDateField(
                        label="From Date",
                        padding_strategy=MultiPartDateField.start_of_period_strategy,
                        required=False,
                    ),
                    "to_date": MultiPartDateField(
                        label="To Date",
                        padding_strategy=MultiPartDateField.end_of_period_strategy,
                        required=False,
                    ),
                }

            def cross_validate(self) -> list[str]:
                errors = []
                from_date = self.fields["from_date"].cleaned
                to_date = self.fields["to_date"].cleaned

                if from_date and to_date and from_date > to_date:
                    errors.append("From date cannot be later than to date")

                return errors

        # Process data if provided
        processed_data = None
        if data:
            processed_data = self._process_date_components_for_form(data)

        form = MyTestForm(processed_data)
        return form

    def test_valid_date_range_passes_validation(self):
        data = QueryDict(
            "from_date-year=2019&from_date-month=6&from_date-day=15"
            "&to_date-year=2020&to_date-month=6&to_date-day=15"
        )
        form = self.get_form_with_date_range_fields(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.non_field_errors), 0)

    def test_invalid_date_range_fails_validation(self):
        data = QueryDict(
            "from_date-year=2020&from_date-month=6&from_date-day=15"
            "&to_date-year=2019&to_date-month=6&to_date-day=15"
        )
        form = self.get_form_with_date_range_fields(data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.non_field_errors), 1)
        self.assertEqual(
            form.non_field_errors[0]["text"],
            "From date cannot be later than to date",
        )

    def test_same_dates_are_valid(self):
        data = QueryDict(
            "from_date-year=2020&from_date-month=6&from_date-day=15"
            "&to_date-year=2020&to_date-month=6&to_date-day=15"
        )
        form = self.get_form_with_date_range_fields(data)
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.non_field_errors), 0)


# All other test classes remain exactly the same since they don't use MultiPartDateField


class BaseFormWithCharFieldTest(TestCase):

    def get_form_with_char_field(self, data=None, required=False):

        class MyTestForm(BaseForm):
            def add_fields(self):
                return {
                    "char_field": CharField(
                        required=required,
                        hint="Enter a value",
                        label="Char Field:",
                    )
                }

        form = MyTestForm(data)
        return form

    def test_form_with_char_field_initial_attrs(self):

        form = self.get_form_with_char_field()
        self.assertEqual(form.fields["char_field"].name, "char_field")
        self.assertEqual(form.fields["char_field"].label, "Char Field:")
        self.assertEqual(form.fields["char_field"].hint, "Enter a value")

    def test_form_with_char_field_with_no_params_required_true(self):

        data = QueryDict("")
        form = self.get_form_with_char_field(data, required=True)
        valid_status = form.is_valid()
        self.assertEqual(valid_status, False)
        self.assertEqual(
            form.errors, {"char_field": {"text": "Value is required."}}
        )
        self.assertEqual(form.fields["char_field"].value, "")
        self.assertEqual(form.fields["char_field"].cleaned, None)
        self.assertEqual(
            form.fields["char_field"].error, {"text": "Value is required."}
        )

    def test_form_with_char_field_with_no_params(self):
        data = QueryDict("")
        form = self.get_form_with_char_field(data)
        valid_status = form.is_valid()
        self.assertEqual(valid_status, True)
        self.assertEqual(form.errors, {})
        self.assertEqual(form.fields["char_field"].value, "")
        self.assertEqual(form.fields["char_field"].cleaned, "")
        self.assertEqual(form.fields["char_field"].error, {})

    def test_form_with_char_field_with_param(self):

        data = QueryDict("char_field=12345")
        form = self.get_form_with_char_field(data)
        valid_status = form.is_valid()
        self.assertEqual(valid_status, True)
        self.assertEqual(form.errors, {})
        self.assertEqual(form.fields["char_field"].value, "12345")
        self.assertEqual(form.fields["char_field"].cleaned, "12345")
        self.assertEqual(form.fields["char_field"].error, {})

        # data contains whitespace
        data = QueryDict("char_field= 12345 ")
        form = self.get_form_with_char_field(data)
        valid_status = form.is_valid()
        self.assertEqual(valid_status, True)
        self.assertEqual(form.errors, {})
        self.assertEqual(form.fields["char_field"].value, " 12345 ")
        self.assertEqual(form.fields["char_field"].cleaned, "12345")
        self.assertEqual(form.fields["char_field"].error, {})

    def test_form_with_char_field_with_multiple_param_takes_last_value(self):

        data = QueryDict("char_field=ABCDE&char_field=12345")
        form = self.get_form_with_char_field(data)
        valid_status = form.is_valid()
        self.assertEqual(valid_status, True)
        self.assertEqual(form.errors, {})
        self.assertEqual(form.fields["char_field"].value, "12345")
        self.assertEqual(form.fields["char_field"].cleaned, "12345")
        self.assertEqual(form.fields["char_field"].error, {})


class BaseFormWithChoiceFieldTest(TestCase):

    def get_form_with_choice_field(self, data=None, required=False):

        class MyTestForm(BaseForm):
            def add_fields(self):
                return {
                    "choice_field": ChoiceField(
                        label="Yes/No",
                        choices=[("yes", "Yes"), ("no", "No")],
                        required=required,
                    )
                }

        form = MyTestForm(data)
        return form

    def test_form_with_choicr_field_initial_attrs(self):

        form = self.get_form_with_choice_field()
        self.assertEqual(form.fields["choice_field"].name, "choice_field")
        self.assertEqual(form.fields["choice_field"].label, "Yes/No")
        self.assertEqual(form.fields["choice_field"].hint, "")

    def test_form_with_choice_field_with_no_params_required_true(self):

        data = QueryDict("")
        form = self.get_form_with_choice_field(data, required=True)
        valid_status = form.is_valid()
        self.assertEqual(valid_status, False)
        self.assertEqual(
            form.errors, {"choice_field": {"text": "Value is required."}}
        )
        self.assertEqual(form.fields["choice_field"].value, "")
        self.assertEqual(form.fields["choice_field"].cleaned, None)
        self.assertEqual(
            form.fields["choice_field"].items,
            [{"text": "Yes", "value": "yes"}, {"text": "No", "value": "no"}],
        )
        self.assertEqual(
            form.fields["choice_field"].error, {"text": "Value is required."}
        )

    def test_form_with_choice_field_with_no_params(self):

        data = QueryDict("")
        form = self.get_form_with_choice_field(data, required=False)
        valid_status = form.is_valid()
        self.assertEqual(valid_status, False)
        self.assertEqual(
            form.errors,
            {
                "choice_field": {
                    "text": "Enter a valid choice. [Empty param value] is not "
                    "one of the available choices. Valid choices are "
                    "[yes, no]"
                }
            },
        )
        self.assertEqual(form.fields["choice_field"].value, "")
        self.assertEqual(form.fields["choice_field"].cleaned, None)
        self.assertEqual(
            form.fields["choice_field"].items,
            [{"text": "Yes", "value": "yes"}, {"text": "No", "value": "no"}],
        )
        self.assertEqual(
            form.fields["choice_field"].error,
            {
                "text": "Enter a valid choice. [Empty param value] is not "
                "one of the available choices. Valid choices are "
                "[yes, no]"
            },
        )

    def test_form_with_choice_field_with_param_with_valid_value(self):

        data = QueryDict("choice_field=yes")
        form = self.get_form_with_choice_field(data)
        valid_status = form.is_valid()
        self.assertEqual(valid_status, True)
        self.assertEqual(
            form.errors,
            {},
        )
        self.assertEqual(form.fields["choice_field"].value, "yes")
        self.assertEqual(form.fields["choice_field"].cleaned, "yes")
        self.assertEqual(
            form.fields["choice_field"].items,
            [
                {"text": "Yes", "value": "yes", "checked": True},
                {"text": "No", "value": "no"},
            ],
        )
        self.assertEqual(
            form.fields["choice_field"].error,
            {},
        )

    def test_form_with_choice_field_with_multi_param_takes_last_value(self):

        data = QueryDict("choice_field=yes&choice_field=no")
        form = self.get_form_with_choice_field(data)
        valid_status = form.is_valid()
        self.assertEqual(valid_status, True)
        self.assertEqual(
            form.errors,
            {},
        )
        self.assertEqual(form.fields["choice_field"].value, "no")
        self.assertEqual(form.fields["choice_field"].cleaned, "no")
        self.assertEqual(
            form.fields["choice_field"].items,
            [
                {"text": "Yes", "value": "yes"},
                {"text": "No", "value": "no", "checked": True},
            ],
        )
        self.assertEqual(
            form.fields["choice_field"].error,
            {},
        )

    def test_form_with_choice_field_with_param_with_invalid_value(self):

        data = QueryDict("choice_field=yes ")
        form = self.get_form_with_choice_field(data)
        valid_status = form.is_valid()
        self.assertEqual(valid_status, False)
        self.assertEqual(
            form.errors,
            {
                "choice_field": {
                    "text": (
                        "Enter a valid choice. "
                        "[yes ] is not one of the available choices. "
                        "Valid choices are [yes, no]"
                    )
                }
            },
        )
        self.assertEqual(form.fields["choice_field"].value, "yes ")
        self.assertEqual(form.fields["choice_field"].cleaned, None)
        self.assertEqual(
            form.fields["choice_field"].error,
            {
                "text": (
                    "Enter a valid choice. "
                    "[yes ] is not one of the available choices. "
                    "Valid choices are [yes, no]"
                )
            },
        )


class BaseFormWithDynamicMultipleChoiceFieldTest(TestCase):

    def get_form_with_dynamic_multiple_choice_field(self, data=None):

        class MyTestForm(BaseForm):
            def add_fields(self):
                return {
                    "dmc_field": DynamicMultipleChoiceField(
                        label="Location",
                        choices=[
                            ("london", "London"),
                            ("leeds", "Leeds"),
                        ],
                        required=True,
                        validate_input=True,
                    )
                }

        form = MyTestForm(data)
        return form

    def test_form_with_dynamic_multiple_choice_field_initial_attrs(self):

        form = self.get_form_with_dynamic_multiple_choice_field()
        self.assertEqual(form.fields["dmc_field"].name, "dmc_field")
        self.assertEqual(form.fields["dmc_field"].label, "Location")
        self.assertEqual(form.fields["dmc_field"].hint, "")

    def test_form_with_dynamic_multiple_choice_field_with_no_params(self):

        data = QueryDict("")
        form = self.get_form_with_dynamic_multiple_choice_field(data)
        valid_status = form.is_valid()
        self.assertEqual(valid_status, False)
        self.assertEqual(
            form.errors, {"dmc_field": {"text": "Value is required."}}
        )
        self.assertEqual(form.fields["dmc_field"].value, [])
        self.assertEqual(form.fields["dmc_field"].cleaned, None)
        self.assertEqual(
            form.fields["dmc_field"].items,
            [
                {"text": "London (0)", "value": "london"},
                {"text": "Leeds (0)", "value": "leeds"},
            ],
        )
        self.assertEqual(
            form.fields["dmc_field"].error, {"text": "Value is required."}
        )

    def test_form_with_dynamic_multiple_choice_field_with_param_with_valid_value(
        self,
    ):

        data = QueryDict("dmc_field=london")
        form = self.get_form_with_dynamic_multiple_choice_field(data)
        valid_status = form.is_valid()
        self.assertEqual(valid_status, True)
        self.assertEqual(form.errors, {})
        self.assertEqual(form.fields["dmc_field"].value, ["london"])
        self.assertEqual(form.fields["dmc_field"].cleaned, ["london"])
        self.assertEqual(
            form.fields["dmc_field"].items,
            [
                {
                    "text": "London",
                    "value": "london",
                    "checked": True,
                },
                {"text": "Leeds", "value": "leeds"},
            ],
        )
        self.assertEqual(form.fields["dmc_field"].error, {})

    def test_form_with_dynamic_multiple_choice_field_with_multiple_param_with_valid_values(
        self,
    ):

        data = QueryDict("dmc_field=london&dmc_field=leeds")
        form = self.get_form_with_dynamic_multiple_choice_field(data)
        valid_status = form.is_valid()
        self.assertEqual(valid_status, True)
        self.assertEqual(form.errors, {})
        self.assertEqual(form.fields["dmc_field"].name, "dmc_field")
        self.assertEqual(form.fields["dmc_field"].value, ["london", "leeds"])
        self.assertEqual(form.fields["dmc_field"].cleaned, ["london", "leeds"])
        self.assertEqual(
            form.fields["dmc_field"].items,
            [
                {
                    "text": "London",
                    "value": "london",
                    "checked": True,
                },
                {
                    "text": "Leeds",
                    "value": "leeds",
                    "checked": True,
                },
            ],
        )
        self.assertEqual(form.fields["dmc_field"].error, {})

    def test_form_with_dynamic_multiple_choice_field_with_multiple_param_with_invalid_values(
        self,
    ):

        data = QueryDict("dmc_field=london&dmc_field=manchester")
        form = self.get_form_with_dynamic_multiple_choice_field(data)
        valid_status = form.is_valid()
        self.assertEqual(valid_status, False)
        self.assertEqual(
            form.errors,
            {
                "dmc_field": {
                    "text": (
                        "Enter a valid choice. Value(s) [london, manchester] do not belong "
                        "to the available choices. Valid choices are [london, leeds]"
                    )
                }
            },
        )
        self.assertEqual(
            form.fields["dmc_field"].value, ["london", "manchester"]
        )
        self.assertEqual(
            form.fields["dmc_field"].items,
            [
                {
                    "text": "London (0)",
                    "value": "london",
                    "checked": True,
                },
            ],
        )
        self.assertEqual(
            form.fields["dmc_field"].error,
            {
                "text": (
                    "Enter a valid choice. Value(s) [london, manchester] do not belong "
                    "to the available choices. Valid choices are [london, leeds]"
                ),
            },
        )


class NewFieldWithRaiseValidationTest(TestCase):

    def get_form_with_new_field(self, data=None):

        class MyTestForm(BaseForm):

            class TestNewField(CharField):

                def validate(self, value):
                    try:
                        datetime.strptime(value, "%Y-%m-%d")
                    except ValueError:
                        raise CustomValidationError(
                            "Value is not in format YYYY-MM-DD"
                        )
                    super().validate(value)

            def add_fields(self):
                return {"new_field": MyTestForm.TestNewField()}

        form = MyTestForm(data)
        return form

    def test_validate_responds_with_no_exception(self):
        """validate() no exception is raised."""

        data = QueryDict("")
        form = self.get_form_with_new_field(data)

        try:
            status = form.is_valid()
            self.assertEqual(status, False)
            self.assertEqual(
                form.errors,
                {"new_field": {"text": "Value is not in format YYYY-MM-DD"}},
            )
            self.assertEqual(
                form.fields["new_field"].error,
                {"text": "Value is not in format YYYY-MM-DD"},
            )
        except Exception as e:
            self.fail(
                f"form.is_valid() raised an exception unexpectedly. {str(e)}"
            )


class BaseFormWithCrossValidationTest(TestCase):

    def get_form(self, data=None):

        class MyTestForm(BaseForm):
            def add_fields(self):
                return {
                    "low_value_field": CharField(required=True),
                    "high_value_field": CharField(required=True),
                }

            def cross_validate(self) -> list[str]:
                error_messages = []
                low = self.fields["low_value_field"].cleaned
                high = self.fields["high_value_field"].cleaned

                if not (high >= low):
                    error_messages.append(
                        f"Low value [{low}] must be <= High value[{high}]."
                    )
                    if high and low:
                        error_messages.append(
                            f"Alternatively supply only one value either [{low}] or [{high}]."
                        )

                return error_messages

        form = MyTestForm(data)
        return form

    def test_form_cross_validation(self):

        data = QueryDict("low_value_field=zebra&high_value_field=fox")
        form = self.get_form(data)
        valid_status = form.is_valid()
        self.assertEqual(valid_status, False)
        self.assertEqual(
            form.non_field_errors,
            [
                {"text": "Low value [zebra] must be <= High value[fox]."},
                {
                    "text": "Alternatively supply only one value either [zebra] or [fox]."
                },
            ],
        )
