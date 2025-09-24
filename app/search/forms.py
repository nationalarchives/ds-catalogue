from abc import ABC, abstractmethod

from app.lib.fields import (
    CharField,
    ChoiceField,
    DateComponentField,
    DynamicMultipleChoiceField,
)
from app.lib.forms import BaseForm
from app.records.constants import TNA_LEVELS
from app.search.buckets import CATALOGUE_BUCKETS
from app.search.constants import Sort

from .collection_names import COLLECTION_CHOICES


class FieldsConstant:
    Q = "q"
    SORT = "sort"
    LEVEL = "level"
    GROUP = "group"
    COLLECTION = "collection"
    ONLINE = "online"
    HELD_BY = "held_by"
    RECORD_DATE_FROM = "record_date_from"
    RECORD_DATE_TO = "record_date_to"
    OPENING_DATE_FROM = "opening_date_from"
    OPENING_DATE_TO = "opening_date_to"


class BaseCatalogueSearchForm(BaseForm, ABC):
    """Abstract base class for catalogue search forms with common functionality"""

    def __init__(self, data=None):
        super().__init__(data)
        # Pass form data to date fields so they can access components
        # This must happen after BaseForm.__init__ has called add_fields()
        for field_name, field in self.fields.items():
            if isinstance(field, DateComponentField):
                field.set_form_data(self.data if data else {})

    def get_common_fields(self):
        """Returns fields common to all catalogue search forms"""
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
            FieldsConstant.RECORD_DATE_FROM: DateComponentField(
                label="Record date from",
                padding_strategy=DateComponentField.start_of_period_strategy,
                required=False,
            ),
            FieldsConstant.RECORD_DATE_TO: DateComponentField(
                label="Record date to",
                padding_strategy=DateComponentField.end_of_period_strategy,
                required=False,
            ),
        }

    @abstractmethod
    def get_specific_fields(self):
        """Returns fields specific to the form subclass"""
        pass

    def add_fields(self):
        """Combines common and specific fields - called by BaseForm.__init__"""
        fields = self.get_common_fields()
        fields.update(self.get_specific_fields())
        return fields

    def cross_validate(self) -> list[str]:
        """Validate date ranges - from dates should not be later than to dates"""
        errors = []

        # Validate record date range
        record_date_from = self.fields[FieldsConstant.RECORD_DATE_FROM].cleaned
        record_date_to = self.fields[FieldsConstant.RECORD_DATE_TO].cleaned

        if (
            record_date_from
            and record_date_to
            and record_date_from > record_date_to
        ):
            errors.append("Record date 'from' cannot be later than 'to' date")

        # Validate opening date range (only for TNA forms that have these fields)
        if (
            FieldsConstant.OPENING_DATE_FROM in self.fields
            and FieldsConstant.OPENING_DATE_TO in self.fields
        ):

            opening_date_from = self.fields[
                FieldsConstant.OPENING_DATE_FROM
            ].cleaned
            opening_date_to = self.fields[
                FieldsConstant.OPENING_DATE_TO
            ].cleaned

            if (
                opening_date_from
                and opening_date_to
                and opening_date_from > opening_date_to
            ):
                errors.append(
                    "Opening date 'from' cannot be later than 'to' date"
                )

        return errors

    def get_api_date_params(self) -> list[str]:
        """Get formatted date parameters as filter list for API request"""
        date_filters = []

        def get_field_value(field_name):
            if field_name in self.fields and hasattr(
                self.fields[field_name], "format_for_api"
            ):
                return self.fields[field_name].format_for_api()
            return None

        # Record dates (common to all forms)
        if record_date_from := get_field_value(FieldsConstant.RECORD_DATE_FROM):
            date_filters.append(f"coveringFromDate:(>={record_date_from})")
        if record_date_to := get_field_value(FieldsConstant.RECORD_DATE_TO):
            date_filters.append(f"coveringToDate:(<={record_date_to})")

        # Opening dates (only for TNA forms - check if fields exist)
        if opening_date_from := get_field_value(
            FieldsConstant.OPENING_DATE_FROM
        ):
            date_filters.append(f"openingFromDate:(>={opening_date_from})")
        if opening_date_to := get_field_value(FieldsConstant.OPENING_DATE_TO):
            date_filters.append(f"openingToDate:(<={opening_date_to})")

        return date_filters


class CatalogueSearchTnaForm(BaseCatalogueSearchForm):
    """TNA-specific search form with opening dates and other TNA-only fields"""

    def get_specific_fields(self):
        return {
            FieldsConstant.LEVEL: DynamicMultipleChoiceField(
                label="Filter by levels",
                choices=list((level, level) for level in TNA_LEVELS.values()),
                validate_input=True,
                active_filter_label="Level",
            ),
            FieldsConstant.COLLECTION: DynamicMultipleChoiceField(
                label="Collections",
                choices=COLLECTION_CHOICES,
                validate_input=False,
                active_filter_label="Collection",
            ),
            FieldsConstant.ONLINE: ChoiceField(
                choices=[
                    ("", "All records"),
                    ("true", "Available online only"),
                ],
                required=False,
                active_filter_label="Online only",
            ),
            # TNA-specific opening date fields
            FieldsConstant.OPENING_DATE_FROM: DateComponentField(
                label="Opening date from",
                padding_strategy=DateComponentField.start_of_period_strategy,
                required=False,
            ),
            FieldsConstant.OPENING_DATE_TO: DateComponentField(
                label="Opening date to",
                padding_strategy=DateComponentField.end_of_period_strategy,
                required=False,
            ),
        }


class CatalogueSearchNonTnaForm(BaseCatalogueSearchForm):
    """Non-TNA search form without opening dates"""

    def get_specific_fields(self):
        return {
            FieldsConstant.HELD_BY: DynamicMultipleChoiceField(
                label="Held by",
                choices=[],
                active_filter_label="Held by",
            ),
        }
