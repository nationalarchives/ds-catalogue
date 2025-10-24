from datetime import date

from app.lib.fields import FromDateField, ToDateField
from app.lib.forms import BaseForm
from django.http import QueryDict
from django.test import TestCase


class BaseFormWithProgressiveDateRequiredErrorTest(TestCase):
    """Test Errors with FromDateField, ToDateField
    defaults progressive=True, required=True"""

    def get_form_with_date_fields(self, data=None):

        class MyTestForm(BaseForm):
            def add_fields(self):
                return {
                    "join_date_from": FromDateField(
                        label="From",
                        active_filter_label="Join date from",
                        progressive=True,
                        required=True,
                    ),
                    "join_date_to": ToDateField(
                        label="To",
                        active_filter_label="Join date to",
                        progressive=True,
                        required=True,
                    ),
                }

            def cross_validate(self) -> list[str]:
                error_messages = []
                date_from = self.fields["join_date_from"].cleaned
                date_to = self.fields["join_date_to"].cleaned

                if date_from and date_to and date_from > date_to:
                    error_messages.append(
                        f"Low value [{date_from}] must be <= High value[{date_to}]."
                    )

                return error_messages

        form = MyTestForm(data)
        return form

    def test_form_without_input_raises_error(self):

        data = QueryDict("")
        self.form = self.get_form_with_date_fields(data)
        self.date_from = self.form.fields["join_date_from"]
        self.date_to = self.form.fields["join_date_to"]
        valid_status = self.form.is_valid()

        # form attributes
        self.assertEqual(valid_status, False)
        self.assertEqual(
            self.form.errors,
            {
                "join_date_from": {"text": "Year value is required."},
                "join_date_to": {"text": "Year value is required."},
            },
        )
        self.assertEqual(
            self.form.non_field_errors,
            [],
        )

        # join_date_from field
        self.assertEqual(
            self.date_from.value, {"year": "", "month": "", "day": ""}
        )
        self.assertEqual(self.date_from.cleaned, None)
        self.assertEqual(
            self.date_from.error,
            {"text": "Year value is required."},
        )

        # join_date_to field
        self.assertEqual(
            self.date_to.value, {"year": "", "month": "", "day": ""}
        )
        self.assertEqual(self.date_to.cleaned, None)
        self.assertEqual(
            self.date_to.error,
            {"text": "Year value is required."},
        )

    def test_form_with_invalid_date_raises_error(self):

        data = QueryDict(
            "join_date_from-year=2000"
            "&join_date_from-month=2"
            "&join_date_from-day=31"
            "&join_date_to-year=1999"
            "&join_date_to-month=2"
            "&join_date_to-day=31"
        )
        self.form = self.get_form_with_date_fields(data)
        self.date_from = self.form.fields["join_date_from"]
        self.date_to = self.form.fields["join_date_to"]
        valid_status = self.form.is_valid()

        # form attributes
        self.assertEqual(valid_status, False)
        self.assertEqual(
            self.form.errors,
            {
                "join_date_from": {
                    "text": "Entered date must be a real date, for example Year 2017, Month 9, Day 23"
                },
                "join_date_to": {
                    "text": "Entered date must be a real date, for example Year 2017, Month 9, Day 23"
                },
            },
        )
        self.assertEqual(self.form.non_field_errors, [])

        # join_date_from field
        self.assertEqual(
            self.date_from.value, {"year": "2000", "month": "2", "day": "31"}
        )
        self.assertEqual(self.date_from.cleaned, None)
        self.assertEqual(
            self.date_from.error,
            {
                "text": "Entered date must be a real date, for example Year 2017, Month 9, Day 23"
            },
        )

        # join_date_to field
        self.assertEqual(
            self.date_to.value, {"year": "1999", "month": "2", "day": "31"}
        )
        self.assertEqual(self.date_to.cleaned, None)
        self.assertEqual(
            self.date_to.error,
            {
                "text": "Entered date must be a real date, for example Year 2017, Month 9, Day 23"
            },
        )


