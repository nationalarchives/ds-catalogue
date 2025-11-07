from datetime import date

from app.lib.fields import FromDateField, ToDateField
from app.lib.forms import BaseForm
from django.http import QueryDict
from django.test import TestCase


class BaseFormWithProgressiveDatesTest(TestCase):
    """Test BaseForm with FromDateField, ToDateField
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

    def test_form_with_date_fields_initial_attrs(self):

        data = QueryDict("")  # no params
        self.form = self.get_form_with_date_fields(data)
        self.date_from = self.form.fields["join_date_from"]
        self.date_to = self.form.fields["join_date_to"]
        valid_status = self.form.is_valid()

        # form attributes
        self.assertEqual(valid_status, True)
        self.assertEqual(self.form.errors, {})
        self.assertEqual(self.form.non_field_errors, [])

        # join_date_from field
        self.assertEqual(self.date_from.progressive, True)
        self.assertEqual(self.date_from.required, False)
        self.assertEqual(self.date_from.id, "id_join_date_from")
        self.assertEqual(self.date_from.name, "join_date_from")
        self.assertEqual(self.date_from.label, "From")
        self.assertEqual(self.date_from.active_filter_label, "Join date from")
        self.assertEqual(self.date_from.hint, "")
        self.assertEqual(
            self.date_from.value, {"year": "", "month": "", "day": ""}
        )
        self.assertEqual(self.date_from.cleaned, None)
        self.assertEqual(self.date_from.error, {})

        # join_date_to field
        self.assertEqual(self.date_to.progressive, True)
        self.assertEqual(self.date_to.required, False)
        self.assertEqual(self.date_to.id, "id_join_date_to")
        self.assertEqual(self.date_to.name, "join_date_to")
        self.assertEqual(self.date_to.label, "To")
        self.assertEqual(self.date_to.active_filter_label, "Join date to")
        self.assertEqual(self.date_to.hint, "")
        self.assertEqual(
            self.date_to.value, {"year": "", "month": "", "day": ""}
        )
        self.assertEqual(self.date_to.cleaned, None)
        self.assertEqual(self.date_to.error, {})

    def test_form_with_date_fields_all_parts(self):

        data = QueryDict(
            "join_date_from-year=1999"
            "&join_date_from-month=12"
            "&join_date_from-day=31"
            "&join_date_to-year=2000"
            "&join_date_to-month=1"
            "&join_date_to-day=01"
        )
        self.form = self.get_form_with_date_fields(data)
        self.date_from = self.form.fields["join_date_from"]
        self.date_to = self.form.fields["join_date_to"]
        valid_status = self.form.is_valid()

        # form attributes
        self.assertEqual(valid_status, True)
        self.assertEqual(self.form.errors, {})
        self.assertEqual(self.form.non_field_errors, [])

        # join_date_from field
        self.assertEqual(
            self.date_from.value, {"year": "1999", "month": "12", "day": "31"}
        )
        self.assertEqual(self.date_from.cleaned, date(1999, 12, 31))
        self.assertEqual(self.date_from.error, {})

        # join_date_to field
        self.assertEqual(
            self.date_to.value, {"year": "2000", "month": "1", "day": "01"}
        )
        self.assertEqual(self.date_to.cleaned, date(2000, 1, 1))
        self.assertEqual(self.date_to.error, {})

    def test_form_with_leap_and_non_leap_years_ranges(self):

        # leap year 2000 date_from to non-leap year 2001 date_to
        data = QueryDict(
            "join_date_from-year=2000"
            "&join_date_from-month=2"
            "&join_date_from-day=29"
            "&join_date_to-year=2001"
            "&join_date_to-month=02"
            "&join_date_to-day=28"
        )
        self.form = self.get_form_with_date_fields(data)
        self.date_from = self.form.fields["join_date_from"]
        self.date_to = self.form.fields["join_date_to"]
        valid_status = self.form.is_valid()

        # form attributes
        self.assertEqual(valid_status, True)
        self.assertEqual(self.form.errors, {})
        self.assertEqual(self.form.non_field_errors, [])

        # join_date_from field
        self.assertEqual(
            self.date_from.value, {"year": "2000", "month": "2", "day": "29"}
        )
        self.assertEqual(self.date_from.cleaned, date(2000, 2, 29))
        self.assertEqual(self.date_from.error, {})

        # join_date_to field
        self.assertEqual(
            self.date_to.value, {"year": "2001", "month": "02", "day": "28"}
        )
        self.assertEqual(self.date_to.cleaned, date(2001, 2, 28))
        self.assertEqual(self.date_to.error, {})

    def test_form_with_date_fields_year_part(self):

        data = QueryDict("join_date_from-year=1999" "&join_date_to-year=2000")
        self.form = self.get_form_with_date_fields(data)
        self.date_from = self.form.fields["join_date_from"]
        self.date_to = self.form.fields["join_date_to"]
        valid_status = self.form.is_valid()

        # form attributes
        self.assertEqual(valid_status, True)
        self.assertEqual(self.form.errors, {})
        self.assertEqual(self.form.non_field_errors, [])

        # join_date_from field
        self.assertEqual(
            self.date_from.value, {"year": "1999", "month": "", "day": ""}
        )
        self.assertEqual(self.date_from.cleaned, date(1999, 1, 1))
        self.assertEqual(self.date_from.error, {})

        # join_date_to field
        self.assertEqual(
            self.date_to.value, {"year": "2000", "month": "", "day": ""}
        )
        self.assertEqual(self.date_to.cleaned, date(2000, 12, 31))
        self.assertEqual(self.date_to.error, {})

    def test_form_with_date_fields_month_part(self):

        data = QueryDict(
            "join_date_from-year=1999"
            "&join_date_from-month=1"
            "&join_date_to-year=2000"
            "&join_date_to-month=2"
        )
        self.form = self.get_form_with_date_fields(data)
        self.date_from = self.form.fields["join_date_from"]
        self.date_to = self.form.fields["join_date_to"]
        valid_status = self.form.is_valid()

        # form attributes
        self.assertEqual(valid_status, True)
        self.assertEqual(self.form.errors, {})
        self.assertEqual(self.form.non_field_errors, [])

        # join_date_from field
        self.assertEqual(
            self.date_from.value, {"year": "1999", "month": "1", "day": ""}
        )
        self.assertEqual(self.date_from.cleaned, date(1999, 1, 1))
        self.assertEqual(self.date_from.error, {})

        # join_date_to field
        self.assertEqual(
            self.date_to.value, {"year": "2000", "month": "2", "day": ""}
        )
        self.assertEqual(self.date_to.cleaned, date(2000, 2, 29))
        self.assertEqual(self.date_to.error, {})
