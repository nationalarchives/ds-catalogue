"""Module for custom fields which interfaces with FE component attrs."""

from calendar import monthrange
from datetime import date

from django.utils.functional import cached_property


class CustomValidationError(Exception):
    pass


class BaseField:
    """
    Flow
    -----
    1. Instantiate the field
    2. Bind the request value
    3. Clean and Validate the value. Assign clean value.
    4. Assign error on failure
    5. Access field attributes
    """

    def __init__(
        self, label=None, required=False, hint="", active_filter_label=None
    ):
        self.label = label
        self.required = required
        self.hint = hint
        self._value = None  # usually the request data
        self._cleaned = None
        self._error = {}
        self.choices = None  # applicable to certain fields ex choice
        self.active_filter_label = active_filter_label

    def bind(self, name, value: list | str) -> None:
        """Binds field name, value to the field. The value is usually from
        user input. Binding happens through the form on initialisation.
        Override to bind to list or string."""

        self.name = name
        self.label = self.label or name.capitalize()
        self._value = value

    def is_valid(self):
        """Runs cleaning and validation. Handles CustomValidationError.
        Stores cleaned value. Returns True if valid, False otherwise"""

        try:
            self._cleaned = self.clean(self.value)
        except CustomValidationError as e:
            self.add_error(str(e))

        return not self._error

    def clean(self, value):
        """Subclass for cleaning and validating. Ex strip str, convert to date object"""

        self.validate(value)
        return value

    def validate(self, value):
        """Basic validation. For more validation, Subclass and raise CustomValidationError"""

        if self.required and not value:
            raise CustomValidationError("Value is required.")

    def add_error(self, message):
        """Stores error message in the format of FE component"""

        self._error = {"text": message}

    @property
    def error(self) -> dict[str, str]:
        return self._error

    @property
    def cleaned(self):
        return self._cleaned if not self._error else None

    @property
    def value(self):
        return self._value

    @property
    def update_choices(self):
        """Implement for multiple choice field."""

        raise NotImplementedError

    @property
    def items(self):
        """Return as required by FE.
        Ex Checkboxes [{"text": "Alpha","value": "alpha"},{"text": "Beta","value": "beta","checked": true}]
        """

        raise NotImplementedError


class CharField(BaseField):

    def bind(self, name, value: list | str) -> None:
        """Binds a empty string or last value from input."""

        if not value:
            value = [""]
        # get last value (for more than one input value)
        value = value[-1]
        super().bind(name, value)

    def clean(self, value):
        value = super().clean(value)
        return str(value).strip() if value else ""


class ChoiceField(BaseField):

    def __init__(self, choices: list[tuple[str, str]], **kwargs):
        """choices: format [(field value, display value),]."""

        super().__init__(**kwargs)
        self.choices = choices

    def _has_match(self, value, search_in):
        return value in search_in

    def bind(self, name, value: list | str) -> None:
        """Binds a empty string or last value from input."""

        if not value:
            value = [""]
        # get last value (for more than one input value)
        value = value[-1]
        super().bind(name, value)

    def validate(self, value):
        if self.required:
            super().validate(value)

        valid_choices = [value for value, _ in self.choices]
        if not self._has_match(value, valid_choices):
            raise CustomValidationError(
                (
                    f"Enter a valid choice. [{value or 'Empty param value'}] is not one of the available choices. "
                    f"Valid choices are [{', '.join(valid_choices)}]"
                )
            )

    @property
    def items(self):
        return [
            (
                {"text": display_value, "value": value, "checked": True}
                if (value == self.value)
                else {"text": display_value, "value": value}
            )
            for value, display_value in self.choices
        ]