class BaseFormWithProgressiveDateErrorTest(TestCase):
    """Test Errors with FromDateField, ToDateField
    defaults progressive=True, required=False"""

    def get_form_with_date_fields(self, data=None):

        class MyTestForm(BaseForm):
            def add_fields(self):
                return {
                    "join_date_from": FromDateField(
                        label="From",
                        active_filter_label="Join date from",
                    ),
                    "join_date_to": ToDateField(
                        label="To",
                        active_filter_label="Join date to",
                    ),
                }

            def cross_validate(self) -> list[str]:
                error_messages = []
                date_from = self.fields["join_date_from"].cleaned
                date_to = self.fields["join_date_to"].cleaned

                if date_from and date_to and date_from > date_to:
                    error_messages.append(
                        f"Low value [{date_from}] must be <= High value[{date_to}]."
                    )

                return error_messages

        form = MyTestForm(data)
        return form

    def test_form_with_invalid_date_range_raises_error(self):

        data = QueryDict(
            "join_date_from-year=2000"
            "&join_date_from-month=1"
            "&join_date_from-day=01"
            "&join_date_to-year=1999"
            "&join_date_to-month=12"
            "&join_date_to-day=31"
        )
        self.form = self.get_form_with_date_fields(data)
        self.date_from = self.form.fields["join_date_from"]
        self.date_to = self.form.fields["join_date_to"]
        valid_status = self.form.is_valid()

        # form attributes
        self.assertEqual(valid_status, False)
        self.assertEqual(self.form.errors, {})
        self.assertEqual(
            self.form.non_field_errors,
            [
                {
                    "text": "Low value [2000-01-01] must be <= High value[1999-12-31]."
                }
            ],
        )

        # join_date_from field
        self.assertEqual(
            self.date_from.value, {"year": "2000", "month": "1", "day": "01"}
        )
        self.assertEqual(self.date_from.cleaned, date(2000, 1, 1))
        self.assertEqual(self.date_from.error, {})

        # join_date_to field
        self.assertEqual(
            self.date_to.value, {"year": "1999", "month": "12", "day": "31"}
        )
        self.assertEqual(self.date_to.cleaned, date(1999, 12, 31))
        self.assertEqual(self.date_to.error, {})

    def test_form_with_invalid_date_raises_error(self):

        data = QueryDict(
            "join_date_from-year=2000"
            "&join_date_from-month=2"
            "&join_date_from-day=31"
            "&join_date_to-year=1999"
            "&join_date_to-month=2"
            "&join_date_to-day=31"
        )
        self.form = self.get_form_with_date_fields(data)
        self.date_from = self.form.fields["join_date_from"]
        self.date_to = self.form.fields["join_date_to"]
        valid_status = self.form.is_valid()

        # form attributes
        self.assertEqual(valid_status, False)
        self.assertEqual(
            self.form.errors,
            {
                "join_date_from": {
                    "text": "Entered date must be a real date, for example Year 2017, Month 9, Day 23"
                },
                "join_date_to": {
                    "text": "Entered date must be a real date, for example Year 2017, Month 9, Day 23"
                },
            },
        )
        self.assertEqual(self.form.non_field_errors, [])

        # join_date_from field
        self.assertEqual(
            self.date_from.value, {"year": "2000", "month": "2", "day": "31"}
        )
        self.assertEqual(self.date_from.cleaned, None)
        self.assertEqual(
            self.date_from.error,
            {
                "text": "Entered date must be a real date, for example Year 2017, Month 9, Day 23"
            },
        )

        # join_date_to field
        self.assertEqual(
            self.date_to.value, {"year": "1999", "month": "2", "day": "31"}
        )
        self.assertEqual(self.date_to.cleaned, None)
        self.assertEqual(
            self.date_to.error,
            {
                "text": "Entered date must be a real date, for example Year 2017, Month 9, Day 23"
            },
        )

    def test_form_with_invalid_date_parts_raises_error(self):

        test_data = (
            (
                # label
                "Invalid-year-1",
                # data
                QueryDict("join_date_from-year=ABC"),
                # expected value
                {"year": "ABC", "month": "", "day": ""},
                # expected error
                "Year must be an integer.",
            ),
            (
                # label
                "Invalid-year-2",
                # data
                QueryDict("join_date_from-year=0"),
                # expected value
                {"year": "0", "month": "", "day": ""},
                # expected error
                "Year must be between 1 and 9999.",
            ),
            (
                # label
                "Invalid-year-3",
                # data
                QueryDict("join_date_from-year=10000"),
                # expected value
                {"year": "10000", "month": "", "day": ""},
                # expected error
                "Year must be between 1 and 9999.",
            ),
            (
                # label
                "Invalid-month-1",
                # data
                QueryDict("join_date_from-year=2000&join_date_from-month=ABC"),
                # expected value
                {"year": "2000", "month": "ABC", "day": ""},
                # expected error
                "Month must be an integer.",
            ),
            (
                # label
                "Invalid-month-2",
                # data
                QueryDict("join_date_from-year=2000&join_date_from-month=0"),
                # expected value
                {"year": "2000", "month": "0", "day": ""},
                # expected error
                "Month must be between 1 and 12.",
            ),
            (
                # label
                "Invalid-month-3",
                # data
                QueryDict("join_date_from-year=2000&join_date_from-month=13"),
                # expected value
                {"year": "2000", "month": "13", "day": ""},
                # expected error
                "Month must be between 1 and 12.",
            ),
            (
                # label
                "Invalid-day-1",
                # data
                QueryDict(
                    "join_date_from-year=2000&join_date_from-month=1&join_date_from-day=ABC"
                ),
                # expected value
                {"year": "2000", "month": "1", "day": "ABC"},
                # expected error
                "Day must be an integer.",
            ),
            (
                # label
                "Invalid-day-2",
                # data
                QueryDict(
                    "join_date_from-year=2000&join_date_from-month=1&join_date_from-day=0"
                ),
                # expected value
                {"year": "2000", "month": "1", "day": "0"},
                # expected error
                "Day must be between 1 and 31.",
            ),
            (
                # label
                "Invalid-day-3",
                # data
                QueryDict(
                    "join_date_from-year=2000&join_date_from-month=1&join_date_from-day=32"
                ),
                # expected value
                {"year": "2000", "month": "1", "day": "32"},
                # expected error
                "Day must be between 1 and 31.",
            ),
        )

        for label, data, expected_value, expected_error in test_data:
            with self.subTest(label):
                self.form = self.get_form_with_date_fields(data)
                self.date_from = self.form.fields["join_date_from"]
                self.date_to = self.form.fields["join_date_to"]
                valid_status = self.form.is_valid()

                self.assertEqual(valid_status, False)

                # expected
                self.assertEqual(self.date_from.value, expected_value)
                self.assertEqual(self.date_from.cleaned, None)
                self.assertEqual(
                    self.date_from.error.get("text"), expected_error
                )


