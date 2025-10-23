from app.lib.fields import DynamicMultipleChoiceField
from app.lib.forms import BaseForm
from django.http import QueryDict
from django.test import TestCase


class BaseFormWithDMCFieldValidateInputTrueTest(TestCase):

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
        self.assertEqual(form.fields["dmc_field"].required, True)
        self.assertEqual(form.fields["dmc_field"].validate_input, True)
        self.assertEqual(form.fields["dmc_field"].active_filter_label, None)
        self.assertEqual(
            form.fields["dmc_field"].choices,
            [("london", "London"), ("leeds", "Leeds")],
        )
        self.assertEqual(
            form.fields["dmc_field"].configured_choices,
            [("london", "London"), ("leeds", "Leeds")],
        )
        self.assertEqual(form.fields["dmc_field"]._cleaned, None)
        self.assertEqual(form.fields["dmc_field"].cleaned, None)
        self.assertEqual(form.fields["dmc_field"].error, {})
        # as this is not a view test, before items called, choices not updated
        self.assertEqual(form.fields["dmc_field"].choices_updated, False)
        self.assertEqual(
            form.fields["dmc_field"].items, []
        )  # should be empty until choices are updated
        # as this is not a view test, after items called, choices are updated
        self.assertEqual(form.fields["dmc_field"].choices_updated, True)

    def test_form_with_dynamic_multiple_choice_field_error_with_no_params(self):

        data = QueryDict("")  # no params
        form = self.get_form_with_dynamic_multiple_choice_field(data)
        valid_status = form.is_valid()
        self.assertEqual(valid_status, False)
        self.assertEqual(
            form.errors, {"dmc_field": {"text": "Value is required."}}
        )
        self.assertEqual(form.fields["dmc_field"].value, [])
        self.assertEqual(form.fields["dmc_field"].cleaned, None)
        # as this is not a view test, before items called, choices not updated
        self.assertEqual(form.fields["dmc_field"].choices_updated, False)
        # required field with no input, so items is empty
        self.assertEqual(form.fields["dmc_field"].items, [])
        # as this is not a view test, after items called, choices are updated
        self.assertEqual(form.fields["dmc_field"].choices_updated, True)
        self.assertEqual(
            form.fields["dmc_field"].error, {"text": "Value is required."}
        )

    def test_form_with_dynamic_multiple_choice_field_with_param_with_valid_value(
        self,
    ):

        data = QueryDict("dmc_field=london&dmc_field=leeds")
        form = self.get_form_with_dynamic_multiple_choice_field(data)
        valid_status = form.is_valid()
        self.assertEqual(valid_status, True)
        self.assertEqual(form.errors, {})
        self.assertEqual(form.fields["dmc_field"].value, ["london", "leeds"])
        self.assertEqual(form.fields["dmc_field"].cleaned, ["london", "leeds"])

        # update choices
        self.assertEqual(form.fields["dmc_field"].choices_updated, False)
        choice_api_data = [
            {"value": "london", "doc_count": 10},
            {"value": "leeds", "doc_count": 5},
        ]
        form.fields["dmc_field"].update_choices(
            choice_api_data, form.fields["dmc_field"].value
        )
        self.assertEqual(form.fields["dmc_field"].choices_updated, True)

        self.assertEqual(
            form.fields["dmc_field"].items,
            [
                {
                    "text": "London (10)",
                    "value": "london",
                    "checked": True,
                },
                {
                    "text": "Leeds (5)",
                    "value": "leeds",
                    "checked": True,
                },
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

        # update choices
        self.assertEqual(form.fields["dmc_field"].choices_updated, False)
        choice_api_data = [
            {"value": "london", "doc_count": 10},
            {"value": "leeds", "doc_count": 5},
        ]
        form.fields["dmc_field"].update_choices(
            choice_api_data, form.fields["dmc_field"].value
        )
        self.assertEqual(form.fields["dmc_field"].choices_updated, True)

        self.assertEqual(
            form.fields["dmc_field"].items,
            [
                {
                    "text": "London (10)",
                    "value": "london",
                    "checked": True,
                },
                {
                    "text": "Leeds (5)",
                    "value": "leeds",
                    "checked": True,
                },
            ],
        )
        self.assertEqual(form.fields["dmc_field"].error, {})

    def test_form_with_dynamic_multiple_choice_field_with_multiple_param_error_with_invalid_values(
        self,
    ):

        # partial match: some levels valid, others invalid
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
        # as this is not a view test, before items called, choices not updated
        self.assertEqual(form.fields["dmc_field"].choices_updated, False)
        # invalid choices, so items is empty
        self.assertEqual(form.fields["dmc_field"].items, [])
        # after items called, choices updated
        self.assertEqual(form.fields["dmc_field"].choices_updated, True)
        self.assertEqual(
            form.fields["dmc_field"].error,
            {
                "text": (
                    "Enter a valid choice. Value(s) [london, manchester] do not belong "
                    "to the available choices. Valid choices are [london, leeds]"
                ),
            },
        )


class BaseFormWithDMCFieldValidateInputFalseTest(TestCase):

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
                        validate_input=False,
                    )
                }

        form = MyTestForm(data)
        return form

    def test_form_with_dynamic_multiple_choice_field_initial_attrs(self):

        form = self.get_form_with_dynamic_multiple_choice_field()
        self.assertEqual(form.fields["dmc_field"].name, "dmc_field")
        self.assertEqual(form.fields["dmc_field"].label, "Location")
        self.assertEqual(form.fields["dmc_field"].hint, "")
        self.assertEqual(form.fields["dmc_field"].required, False)
        self.assertEqual(form.fields["dmc_field"].validate_input, False)
        self.assertEqual(form.fields["dmc_field"].active_filter_label, None)
        self.assertEqual(
            form.fields["dmc_field"].choices,
            [("london", "London"), ("leeds", "Leeds")],
        )
        self.assertEqual(
            form.fields["dmc_field"].configured_choices,
            [("london", "London"), ("leeds", "Leeds")],
        )
        self.assertEqual(form.fields["dmc_field"]._cleaned, None)
        self.assertEqual(form.fields["dmc_field"].cleaned, None)
        self.assertEqual(form.fields["dmc_field"].error, {})
        # as this is not a view test, before items called, choices not updated
        self.assertEqual(form.fields["dmc_field"].choices_updated, False)
        self.assertEqual(
            form.fields["dmc_field"].items, []
        )  # should be empty until choices are updated
        # as this is not a view test, after items called, choices are updated
        self.assertEqual(form.fields["dmc_field"].choices_updated, True)

    def test_form_with_dynamic_multiple_choice_field_error_with_no_params(self):

        data = QueryDict("")  # no params
        form = self.get_form_with_dynamic_multiple_choice_field(data)
        valid_status = form.is_valid()
        self.assertEqual(valid_status, True)
        self.assertEqual(form.fields["dmc_field"].value, [])
        self.assertEqual(form.fields["dmc_field"].cleaned, [])

        # update choices
        self.assertEqual(form.fields["dmc_field"].choices_updated, False)
        choice_api_data = [
            {"value": "london", "doc_count": 10},
            {"value": "leeds", "doc_count": 5},
        ]
        form.fields["dmc_field"].update_choices(
            choice_api_data, form.fields["dmc_field"].value
        )
        self.assertEqual(form.fields["dmc_field"].choices_updated, True)

        self.assertEqual(
            form.fields["dmc_field"].items,
            [
                {"text": "London (10)", "value": "london"},
                {"text": "Leeds (5)", "value": "leeds"},
            ],
        )
        self.assertEqual(form.fields["dmc_field"].error, {})

    def test_form_with_dynamic_multiple_choice_field_with_data_found_for_all_params(
        self,
    ):

        data = QueryDict("dmc_field=london&dmc_field=leeds")
        form = self.get_form_with_dynamic_multiple_choice_field(data)
        valid_status = form.is_valid()
        self.assertEqual(valid_status, True)
        self.assertEqual(form.errors, {})
        self.assertEqual(form.fields["dmc_field"].value, ["london", "leeds"])
        self.assertEqual(form.fields["dmc_field"].cleaned, ["london", "leeds"])

        # update choices
        self.assertEqual(form.fields["dmc_field"].choices_updated, False)
        choice_api_data = [
            {"value": "london", "doc_count": 10},
            {"value": "leeds", "doc_count": 5},
        ]
        form.fields["dmc_field"].update_choices(
            choice_api_data, form.fields["dmc_field"].value
        )
        self.assertEqual(form.fields["dmc_field"].choices_updated, True)

        self.assertEqual(
            form.fields["dmc_field"].items,
            [
                {
                    "text": "London (10)",
                    "value": "london",
                    "checked": True,
                },
                {
                    "text": "Leeds (5)",
                    "value": "leeds",
                    "checked": True,
                },
            ],
        )
        self.assertEqual(form.fields["dmc_field"].error, {})

    def test_form_with_dynamic_multiple_choice_field_with_data_found_for_some_params(
        self,
    ):

        data = QueryDict("dmc_field=london&dmc_field=leeds")
        form = self.get_form_with_dynamic_multiple_choice_field(data)
        valid_status = form.is_valid()
        self.assertEqual(valid_status, True)
        self.assertEqual(form.errors, {})
        self.assertEqual(form.fields["dmc_field"].value, ["london", "leeds"])
        self.assertEqual(form.fields["dmc_field"].cleaned, ["london", "leeds"])

        # update choices
        self.assertEqual(form.fields["dmc_field"].choices_updated, False)
        choice_api_data = [
            {"value": "london", "doc_count": 10},
        ]
        form.fields["dmc_field"].update_choices(
            choice_api_data, form.fields["dmc_field"].value
        )
        self.assertEqual(form.fields["dmc_field"].choices_updated, True)

        self.assertEqual(
            form.fields["dmc_field"].items,
            [
                {
                    "text": "London (10)",  # Data found
                    "value": "london",
                    "checked": True,
                },
                {
                    "text": "Leeds (0)",  # Data not found is coerced to 0
                    "value": "leeds",
                    "checked": True,
                },
            ],
        )
        self.assertEqual(form.fields["dmc_field"].error, {})
