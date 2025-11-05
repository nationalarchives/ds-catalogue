"""Module for custom fields which interfaces with FE component attrs."""

import calendar
from datetime import date
from enum import StrEnum

from django.http import QueryDict
from django.utils.functional import cached_property


class ValidationError(Exception):
    pass


class DateKeys(StrEnum):
    """Date keys for multi part date fields used both BE and FE.
    They appear in the input name as suffixes in the FE component.
    Ex for field name 'start_date', the input keys are
    The separator is defined in the field as date_ymd_separator.
    'start_date-year', 'start_date-month', 'start_date-day'."""

    YEAR = "year"
    MONTH = "month"
    DAY = "day"


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
        self.id = None  # set on bind
        self.label = label
        self.required = required
        self.hint = hint
        self._value = None  # usually the request data
        self._cleaned = None
        self._error = {}
        self.choices = None  # applicable to certain fields ex choice
        self.active_filter_label = active_filter_label

    def bind(self, name, value: list | str | QueryDict | dict) -> None:
        """Binds field name, value to the field. The value is usually from
        user input. Binding happens through the form on initialisation.
        Override to bind to list or string."""

        self.name = name
        self._value = value
        # also bind id and label
        self.id = "id_" + name
        self.label = self.label or name.capitalize()

    def get_bind_value(self, data: QueryDict, name: str):
        """Override in subclasses if special bind value extraction is needed."""
        return data.getlist(name)

    def is_valid(self):
        """Runs cleaning and validation. Handles ValidationError.
        Stores cleaned value. Returns True if valid, False otherwise"""

        try:
            self._cleaned = self.clean(self.value)
        except ValidationError as e:
            self.add_error(str(e))

        return not self._error

    def clean(self, value):
        """Subclass for cleaning and validating. Ex strip str, convert to date object"""

        self.validate(value)
        return value

    def validate(self, value):
        """Basic validation. For more validation, Subclass and raise ValidationError"""

        if self.required and not value:
            raise ValidationError("Value is required.")

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
            raise ValidationError(
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

        keyword args - validate_input: bool,
                       more_filter_choices_text: str
        validate_input: is optional, it defaults True if choices provided,
        False otherwise. Override to False when validation from defined
        choices is required. Coerce to False when no choices provided.
        more_filter_choices_text: text for more choices link/button.
        if not provided, a defined default is used. Override to empty string
        in form when no more choices are available.

        set by form - when more choices are available:
            more_filter_choices_available: default False. Indicates if more
            choices are available from the API.
            more_filter_choices_url: When more choices are available, this url
            is used for the more choices link/button. Default "".

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

        self.more_filter_choices_text: str = kwargs.pop(
            "more_filter_choices_text", "See more options"
        )  # default text
        self.more_filter_choices_available: bool = False  # set by form
        self.more_filter_choices_url: str = ""  # set by form

        super().__init__(**kwargs)

        # TODO: FILTER_CHOICES_LIMIT: discuss limit with team
        # The API response limit for aggs is 10,
        # we don't allow more than that for filtering.
        # Also, this keeps the URL length manageable.
        # self.FILTER_CHOICES_LIMIT = 5

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
                    raise ValidationError(
                        (
                            f"Enter a valid choice. Value(s) [{', '.join(value)}] do not belong "
                            f"to the available choices. Valid choices are [{', '.join(self.valid_choices)}]"
                        )
                    )

        # TODO: FILTER_CHOICES_LIMIT: discuss limit with team
        # if (
        #     self.FILTER_CHOICES_LIMIT > 0
        #     and len(value) > self.FILTER_CHOICES_LIMIT
        # ):
        #     raise ValidationError(
        #         f"Maximum filter choices exceeded. Must be {self.FILTER_CHOICES_LIMIT} or fewer."
        #     )

    @property
    def items(self):
        if self.error:
            if self.configured_choices:
                # remove choices that have been updated
                # with configured choices by coercing with empty data
                self.update_choices([], [])
        else:
            # check choices not updated i.e. api did not return any choice data
            if not self.choices_updated:
                # remove choices that have been updated
                # with configured choices by coercing with empty data
                # and coerce 0 counts for input not in api data
                self.update_choices([], self.value)
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

        for missing_value in [
            v for v in selected_values if v not in choice_vals_with_hits
        ]:
            try:
                label_base = self.configured_choice_labels[missing_value]
            except KeyError:
                label_base = missing_value
            choices.append((missing_value, f"{label_base} (0)"))

        # Replace the field's attribute value
        self.choices = choices
        self.choices_updated = True


class MultiPartDateField(BaseField):
    """A field for handling date input split into multiple parts (day, month, year).
    The input is expected to be QueryDict of date parts.
    The field handles progressive and non-progressive date entry.
    Non-progressive date entry requires all parts to be entered or none.

    Note: progressive data passes with all parts and progressive=True
    """

    def __init__(
        self, progressive: bool = True, date_ymd_separator: str = "-", **kwargs
    ):
        """
        This field is used for both progressive and non-progressive date entry.

        progressive: if True, allows progressive date entry starting from year,
        then month, then day. If False, requires all parts (day, month, year)
        to be entered or none.
        date_ymd_separator: separator between field name and date part key.
        FE component uses this value as separator for ymd date entry.
        Ex for field name 'start_date' and separator '-', the input keys are
        'start_date-year', 'start_date-month', 'start_date-day'.

        progressive, date_ymd_separator - are field specific attributes used
        to configure the field behaviour and interface with the FE component.
        """

        self.progressive = progressive
        self.date_ymd_separator = date_ymd_separator
        self.date_keys = [
            DateKeys.YEAR.value,
            DateKeys.MONTH.value,
            DateKeys.DAY.value,
        ]
        super().__init__(**kwargs)

    def bind(self, name, value: QueryDict) -> None:
        """Extracts values from QueryDict and binds to a dict."""

        # bind value will either be empty dict or a dict with parts
        bind_value = {}

        for key in self.date_keys:
            input_value = value.get(f"{name}{self.date_ymd_separator}{key}", "")
            bind_value[key] = input_value

        super().bind(name, bind_value)

    def get_bind_value(self, data: QueryDict, name: str):
        """MultiPartDateField needs the entire QueryDict to extract date parts."""
        return data

    def clean(self, value: dict[str, str]) -> dict[str, str] | date | None:
        """Cleans and validates dict value. returns dict for calling function
        to handle partial date."""

        value = super().clean(value)

        # after validation, convert to date object
        year, month, day = (
            value.get(date_key, "") for date_key in self.date_keys
        )
        if year and month and day:
            # return for either progressive or full date
            return date(int(year), int(month), int(day))

        # partial date or no date entered
        if self.progressive:
            # return to calling function to handle partial date
            return value

        # not progressive, no full date entered, cleaned is None
        return None

    def validate(self, value: dict):
        """Overrides validate because of multi parts.
        value must be a dict with keys day, month, year."""

        # first validate required field
        self._validate_required(value)

        # validate complete date for non-progressive entry
        if not self.progressive and not self._is_complete_date(value):
            raise ValidationError(
                "Either all or none of the date parts (day, month, year) must be provided."
            )

        # validate date parts if any part entered
        year_int = self._validate_year_only(DateKeys.YEAR.value, value)
        month_int = self._validate_month_only(DateKeys.MONTH.value, value)
        day_int = self._validate_day_only(DateKeys.DAY.value, value)
        if year_int and month_int and day_int:
            self._validate_full_date(year_int, month_int, day_int)

    def _validate_required(self, value):
        """Validates required field."""

        year, _, _ = (value.get(date_key, "") for date_key in self.date_keys)

        # basic validation for required field
        if self.required:
            if self.progressive:
                if not year:
                    raise ValidationError("Year value is required.")
            else:
                if any(v == "" for v in value.values()):
                    raise ValidationError(
                        "All date parts (day, month, year) are required."
                    )

    def _validate_int(self, key, value) -> int:
        """Validates integer input for progressive date field."""

        input_value = value.get(key, "")
        try:
            int_value = int(input_value)
        except ValueError:
            raise ValidationError(f"{key.capitalize()} must be an integer.")
        return int_value

    def _validate_year_only(self, key, value) -> int | None:
        """Validates year input."""

        year = value.get(key, "")
        year_int = None
        if year:
            year_int = self._validate_int(key, value)
            if not (1 <= year_int <= 9999):
                raise ValidationError(
                    f"{key.capitalize()} must be between 1 and 9999."
                )
        return year_int

    def _validate_month_only(self, key, value) -> int | None:
        """Validates month input."""

        month = value.get(key, "")
        month_int = None
        if month:
            month_int = self._validate_int(key, value)
            if not (1 <= month_int <= 12):
                raise ValidationError(
                    f"{key.capitalize()} must be between 1 and 12."
                )
        return month_int

    def _validate_day_only(self, key, value) -> int | None:
        """Validates day input."""

        day = value.get(key, "")
        day_int = None
        if day:
            day_int = self._validate_int(key, value)
            if not (1 <= day_int <= 31):
                raise ValidationError(
                    f"{key.capitalize()} must be between 1 and 31."
                )
        return day_int

    def _validate_full_date(self, year: int, month: int, day: int):
        """Validates full date input."""

        try:
            _ = date(year, month, day)
        except ValueError:
            raise ValidationError(
                "Entered date must be a real date, for example Year 2017, Month 9, Day 23"
            )

    def _is_complete_date(self, value):
        """Checks if all or none of the date parts are filled."""

        filled = [bool(value.get(key)) for key in self.date_keys]
        return all(filled) or not any(filled)


class BaseProgressiveDateField(MultiPartDateField):

    def clean(self, value: dict | date | None) -> date | None:

        # clean and validate partial input from super method
        value = super().clean(value)

        if value and isinstance(value, dict):
            # fill in missing parts progressively to form a valid date

            if year := value.get("year"):
                return self._create_date_from_parts(
                    year=year, month=value.get("month"), day=value.get("day")
                )
            else:
                # year not entered, cannot progress
                return None

        return value

    def _create_date_from_parts(
        self, year: str, month: str, day: str
    ) -> dict[str, str]:
        """Subclass to fill in missing parts progressively to form a valid date."""
        raise NotImplementedError


class FromDateField(BaseProgressiveDateField):
    """Progressive date entry starting from year, then month, then day.
    Missing parts are filled in progressively to form a valid date.
    Ex year only 2023 -> 2023-01-01
    Ex year and month 2023-02 -> 2023-02-01
    Note: Field name should be suffixed with '_from'
    """

    def _create_date_from_parts(self, year: str, month: str, day: str) -> date:
        """Fill in missing parts progressively to form a valid date."""
        if not month:
            month = "01"
        if not day:
            day = "01"
        return date(int(year), int(month), int(day))


class ToDateField(BaseProgressiveDateField):
    """Progressive date entry starting from year, then month, then day.
    Missing parts are filled in progressively to form a valid date.
    Ex year only 2023 -> 2023-12-31
    Ex year and month 2023-02 -> 2023-02-28/29
    Note: field name should be suffixed with '_to'"""

    def _create_date_from_parts(self, year: str, month: str, day: str) -> date:
        """Fill in missing parts progressively to form a valid date."""
        if month:
            day = str(calendar.monthrange(int(year), int(month))[1])
        else:
            month = "12"
            day = "31"
        return date(int(year), int(month), int(day))