class ProgressiveDateCrossValidateAssignFieldErrorTest(TestCase):
    """Test assigns cross validation error to field.
    Adds error to field in cross_validate using add_error method.
    This is a different approach to the above test class.
    This approach means the field shows as having an error,
    so cleaned is None, but _cleaned retains the valid date value.
    This means the valid date can still be used in active filters etc."""

    def get_form_with_date_fields(self, data=None):

        class MyTestForm(BaseForm):
            def add_fields(self):
                return {
                    "join_date_from": FromDateField(
                        label="From",
                        active_filter_label="Join date from",
                    ),
                    "join_date_to": ToDateField(
                        label="To",
                        active_filter_label="Join date to",
                    ),
                }

            def cross_validate(self) -> list[str]:
                error_messages = []
                date_from = self.fields["join_date_from"]
                date_to = self.fields["join_date_to"]

                if (
                    date_from.cleaned
                    and date_from.cleaned
                    and date_from.cleaned > date_to.cleaned
                ):
                    date_from.add_error(
                        "This date must be earlier than or equal to the 'to' date."
                    )
                    error_messages.append(
                        "Join date from: " + date_from.error.get("text")
                    )

                return error_messages

        form = MyTestForm(data)
        return form

    def test_form_with_invalid_date_range_raises_error(self):

        data = QueryDict(
            "join_date_from-year=2000"
            "&join_date_from-month=1"
            "&join_date_from-day=01"
            "&join_date_to-year=1999"
            "&join_date_to-month=12"
            "&join_date_to-day=31"
        )
        self.form = self.get_form_with_date_fields(data)
        self.date_from = self.form.fields["join_date_from"]
        self.date_to = self.form.fields["join_date_to"]
        valid_status = self.form.is_valid()

        # form attributes
        self.assertEqual(valid_status, False)
        self.assertEqual(
            self.form.errors,
            {
                "join_date_from": {
                    "text": "This date must be earlier than or equal to the 'to' date."
                }
            },
        )
        self.assertEqual(
            self.form.non_field_errors,
            [
                {
                    "text": "Join date from: This date must be earlier than or equal to the 'to' date."
                }
            ],
        )

        # join_date_from field
        self.assertEqual(
            self.date_from.value, {"year": "2000", "month": "1", "day": "01"}
        )
        # NOTE: cleaned is None because the field has an error
        self.assertEqual(self.date_from.cleaned, None)
        # NOTE: _cleaned remains set to the valid date,
        self.assertEqual(self.date_from._cleaned, date(2000, 1, 1))
        # Error assigned in cross_validate to field
        self.assertEqual(
            self.date_from.error,
            {
                "text": "This date must be earlier than or equal to the 'to' date."
            },
        )

        # join_date_to field
        self.assertEqual(
            self.date_to.value, {"year": "1999", "month": "12", "day": "31"}
        )
        self.assertEqual(self.date_to.cleaned, date(1999, 12, 31))
        self.assertEqual(self.date_to.error, {})
