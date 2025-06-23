"""Module for basic form which to work with customised fields."""

from typing import Any

from django.http import QueryDict

from .fields import BaseField


class BaseForm:
    """
    Flow
    -----
    1. Create the form with fields and cross_validations
    2. Instanitate and bind the form with request data
    3. Clean and Validate the form via is_valid()
    4. On failure in cross validatiom, field errors assign to form errors
    5. Access form and fields attributes

    Form Attributes
    ---------------
    data         - request querydict data, mix default values here
    errors       - overall error forms and fields
    is_valid()   - to clean and validate form fields
    """

    NON_FIELD_ERRORS_KEY = "NONFIELDERRORS"

    def __init__(self, data: QueryDict | None = None) -> None:

        self.data: QueryDict = data or QueryDict("")
        self._fields = self.add_fields()
        self._errors = {}

        self.bind_fields()

    @property
    def fields(self) -> dict[str, BaseField]:
        return self._fields

    def add_fields(self) -> dict[str, BaseField]:
        """Implement in SubClass. Ex {"<field_name>": <Field>, }."""

        return {}

    def bind_fields(self):
        """Binds fields with data as list as inputs can be driven manually.
        Binding list or string value is handled at the field."""

        for name, field in self.fields.items():
            field.bind(name, self.data.getlist(name))

    def is_valid(self) -> bool:
        """Returns True when fields are cleaned and validated without errors and stores cleaned data.
        When False, adds overall errors for form and field."""

        valid = True

        # clean and validate fields
        for name, field in self.fields.items():
            if not field.is_valid():
                self.add_error(name, message=field.error.get("text"))
                valid = False

        # clean and validate fields at form level
        if crosss_validate_errors := self.cross_validate():
            self.add_error(self.NON_FIELD_ERRORS_KEY, crosss_validate_errors)
            valid = False

        return valid

    def cross_validate(self) -> list[str]:
        """Subclass to validate between fields cleaned values
        returns list of error messages ['error message 1', 'error message 2'].
        """

        return []

    def add_error(self, key, message: str | list = None):
        """Sets field and non field errors
        Field errors: dict[str, dict[str, str]]
                      ex {"<field_name>", {"text: "<error message>"}}
        Non Field errors: dict[str, list[dict[str, str]]]
                          ex {"NONFIELDERRORS", [{"text: "<error message 1>"},
                                                 {"text: "<error message 2>"}]}
        """

        if isinstance(message, list):
            message_format = [{"text": item} for item in message]
        else:
            message_format = {"text": message}

        self._errors[key] = message_format

    @property
    def errors(
        self,
    ) -> dict[str, dict[str, str]] | dict[str, list[dict[str, str]]]:
        return self._errors
