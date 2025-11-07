from datetime import datetime

from app.lib.fields import (
    CharField,
    ChoiceField,
    ValidationError,
)
from app.lib.forms import BaseForm
from django.http import QueryDict
from django.test import TestCase


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
        self.assertEqual(form.fields["char_field"].id, "id_char_field")
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
        self.assertEqual(form.fields["choice_field"].id, "id_choice_field")
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


class NewFieldWithRaiseValidationTest(TestCase):

    def get_form_with_new_field(self, data=None):

        class MyTestForm(BaseForm):

            class TestNewField(CharField):

                def validate(self, value):
                    try:
                        datetime.strptime(value, "%Y-%m-%d")
                    except ValueError:
                        raise ValidationError(
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
