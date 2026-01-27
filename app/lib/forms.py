"""Module for basic form which to work with customised fields."""

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
    data             - request querydict data, mix default values here
    errors           - field errors
    non_field_errors - non field errors
    is_valid()       - to clean and validate form fields
    """

    def __init__(self, data: QueryDict | None = None) -> None:

        self.data: QueryDict = data or QueryDict("")
        self._fields = self.add_fields()
        self._non_field_errors = None

        self.bind_fields()

    @property
    def fields(self) -> dict[str, BaseField]:
        return self._fields

    def add_fields(self) -> dict[str, BaseField]:
        """Implement in SubClass. Ex {"<field_name>": <Field>, }."""

        return {}

    def bind_fields(self):
        """Binds fields with data as list as inputs can be driven manually.
        Binding values are handled at the field."""

        for name, field in self.fields.items():
            value = field.get_bind_value(self.data, name)
            field.bind(name, value)

    def is_valid(self) -> bool:
        """Returns True when fields are cleaned and validated without errors and stores cleaned data.
        When False, adds non field errors"""

        valid = True

        # clean and validate fields
        for field in self.fields.values():
            if not field.is_valid():
                valid = False

        # clean and validate fields at form level
        if cross_validate_errors := self.cross_validate():
            self.add_non_field_error(cross_validate_errors)
            valid = False

        return valid

    def cross_validate(self) -> list[str]:
        """Subclass to validate between fields cleaned values
        returns list of error messages ['error message 1', 'error message 2'].
        """

        return []

    def add_non_field_error(self, message: list):
        """Sets errors defined by key
        Ex:
        Non Field errors: list[dict[str, str]]]
                          ex [{"text: "<error message 1>"},
                              {"text: "<error message 2>"}]
        """
        self._non_field_errors = [{"text": item} for item in message]

    @property
    def errors(
        self,
    ) -> dict[str, dict[str, str]]:
        """Returns field errors."""

        errors = {
            field.name: field.error
            for field in self.fields.values()
            if field.error
        }
        return errors

    @property
    def non_field_errors(self) -> list[dict[str, str]]:
        """Returns non field errors."""

        return self._non_field_errors or []
