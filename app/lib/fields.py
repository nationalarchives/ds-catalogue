"""Module for custom fields which interfaces with FE component attrs."""

from datetime import date
from typing import Optional
from calendar import monthrange
from django.utils.functional import cached_property

class ValidationError(Exception):
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

    def __init__(self, label=None, required=False, hint=""):
        self.label = label
        self.required = required
        self.hint = hint
        self._value = None  # usually the request data
        self._cleaned = None
        self._error = {}
        self.choices = None  # applicable to certain fields ex choice

    def bind(self, name, value: list | str) -> None:
        """Binds field name, value to the field. The value is usually from
        user input. Binding happens through the form on initialisation.
        Override to bind to list or string."""

        self.name = name
        self.label = self.label or name.capitalize()
        self._value = value

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
        """choices: format [(field value, display value),]. Has field specific attributes."""

        # field specific attr, validate input choices before querying the api
        self.validate_input = bool(choices) and kwargs.pop(
            "validate_input", True
        )
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
                    raise ValidationError(
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
        """
        Args:
            is_from_date: If True, partial dates default to start of period.
                         If False, partial dates default to end of period.
        """
        super().__init__(**kwargs)
        self.day = None
        self.month = None 
        self.year = None
        self.is_from_date = is_from_date
        
    def bind(self, name, value: list | str) -> None:
        """Binds the field with component values from request data"""
        # Call parent bind with empty string to satisfy parent class
        super().bind(name, '')
        
        # Determine if this is a from or to date based on field name
        if name:
            self.is_from_date = 'from' in name.lower()
        
        # The data comes from request.GET as separate fields
        # We need to extract from the parent form's data
        if hasattr(self, '_form_data'):
            self.day = self._form_data.get(f'{name}-day', '')
            self.month = self._form_data.get(f'{name}-month', '')
            self.year = self._form_data.get(f'{name}-year', '')
    
    def set_form_data(self, form_data):
        """Set reference to form data for accessing component fields"""
        self._form_data = form_data
        # Re-extract components after form data is set
        if self.name:
            self.day = form_data.get(f'{self.name}-day', '')
            self.month = form_data.get(f'{self.name}-month', '')
            self.year = form_data.get(f'{self.name}-year', '')
    
    def is_valid(self):
        """Override to handle DateComponentField validation properly"""
        
        try:
            # For DateComponentField, we don't use self.value in clean
            # We use the component values directly
            self._cleaned = self.clean(None)
        except ValidationError as e:
            self.add_error(str(e))
        except Exception as e:
            self.add_error("An error occurred validating the date")

        result = not bool(self._error)
        return result
    
    def clean(self, value):
        """Convert components to date object or None, handling partial dates"""
        
        # If no components provided, return None (field is optional)
        if not any([self.day, self.month, self.year]):
            return None
        
        # Must have at least a year
        if not self.year:
            raise ValidationError("Year is required if any date component is provided")
        
        try:
            year = int(self.year)
            
            # Validate year range
            if year < 1000 or year > 9999:
                raise ValidationError("Please enter a valid 4-digit year")
            
            # Keep year as string for consistency
            self.year = str(year)
            
            # Handle year-only input
            if not self.month and not self.day:
                if self.is_from_date:
                    # Start of year: January 1st
                    self.month = '1'
                    self.day = '1'
                    return date(year, 1, 1)
                else:
                    # End of year: December 31st
                    self.month = '12'
                    self.day = '31'
                    return date(year, 12, 31)
            
            # Handle year and month input (no day)
            if self.month and not self.day:
                month = int(self.month)
                
                # Validate month
                if not (1 <= month <= 12):
                    raise ValidationError("Month must be between 1 and 12")
                
                # Keep month as string
                self.month = str(month)
                
                if self.is_from_date:
                    # Start of month: 1st day
                    self.day = '1'
                    return date(year, month, 1)
                else:
                    # End of month: last day (28/29/30/31 depending on month)
                    last_day = monthrange(year, month)[1]
                    self.day = str(last_day)
                    return date(year, month, last_day)
            
            # Handle complete date (all components provided)
            if self.day:
                if not self.month:
                    raise ValidationError("Month is required if day is provided")
                
                day = int(self.day)
                month = int(self.month)
                
                # Basic range validation
                if not (1 <= month <= 12):
                    raise ValidationError("Month must be between 1 and 12")
                if not (1 <= day <= 31):
                    raise ValidationError("Day must be between 1 and 31")
                
                # Keep as strings for consistency
                self.day = str(day)
                self.month = str(month)
                
                # Create date object (this validates the actual date)
                return date(year, month, day)
            
        except ValueError as e:
            if "day is out of range for month" in str(e):
                raise ValidationError("Invalid day for the given month")
            elif "month must be" in str(e):
                raise ValidationError("Month must be between 1 and 12")
            else:
                raise ValidationError("Please enter a valid date")
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError("Please enter a valid date")
    
    @property
    def value(self):
        """Return the component values as a dict for template access"""
        return {
            'day': self.day or '',
            'month': self.month or '',
            'year': self.year or ''
        }
    
    def get_computed_components(self) -> dict:
        """Get the computed component values after cleaning"""
        # Make sure we return the current values (which may have been computed)
        result = {
            f'{self.name}-day': str(self.day) if self.day else '',
            f'{self.name}-month': str(self.month) if self.month else '',
            f'{self.name}-year': str(self.year) if self.year else ''
        }
        return result
    
    def format_for_api(self) -> Optional[str]:
        """Format the cleaned date as YYYY-MM-DD for API"""
        if self.cleaned:
            return self.cleaned.strftime('%Y-%m-%d')
        return None