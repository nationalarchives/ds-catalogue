from app.lib.fields import (
    CharField,
    ChoiceField,
    DynamicMultipleChoiceField,
    MultiPartDateField,
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
    CLOSURE = "closure"
    COVERING_DATE_FROM = "covering_date_from"
    COVERING_DATE_TO = "covering_date_to"
    OPENING_DATE_FROM = "opening_date_from"
    OPENING_DATE_TO = "opening_date_to"


class CatalogueSearchBaseForm(BaseForm):
    """Base class for catalogue search forms with common functionality"""

    def add_fields(self):
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
            FieldsConstant.COVERING_DATE_FROM: MultiPartDateField(
                label="Covering date from",
                padding_strategy=MultiPartDateField.start_of_period_strategy,
                required=False,
            ),
            FieldsConstant.COVERING_DATE_TO: MultiPartDateField(
                label="Covering date to",
                padding_strategy=MultiPartDateField.end_of_period_strategy,
                required=False,
            ),
        }

    def cross_validate(self) -> list[str]:
        """Validate date ranges - from dates should not be later than to dates"""
        errors = []

        # Validate record date range
        covering_date_from = self.fields[
            FieldsConstant.COVERING_DATE_FROM
        ].cleaned
        covering_date_to = self.fields[FieldsConstant.COVERING_DATE_TO].cleaned

        if (
            covering_date_from
            and covering_date_to
            and covering_date_from > covering_date_to
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
        if covering_date_from := get_field_value(
            FieldsConstant.COVERING_DATE_FROM
        ):
            date_filters.append(f"coveringFromDate:(>={covering_date_from})")
        if covering_date_to := get_field_value(FieldsConstant.COVERING_DATE_TO):
            date_filters.append(f"coveringToDate:(<={covering_date_to})")

        # Opening dates (only for TNA forms - check if fields exist)
        if opening_date_from := get_field_value(
            FieldsConstant.OPENING_DATE_FROM
        ):
            date_filters.append(f"openingFromDate:(>={opening_date_from})")
        if opening_date_to := get_field_value(FieldsConstant.OPENING_DATE_TO):
            date_filters.append(f"openingToDate:(<={opening_date_to})")

        return date_filters


class CatalogueSearchTnaForm(CatalogueSearchBaseForm):
    """TNA-specific search form with opening dates and other TNA-only fields"""

    def add_fields(self):
        fields = super().add_fields()
        fields.update(
            {
                FieldsConstant.LEVEL: DynamicMultipleChoiceField(
                    label="Filter by levels",
                    choices=list(
                        (level, level) for level in TNA_LEVELS.values()
                    ),
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
                FieldsConstant.CLOSURE: DynamicMultipleChoiceField(
                    label="Closure status",
                    choices=[],  # no initial choices as they are set dynamically
                    active_filter_label="Closure status",
                ),
                # TNA-specific opening date fields
                FieldsConstant.OPENING_DATE_FROM: MultiPartDateField(
                    label="Opening date from",
                    padding_strategy=MultiPartDateField.start_of_period_strategy,
                    required=False,
                ),
                FieldsConstant.OPENING_DATE_TO: MultiPartDateField(
                    label="Opening date to",
                    padding_strategy=MultiPartDateField.end_of_period_strategy,
                    required=False,
                ),
            }
        )
        return fields


class CatalogueSearchNonTnaForm(CatalogueSearchBaseForm):
    """Non-TNA search form without opening dates"""

    def add_fields(self):
        fields = super().add_fields()
        fields.update(
            {
                FieldsConstant.HELD_BY: DynamicMultipleChoiceField(
                    label="Held by",
                    choices=[],
                    active_filter_label="Held by",
                ),
            }
        )
        return fields
