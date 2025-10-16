from app.lib.fields import (
    CharField,
    ChoiceField,
    DynamicMultipleChoiceField,
    FromDateField,
    ToDateField,
)
from app.lib.forms import BaseForm
from app.records.constants import TNA_LEVELS
from app.search.buckets import CATALOGUE_BUCKETS, Aggregation
from app.search.constants import Sort

from .collection_names import COLLECTION_CHOICES


class FieldsConstant:

    Q = "q"
    SORT = "sort"
    LEVEL = "level"
    GROUP = "group"
    COLLECTION = "collection"
    ONLINE = "online"
    SUBJECT = "subject"
    HELD_BY = "held_by"
    CLOSURE = "closure"
    FILTER_LIST = "filter_list"
    COVERING_DATE_FROM = "covering_date_from"
    COVERING_DATE_TO = "covering_date_to"
    OPENING_DATE_FROM = "opening_date_from"
    OPENING_DATE_TO = "opening_date_to"


class CatalogueSearchBaseForm(BaseForm):

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
        }

    def cross_validate(self) -> list[str]:
        error_messages = super().cross_validate()
        date_range_message = self.validate_date_range(
            self.fields.get(FieldsConstant.COVERING_DATE_FROM),
            self.fields.get(FieldsConstant.COVERING_DATE_TO),
            "Record dates",
        )
        error_messages.extend(date_range_message)
        return error_messages

    def validate_date_range(
        self, date_from: FromDateField, date_to: ToDateField, prefix_text: str
    ) -> list[str]:
        """Validate that date_from is earlier than or equal to date_to.
        Subclass and call from cross_validate() to add error messages to form.
        """

        error_messages = []
        if (
            date_from.cleaned
            and date_to.cleaned
            and date_from.cleaned > date_to.cleaned
        ):
            # add error at field and form level

            # add field error to first date field
            field_message = (
                "This date must be earlier than or equal to the 'to' date."
            )
            date_from.add_error(field_message)

            # add cross field error message (not derived from field)
            # use _cleaned since an error has been added to the field and cleaned is now None
            cross_field_message = f"{prefix_text}: {date_from._cleaned.strftime("%d-%m-%Y")} must be earlier than or equal to the {date_to._cleaned.strftime("%d-%m-%Y")}."
            error_messages.append(cross_field_message)

        return error_messages


class CatalogueSearchTnaForm(CatalogueSearchBaseForm):

    def add_fields(self):

        fields = super().add_fields()

        return fields | {
            FieldsConstant.LEVEL: DynamicMultipleChoiceField(
                label="Filter by levels",
                choices=list((level, level) for level in TNA_LEVELS.values()),
                validate_input=True,  # validate input with choices before querying the API
                active_filter_label="Level",
            ),
            FieldsConstant.COLLECTION: DynamicMultipleChoiceField(
                label="Collections",
                choices=COLLECTION_CHOICES,
                validate_input=False,  # do not validate input COLLECTION_CHOICES fixed or dynamic
                active_filter_label="Collection",
            ),
            FieldsConstant.SUBJECT: DynamicMultipleChoiceField(
                label="Subjects",
                choices=[],  # no initial choices as they are set dynamically
                active_filter_label="Subject",
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
            FieldsConstant.FILTER_LIST: ChoiceField(
                choices=[
                    ("", "No filter"),
                    (
                        Aggregation.COLLECTION.long_aggs,
                        FieldsConstant.COLLECTION,
                    ),
                    (
                        Aggregation.SUBJECT.long_aggs,
                        FieldsConstant.SUBJECT,
                    ),
                ],
            ),
            FieldsConstant.COVERING_DATE_FROM: FromDateField(
                label="From",
                active_filter_label="Record date from",
                progressive=True,  # interfaces with FE component for progressive date entry
                date_ymd_separator="-",  # FE component uses this value as separator for ymd date entry
            ),
            FieldsConstant.COVERING_DATE_TO: ToDateField(
                label="To",
                active_filter_label="Record date to",
                progressive=True,  # interfaces with FE component for progressive date entry
                date_ymd_separator="-",  # FE component uses this value as separator for ymd date entry
            ),
            FieldsConstant.OPENING_DATE_FROM: FromDateField(
                label="From",
                active_filter_label="Opening date from",
                progressive=True,  # interfaces with FE component for progressive date entry
                date_ymd_separator="-",  # FE component uses this value as separator for ymd date entry
            ),
            FieldsConstant.OPENING_DATE_TO: ToDateField(
                label="To",
                active_filter_label="Opening date to",
                progressive=True,  # interfaces with FE component for progressive date entry
                date_ymd_separator="-",  # FE component uses this value as separator for ymd date entry
            ),
        }

    def cross_validate(self) -> list[str]:
        error_messages = super().cross_validate()
        date_range_message = self.validate_date_range(
            self.fields.get(FieldsConstant.OPENING_DATE_FROM),
            self.fields.get(FieldsConstant.OPENING_DATE_TO),
            "Record opening dates",
        )
        error_messages.extend(date_range_message)
        return error_messages


class CatalogueSearchNonTnaForm(CatalogueSearchBaseForm):

    def add_fields(self):

        fields = super().add_fields()

        return fields | {
            FieldsConstant.COVERING_DATE_FROM: FromDateField(
                label="From",
                active_filter_label="Record date from",
                progressive=True,  # interfaces with FE component for progressive date entry
                date_ymd_separator="-",  # FE component uses this value as separator for ymd date entry
            ),
            FieldsConstant.COVERING_DATE_TO: ToDateField(
                label="To",
                active_filter_label="Record date to",
                progressive=True,  # interfaces with FE component for progressive date entry
                date_ymd_separator="-",  # FE component uses this value as separator for ymd date entry
            ),
            FieldsConstant.HELD_BY: DynamicMultipleChoiceField(
                label="Held by",
                choices=[],  # no initial choices as they are set dynamically
                active_filter_label="Held by",
            ),
        }
