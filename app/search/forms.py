from app.lib.fields import DateComponentField  # Make sure this is imported
from app.lib.fields import (
    CharField,
    ChoiceField,
    DynamicMultipleChoiceField,
)
from app.lib.forms import BaseForm
from app.records.constants import TNA_LEVELS
from app.search.buckets import CATALOGUE_BUCKETS
from app.search.constants import Sort


class FieldsConstant:
    Q = "q"
    SORT = "sort"
    LEVEL = "level"
    GROUP = "group"
    # Using shorter but clear names
    RECORD_DATE_FROM = "rd_from"
    RECORD_DATE_TO = "rd_to"
    OPENING_DATE_FROM = "od_from"
    OPENING_DATE_TO = "od_to"


class CatalogueSearchForm(BaseForm):

    def __init__(self, data=None):
        super().__init__(data)
        # Pass form data to date fields so they can access components
        for field_name, field in self.fields.items():
            if isinstance(field, DateComponentField):
                field.set_form_data(self.data)

    def add_fields(self):
        return {
            FieldsConstant.GROUP: ChoiceField(
                choices=CATALOGUE_BUCKETS.as_choices(),
            ),
            FieldsConstant.SORT: ChoiceField(
                choices=[
                    (Sort.RELEVANCE.value, "Relevance"),
                    (Sort.DATE_DESC.value, "Date (newest first)"),
                    (Sort.DATE_ASC.value, "Date (oldest first)"),
                    (Sort.TITLE_ASC.value, "Title (A–Z)"),
                    (Sort.TITLE_DESC.value, "Title (Z–A)"),
                ],
            ),
            FieldsConstant.Q: CharField(),
            FieldsConstant.LEVEL: DynamicMultipleChoiceField(
                label="Filter by levels",
                choices=list((level, level) for level in TNA_LEVELS.values()),
                validate_input=True,
            ),
            # Document date range
            FieldsConstant.RECORD_DATE_FROM: DateComponentField(
                label="Document date from",
                required=False,
                is_from_date=True,  # Defaults to start of period for partial dates
            ),
            FieldsConstant.RECORD_DATE_TO: DateComponentField(
                label="Document date to",
                required=False,
                is_from_date=False,  # Defaults to end of period for partial dates
            ),
            # Opening date range
            FieldsConstant.OPENING_DATE_FROM: DateComponentField(
                label="Opening date from",
                required=False,
                is_from_date=True,  # Defaults to start of period for partial dates
            ),
            FieldsConstant.OPENING_DATE_TO: DateComponentField(
                label="Opening date to",
                required=False,
                is_from_date=False,  # Defaults to end of period for partial dates
            ),
        }

    def get_cleaned_query_dict(self):
        """Get a QueryDict with computed date values filled in"""
        from django.http import QueryDict

        # Create a mutable copy of the original data
        cleaned_data = QueryDict(mutable=True)

        # Collect all date field computed values first
        date_components_to_add = {}
        date_components_to_skip = set()

        for field_name, field in self.fields.items():
            if isinstance(field, DateComponentField):
                # Make sure the field has been validated and has a cleaned value
                if hasattr(field, "_cleaned") and field._cleaned is not None:
                    # The field has been cleaned and has computed values
                    computed = field.get_computed_components()
                    date_components_to_add.update(computed)
                    # Track which keys we're replacing
                    for key in computed.keys():
                        date_components_to_skip.add(key)

        # Add all non-date-component data from original request
        for key in self.data.keys():
            # Skip if this is a date component we're replacing
            if key in date_components_to_skip:
                continue

            values = self.data.getlist(key)
            for value in values:
                if value:  # Only add non-empty values
                    cleaned_data.appendlist(key, value)

        # Add computed date components
        for key, value in date_components_to_add.items():
            if value:  # Only add non-empty values
                cleaned_data[key] = value

        cleaned_data._mutable = False
        return cleaned_data

    def cross_validate(self) -> list[str]:
        """Form-level validation for date ranges"""
        errors = []

        # Document date range validation
        doc_from = self.fields[FieldsConstant.RECORD_DATE_FROM].cleaned
        doc_to = self.fields[FieldsConstant.RECORD_DATE_TO].cleaned

        # It's OK to have just one date (from OR to)
        if doc_from and doc_to and doc_from > doc_to:
            errors.append(
                "Document 'from' date must be before or equal to 'to' date"
            )

        # Opening date range validation
        opening_from = self.fields[FieldsConstant.OPENING_DATE_FROM].cleaned
        opening_to = self.fields[FieldsConstant.OPENING_DATE_TO].cleaned

        if opening_from and opening_to and opening_from > opening_to:
            errors.append(
                "Opening 'from' date must be before or equal to 'to' date"
            )

        return errors

    def get_api_date_params(self) -> dict:
        """Get formatted date parameters for API request"""
        params = {}

        # Record dates
        if rd_from := self.fields[
            FieldsConstant.RECORD_DATE_FROM
        ].format_for_api():
            params["record_date_from"] = rd_from
        if rd_to := self.fields[FieldsConstant.RECORD_DATE_TO].format_for_api():
            params["record_date_to"] = rd_to

        # Opening dates
        if od_from := self.fields[
            FieldsConstant.OPENING_DATE_FROM
        ].format_for_api():
            params["opening_date_from"] = od_from
        if od_to := self.fields[
            FieldsConstant.OPENING_DATE_TO
        ].format_for_api():
            params["opening_date_to"] = od_to

        return params
