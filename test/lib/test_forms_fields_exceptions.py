from datetime import datetime

from django.http import QueryDict
from django.test import TestCase

from app.lib.fields import BaseField, CharField
from app.lib.forms import BaseForm


class NewFieldWithBadValidateTest(TestCase):

    def get_form_with_new_field(self, data=None):

        class MyTestForm(BaseForm):

            class TestNewField(CharField):

                def validate(self, value):
                    try:
                        datetime.strptime(value, "%Y-%m-%d")
                    except ValueError:
                        raise Exception("Value is not in format YYYY-MM-DD")
                    super().validate(value)

            def add_fields(self):
                return {"new_field": MyTestForm.TestNewField()}

        form = MyTestForm(data)
        return form

    def test_bad_validate_responds_with_error(self):
        """validate() should not respond with any Error. Exception is raised here."""

        data = QueryDict("")
        form = self.get_form_with_new_field(data)

        with self.assertRaises(Exception) as context:
            _ = form.is_valid()

        self.assertEqual(
            "Value is not in format YYYY-MM-DD",
            str(context.exception),
        )


class NewFieldWithBadCleanTest(TestCase):

    def get_form_with_new_field(self, data=None):

        class MyTestForm(BaseForm):

            class TestNewField(BaseField):

                def clean(self, value):
                    value = super().clean(value)

                    # transform value to something
                    # Bad transformation / UNHANDLED transformation
                    transformed_value = int(value)

                    return transformed_value

            def add_fields(self):
                return {"new_field": MyTestForm.TestNewField()}

        form = MyTestForm(data)
        return form

    def test_bad_clean_responds_with_error(self):
        """clean() should not respond with any Error. Exception is raised here."""

        data = QueryDict("")
        form = self.get_form_with_new_field(data)

        with self.assertRaises(Exception) as context:
            _ = form.is_valid()

        self.assertEqual(
            "int() argument must be a string, a bytes-like object or a real number, not 'list'",
            str(context.exception),
        )


class NewFieldWithBadBindTest(TestCase):

    def get_form_with_new_field(self, data=None):

        class MyTestForm(BaseForm):

            class TestNewField(BaseField):

                def bind(self, name, value):
                    # A BAD Binding
                    value = value[1]
                    super().bind(name, value)

            def add_fields(self):
                return {"new_field": MyTestForm.TestNewField()}

        form = MyTestForm(data)
        return form

    def test_bad_bind_responds_with_error(self):
        """bind() should not respond with any Error. Exception is raised here."""

        data = QueryDict("")

        with self.assertRaises(Exception) as context:
            _ = self.get_form_with_new_field(data)

        self.assertEqual(
            "list index out of range",
            str(context.exception),
        )