class DynamicMultipleChoiceField(BaseField):

    def __init__(self, choices: list[tuple[str, str]], **kwargs):
        """
        choices: data format - [(field value, display value),]
        defined choices act to validate input against and lookup
        display labels for dynamic values, otherwise an empty list when
        there are no fixed choices to validate against or need to
        lookup labels.

        keyword args - validate_input: bool
        validate_input is optional, it defaults True if choices provided,
        False otherwise. Override to False when validation from defined
        choices is required. Coerce to False when no choices provided.

        Choices are updated dynamically using update_choices() method.
        """

        # field specific attr, validate input choices before querying the api
        validate_default = True if choices else False
        if choices:
            self.validate_input = kwargs.pop("validate_input", validate_default)
        else:
            # coerce to False when no choices provided
            self.validate_input = False
            kwargs.pop("validate_input", None)

        super().__init__(**kwargs)
        self.choices = choices
        self.configured_choices = self.choices
        # cache valid choices
        if self.validate_input:
            self.valid_choices = [value for value, _ in self.choices]
        else:
            self.valid_choices = []

        # The self.choices_updated is used to at the time of render
        # to coerce 0 counts on error or when choices
        # have been updated to reflect options from the API.
        self.choices_updated = False

    def _has_match_all(self, value, search_in):
        return all(item in search_in for item in value)

    def validate(self, value):
        if self.required or self.validate_input:
            super().validate(value)
            if self.validate_input:
                if not self._has_match_all(value, self.valid_choices):
                    raise CustomValidationError(
                        (
                            f"Enter a valid choice. Value(s) [{', '.join(value)}] do not belong "
                            f"to the available choices. Valid choices are [{', '.join(self.valid_choices)}]"
                        )
                    )

    @property
    def items(self):
        if self.error:
            # applied filter did not return results,
            # so coerce api data to 0 counts for selected values
            zero_count_data = []
            partial_match = False
            if not self._has_match_all(self.value, self.valid_choices):
                for input_value in self.value:
                    if input_value in self.valid_choices:
                        partial_match = True
                        zero_count_data.append(
                            {"value": input_value, "doc_count": 0}
                        )
            if not partial_match:
                for value in self.valid_choices:
                    zero_count_data.append({"value": value, "doc_count": 0})

            if zero_count_data:
                self.update_choices(zero_count_data, self.value)

        return [
            (
                {"text": display_value, "value": value, "checked": True}
                if (value in self.value)
                else {"text": display_value, "value": value}
            )
            for value, display_value in self.choices
        ]

    @cached_property
    def configured_choice_labels(self):
        return {value: label for value, label in self.configured_choices}

    def choice_label_from_api_data(self, data: dict[str, str | int]) -> str:
        count = f"{data['doc_count']:,}"
        try:
            # Use a label from the configured choice values, if available
            return f"{self.configured_choice_labels[data['value']]} ({count})"
        except KeyError:
            # Fall back to using the key value (which is the same in most cases)
            return f"{data['value']} ({count})"

    def update_choices(
        self,
        choice_api_data: list[dict[str, str | int]],
        selected_values,
    ):
        """
        Updates this fields `choices` list using aggregation data from the most recent
        API result. If `selected_values` is provided, options with values matching items
        in that list will be preserved in the new `choices` list, even if they are not
        present in `choice_data`.

        Expected `choice_api_data` format:
        [
            {
                "value": "Item",
                "doc_count": 10
            },
            …
        ]
        """

        # Generate a new list of choices
        choices = []
        choice_vals_with_hits = set()
        for item in choice_api_data:
            choices.append(
                (item["value"], self.choice_label_from_api_data(item))
            )
            choice_vals_with_hits.add(item["value"])

        if self.validate_input:
            check_values_from = [
                v
                for v in selected_values
                if v not in choice_vals_with_hits and v in self.valid_choices
            ]
        else:
            check_values_from = [
                v for v in selected_values if v not in choice_vals_with_hits
            ]

        for missing_value in check_values_from:
            try:
                label_base = self.configured_choice_labels[missing_value]
            except KeyError:
                label_base = missing_value
            choices.append((missing_value, f"{label_base} (0)"))

        # Replace the field's attribute value
        self.choices = choices
        self.choices_updated = True


