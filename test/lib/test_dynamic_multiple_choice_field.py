from app.lib.fields import DynamicMultipleChoiceField
from app.lib.forms import BaseForm
from django.http import QueryDict
from django.test import TestCase


class BaseFormWithDMCFieldValidateInputTrueTest(TestCase):

    def create_form_with_dynamic_multiple_choice_field(
        self, data=None
    ) -> tuple[BaseForm, DynamicMultipleChoiceField]:

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
        dmc_field = form.fields["dmc_field"]
        return form, dmc_field

    def test_form_with_dynamic_multiple_choice_field_initial_attrs(self):

        _, dmc_field = self.create_form_with_dynamic_multiple_choice_field()

        self.assertEqual(dmc_field.id, "id_dmc_field")
        self.assertEqual(dmc_field.name, "dmc_field")
        self.assertEqual(dmc_field.label, "Location")
        self.assertEqual(dmc_field.hint, "")
        self.assertEqual(dmc_field.required, True)
        self.assertEqual(dmc_field.validate_input, True)
        self.assertEqual(dmc_field.active_filter_label, None)
        self.assertEqual(
            dmc_field.choices,
            [("london", "London"), ("leeds", "Leeds")],
        )
        self.assertEqual(
            dmc_field.configured_choices,
            [("london", "London"), ("leeds", "Leeds")],
        )
        self.assertEqual(dmc_field._cleaned, None)
        self.assertEqual(dmc_field.cleaned, None)
        self.assertEqual(dmc_field.error, {})
        # as this is not a view test, before items called, choices not updated
        self.assertEqual(dmc_field.choices_updated, False)
        self.assertEqual(
            dmc_field.items, []
        )  # should be empty until choices are updated
        # as this is not a view test, after items called, choices are updated
        self.assertEqual(dmc_field.choices_updated, True)

    def test_form_with_dynamic_multiple_choice_field_error_with_no_params(self):

        data = QueryDict("")  # no params
        form, dmc_field = self.create_form_with_dynamic_multiple_choice_field(
            data
        )
        valid_status = form.is_valid()
        self.assertEqual(valid_status, False)
        self.assertEqual(
            form.errors, {"dmc_field": {"text": "Value is required."}}
        )
        self.assertEqual(dmc_field.value, [])
        self.assertEqual(dmc_field.cleaned, None)
        # as this is not a view test, before items called, choices not updated
        self.assertEqual(dmc_field.choices_updated, False)
        # required field with no input, so items is empty
        self.assertEqual(dmc_field.items, [])
        # as this is not a view test, after items called, choices are updated
        self.assertEqual(dmc_field.choices_updated, True)
        self.assertEqual(dmc_field.error, {"text": "Value is required."})

    def test_form_with_dynamic_multiple_choice_field_with_param_with_valid_value(
        self,
    ):

        data = QueryDict("dmc_field=london")
        form, dmc_field = self.create_form_with_dynamic_multiple_choice_field(
            data
        )
        valid_status = form.is_valid()
        self.assertEqual(valid_status, True)
        self.assertEqual(form.errors, {})
        self.assertEqual(dmc_field.value, ["london"])
        self.assertEqual(dmc_field.cleaned, ["london"])

        # update choices
        self.assertEqual(dmc_field.choices_updated, False)
        choice_api_data = [
            {"value": "london", "doc_count": 10},
        ]
        dmc_field.update_choices(choice_api_data, dmc_field.value)
        self.assertEqual(dmc_field.choices_updated, True)

        self.assertEqual(
            dmc_field.items,
            [
                {
                    "text": "London (10)",
                    "value": "london",
                    "checked": True,
                },
            ],
        )
        self.assertEqual(dmc_field.error, {})

    def test_form_with_dynamic_multiple_choice_field_with_multiple_param_with_valid_values(
        self,
    ):

        data = QueryDict("dmc_field=london&dmc_field=leeds")
        form, dmc_field = self.create_form_with_dynamic_multiple_choice_field(
            data
        )
        valid_status = form.is_valid()
        self.assertEqual(valid_status, True)
        self.assertEqual(form.errors, {})
        self.assertEqual(dmc_field.id, "id_dmc_field")
        self.assertEqual(dmc_field.name, "dmc_field")
        self.assertEqual(dmc_field.value, ["london", "leeds"])
        self.assertEqual(dmc_field.cleaned, ["london", "leeds"])

        # update choices
        self.assertEqual(dmc_field.choices_updated, False)
        choice_api_data = [
            {"value": "london", "doc_count": 10},
            {"value": "leeds", "doc_count": 5},
        ]
        dmc_field.update_choices(choice_api_data, dmc_field.value)
        self.assertEqual(dmc_field.choices_updated, True)

        self.assertEqual(
            dmc_field.items,
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
        self.assertEqual(dmc_field.error, {})

    def test_form_with_dynamic_multiple_choice_field_with_multiple_param_error_with_invalid_values(
        self,
    ):

        # partial match: some levels valid, others invalid
        data = QueryDict("dmc_field=london&dmc_field=manchester")
        form, dmc_field = self.create_form_with_dynamic_multiple_choice_field(
            data
        )
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
        self.assertEqual(dmc_field.value, ["london", "manchester"])
        # as this is not a view test, before items called, choices not updated
        self.assertEqual(dmc_field.choices_updated, False)
        # invalid choices, so items is empty
        self.assertEqual(dmc_field.items, [])
        # after items called, choices updated
        self.assertEqual(dmc_field.choices_updated, True)
        self.assertEqual(
            dmc_field.error,
            {
                "text": (
                    "Enter a valid choice. Value(s) [london, manchester] do not belong "
                    "to the available choices. Valid choices are [london, leeds]"
                ),
            },
        )


class BaseFormWithDMCFieldValidateInputFalseTest(TestCase):

    def create_form_with_dynamic_multiple_choice_field(
        self, data=None
    ) -> tuple[BaseForm, DynamicMultipleChoiceField]:

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
        dmc_field = form.fields["dmc_field"]
        return form, dmc_field

    def test_form_with_dynamic_multiple_choice_field_initial_attrs(self):

        _, dmc_field = self.create_form_with_dynamic_multiple_choice_field()

        self.assertEqual(dmc_field.id, "id_dmc_field")
        self.assertEqual(dmc_field.name, "dmc_field")
        self.assertEqual(dmc_field.label, "Location")
        self.assertEqual(dmc_field.hint, "")
        self.assertEqual(dmc_field.required, False)
        self.assertEqual(dmc_field.validate_input, False)
        self.assertEqual(dmc_field.active_filter_label, None)
        self.assertEqual(
            dmc_field.choices,
            [("london", "London"), ("leeds", "Leeds")],
        )
        self.assertEqual(
            dmc_field.configured_choices,
            [("london", "London"), ("leeds", "Leeds")],
        )
        self.assertEqual(dmc_field._cleaned, None)
        self.assertEqual(dmc_field.cleaned, None)
        self.assertEqual(dmc_field.error, {})
        # as this is not a view test, before items called, choices not updated
        self.assertEqual(dmc_field.choices_updated, False)
        self.assertEqual(
            dmc_field.items, []
        )  # should be empty until choices are updated
        # as this is not a view test, after items called, choices are updated
        self.assertEqual(dmc_field.choices_updated, True)

        self.assertEqual(dmc_field.more_filter_choices_available, False)
        self.assertEqual(dmc_field.more_filter_choices_url, "")
        self.assertEqual(dmc_field.more_filter_choices_text, "See more options")

    def test_form_with_dynamic_multiple_choice_field_with_no_params(self):

        data = QueryDict("")  # no params
        form, dmc_field = self.create_form_with_dynamic_multiple_choice_field(
            data
        )
        valid_status = form.is_valid()
        self.assertEqual(valid_status, True)
        self.assertEqual(dmc_field.value, [])
        self.assertEqual(dmc_field.cleaned, [])

        # update choices
        self.assertEqual(dmc_field.choices_updated, False)
        choice_api_data = [
            {"value": "london", "doc_count": 10},
            {"value": "leeds", "doc_count": 5},
        ]
        dmc_field.update_choices(choice_api_data, dmc_field.value)
        self.assertEqual(dmc_field.choices_updated, True)

        self.assertEqual(
            dmc_field.items,
            [
                {"text": "London (10)", "value": "london"},
                {"text": "Leeds (5)", "value": "leeds"},
            ],
        )
        self.assertEqual(dmc_field.error, {})

    def test_form_with_dynamic_multiple_choice_field_with_data_found_for_all_params(
        self,
    ):

        data = QueryDict("dmc_field=london&dmc_field=leeds")
        form, dmc_field = self.create_form_with_dynamic_multiple_choice_field(
            data
        )
        valid_status = form.is_valid()
        self.assertEqual(valid_status, True)
        self.assertEqual(form.errors, {})
        self.assertEqual(dmc_field.value, ["london", "leeds"])
        self.assertEqual(dmc_field.cleaned, ["london", "leeds"])

        # update choices
        self.assertEqual(dmc_field.choices_updated, False)
        choice_api_data = [
            {"value": "london", "doc_count": 10},
            {"value": "leeds", "doc_count": 5},
        ]
        dmc_field.update_choices(choice_api_data, dmc_field.value)
        self.assertEqual(dmc_field.choices_updated, True)

        self.assertEqual(
            dmc_field.items,
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
        self.assertEqual(dmc_field.error, {})

    def test_form_with_dynamic_multiple_choice_field_with_data_found_for_some_params(
        self,
    ):

        data = QueryDict("dmc_field=london&dmc_field=leeds")
        form, dmc_field = self.create_form_with_dynamic_multiple_choice_field(
            data
        )
        valid_status = form.is_valid()
        self.assertEqual(valid_status, True)
        self.assertEqual(form.errors, {})
        self.assertEqual(dmc_field.value, ["london", "leeds"])
        self.assertEqual(dmc_field.cleaned, ["london", "leeds"])

        # update choices
        self.assertEqual(dmc_field.choices_updated, False)
        choice_api_data = [
            {"value": "london", "doc_count": 10},
        ]
        dmc_field.update_choices(choice_api_data, dmc_field.value)
        self.assertEqual(dmc_field.choices_updated, True)

        self.assertEqual(
            dmc_field.items,
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
        self.assertEqual(dmc_field.error, {})