class DateComponentField(BaseField):
    """Handles day/month/year components and validates them as a complete date"""

    def __init__(self, is_from_date=True, **kwargs):
        super().__init__(**kwargs)
        self.day = ""
        self.month = ""
        self.year = ""
        self.is_from_date = is_from_date
        self._form_data = None
        self._components_extracted = False

    def bind(self, name, value: list | str) -> None:
        super().bind(name, "")
        # Don't auto-detect is_from_date from field name in tests
        # Let the constructor value take precedence

    def set_form_data(self, form_data):
        """Set form data and extract components immediately"""
        self._form_data = form_data
        if self.name and form_data:
            self._extract_components(form_data, self.name)

    def _extract_components(self, form_data, name):
        """Extract day, month, year components from form data"""
        if form_data:
            self.day = str(form_data.get(f"{name}-day", "")).strip()
            self.month = str(form_data.get(f"{name}-month", "")).strip()
            self.year = str(form_data.get(f"{name}-year", "")).strip()
            self._components_extracted = True

    def is_valid(self):
        """Validate the date components and create cleaned date object"""
        # If we haven't extracted components yet and we have form data, do it now
        if not self._components_extracted and self._form_data and self.name:
            self._extract_components(self._form_data, self.name)

        try:
            self._cleaned = self.clean(None)
        except CustomValidationError as e:
            self.add_error(str(e))
        except Exception as e:
            self.add_error(f"Invalid date: {str(e)}")

        return not bool(self._error)

    def clean(self, value):
        """Convert components to date object or None, handling partial dates"""
        # If no components are provided, return None (empty date)
        if not any([self.day, self.month, self.year]):
            return None

        # Validate and get the year first
        year = self._validate_year()

        # Handle year-only input
        if not self.month and not self.day:
            return self._fill_year_only(year)

        # Handle year-month input (no day)
        if self.month and not self.day:
            return self._fill_year_month_only(year)

        # Handle full date input
        if self.day:
            return self._fill_full_date(year)

        raise CustomValidationError("Please enter a valid date")

    def _validate_year(self):
        """Validate and return the year as an integer"""
        if not self.year:
            raise CustomValidationError(
                "Year is required if any date component is provided"
            )

        try:
            year = int(self.year)
        except ValueError:
            raise CustomValidationError("Please enter a valid 4-digit year")

        if not (1000 <= year <= 9999):
            raise CustomValidationError("Please enter a valid 4-digit year")

        return year

    def _validate_month(self, month):
        """Validate month is between 1 and 12"""
        if not (1 <= month <= 12):
            raise CustomValidationError("Month must be between 1 and 12")

    def _validate_day(self, day):
        """Validate day is between 1 and 31"""
        if not (1 <= day <= 31):
            raise CustomValidationError("Day must be between 1 and 31")

    def _fill_year_only(self, year):
        """Fill in month and day for year-only dates"""
        if self.is_from_date:
            return date(year, 1, 1)  # January 1st
        else:
            return date(year, 12, 31)  # December 31st

    def _fill_year_month_only(self, year):
        """Fill in day for year-month dates"""
        try:
            month = int(self.month)
        except ValueError:
            raise CustomValidationError(
                "Month must be a number between 1 and 12"
            )

        self._validate_month(month)

        if self.is_from_date:
            return date(year, month, 1)  # First day of month
        else:
            last_day = monthrange(year, month)[1]
            return date(year, month, last_day)  # Last day of month

    def _fill_full_date(self, year):
        """Create date from full year-month-day input"""
        if not self.month:
            raise CustomValidationError("Month is required if day is provided")

        try:
            day = int(self.day)
            month = int(self.month)
        except ValueError:
            raise CustomValidationError("Day and month must be numbers")

        self._validate_month(month)
        self._validate_day(day)

        try:
            return date(year, month, day)
        except ValueError:
            raise CustomValidationError(
                "Invalid date - please check the day is valid for the given month"
            )

    @property
    def value(self):
        """Return the current component values"""
        return {
            "day": self.day,
            "month": self.month,
            "year": self.year,
        }

    def get_computed_components(self) -> dict:
        """Return components in the format expected by templates"""
        return {
            f"{self.name}-day": self.day,
            f"{self.name}-month": self.month,
            f"{self.name}-year": self.year,
        }

    def format_for_api(self) -> str | None:
        """Format the cleaned date for API consumption"""
        if self.cleaned:
            return self.cleaned.strftime("%Y-%m-%d")
        return None
