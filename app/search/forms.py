from app.lib.constants import DATE_YMD_SEPARATOR
from app.lib.fields import (
    CharField,
    ChoiceField,
    DynamicMultipleChoiceField,
    FromDateField,
    ToDateField,
)
from app.lib.forms import BaseForm
from app.records.constants import TnaLevels

from .buckets import CATALOGUE_BUCKETS, Aggregation
from .collection_names import COLLECTION_CHOICES
from .constants import (
    DATE_DISPLAY_FORMAT,
    Display,
    FieldsConstant,
    Sort,
)


class AdvancedSearchForm(BaseForm):
    def add_fields(self):
        return {
            FieldsConstant.ALL_WORDS: CharField(
                required=False,
                label="All of these words",
                hint="Include the important words, for example: medal card UK",
            ),
            FieldsConstant.EXACT_WORDS: CharField(
                required=False,
                label="These exact words or phrases",
                hint="Put each word on a new line, for example:<br>medal<br>card",
            ),
            FieldsConstant.ANY_WORDS: CharField(
                required=False,
                label="Any of these words",
                hint="Put each word on a new line, for example:<br>medal<br>card",
            ),
            FieldsConstant.IGNORE_WORDS: CharField(
                required=False,
                label="Ignore these words",
                hint="Put each word on a new line, for example:<br>medal<br>card",
            ),
            FieldsConstant.REFERENCES: CharField(
                required=False,
                label="Search for or within any of these references",
                hint="Put each catalogue reference on a new line, for example: <br>WO 95<br>WO 96",
            ),
            FieldsConstant.COVERING_DATE_FROM: FromDateField(
                label="From",
                required=False,
                progressive=True,
                date_ymd_separator=DATE_YMD_SEPARATOR,
                hint="For example: 1997, 1999 and 1, or 1997 1 and 31",
            ),
            FieldsConstant.COVERING_DATE_TO: ToDateField(
                label="To",
                required=False,
                progressive=True,
                date_ymd_separator=DATE_YMD_SEPARATOR,
                hint="For example: 1997, 1999 and 1, or 1997 1 and 31",
            ),
        }

    def cross_validate(self) -> list[str]:
        errors = []
        date_from = self.fields[FieldsConstant.COVERING_DATE_FROM]
        date_to = self.fields[FieldsConstant.COVERING_DATE_TO]

        if (
            date_from.cleaned
            and date_to.cleaned
            and date_from.cleaned > date_to.cleaned
        ):
            from_date = date_from.cleaned.strftime(DATE_DISPLAY_FORMAT)
            to_date = date_to.cleaned.strftime(DATE_DISPLAY_FORMAT)

            date_from.add_error(
                "This date must be earlier than or equal to the 'to' date."
            )
            errors.append(
                f"Record dates: 'from' date ({from_date}) cannot be after 'to' date ({to_date})."
            )
        return errors


class CatalogueSearchBaseForm(BaseForm):
    """This is Base form that corresponds to top level (UI) for catalogue search
    page. Other fields and validations are added in subclass forms."""

    def add_fields(self):

        return {
            # determines the Catalogue Search TNA or NonTNA form to use
            FieldsConstant.GROUP: ChoiceField(
                choices=CATALOGUE_BUCKETS.as_choices(),
            ),
            # search term
            FieldsConstant.Q: CharField(),
        }


class CatalogueSearchCommonForm(CatalogueSearchBaseForm):
    """Common fields and validation for TNA and Non-TNA catalogue search forms."""

    def add_fields(self):

        fields = super().add_fields()

        return fields | {
            FieldsConstant.SORT: ChoiceField(
                choices=[
                    (Sort.RELEVANCE.value, "Relevance"),
                    (Sort.DATE_DESC.value, "Date (newest first)"),
                    (Sort.DATE_ASC.value, "Date (oldest first)"),
                    (Sort.TITLE_ASC.value, "Title (A–Z)"),
                    (Sort.TITLE_DESC.value, "Title (Z–A)"),
                ],
            ),
            FieldsConstant.FILTER_LIST: ChoiceField(
                choices=Aggregation.as_input_choices_for_long_aggs(),
            ),
            FieldsConstant.DISPLAY: ChoiceField(
                choices=[
                    (Display.LIST.value, "List view"),
                    (Display.GRID.value, "Grid view"),
                ],
                required=False,
            ),
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
            field_message = "This date must be earlier than or equal to the 'to' date."

            # add cross field error message (not derived from field)
            cross_field_message = (
                f"{prefix_text}: 'from' date ({date_from.cleaned.strftime(DATE_DISPLAY_FORMAT)}) "
                f"cannot be after 'to' date ({date_to.cleaned.strftime(DATE_DISPLAY_FORMAT)})."
            )

            # NOTE: add error after building cross field message to use cleaned date
            date_from.add_error(field_message)

            error_messages.append(cross_field_message)

        return error_messages


class CatalogueSearchTnaForm(CatalogueSearchCommonForm):
    def add_fields(self):

        fields = super().add_fields()

        return (
            fields
            | {
                FieldsConstant.LEVEL: DynamicMultipleChoiceField(
                    label="Filter by levels",
                    choices=[(m.level, m.level) for m in TnaLevels],
                    validate_input=True,  # validate input with choices before querying the API
                    active_filter_label="Level",
                    more_filter_choices_text="See more levels",
                ),
                FieldsConstant.COLLECTION: DynamicMultipleChoiceField(
                    label="Collections",
                    choices=COLLECTION_CHOICES,
                    validate_input=False,  # do not validate input COLLECTION_CHOICES fixed or dynamic
                    active_filter_label="Collection",
                    more_filter_choices_text="See more collections",
                ),
                FieldsConstant.SUBJECT: DynamicMultipleChoiceField(
                    label="Subjects",
                    choices=[],  # no initial choices as they are set dynamically
                    active_filter_label="Subject",
                    more_filter_choices_text="See more subjects",
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
                FieldsConstant.COVERING_DATE_FROM: FromDateField(
                    label="From",
                    active_filter_label="Record date from",
                    progressive=True,  # interfaces with FE component for progressive date entry
                    date_ymd_separator=DATE_YMD_SEPARATOR,  # FE component uses this value as separator for ymd date entry
                ),
                FieldsConstant.COVERING_DATE_TO: ToDateField(
                    label="To",
                    active_filter_label="Record date to",
                    progressive=True,  # interfaces with FE component for progressive date entry
                    date_ymd_separator=DATE_YMD_SEPARATOR,  # FE component uses this value as separator for ymd date entry
                ),
                FieldsConstant.OPENING_DATE_FROM: FromDateField(
                    label="From",
                    active_filter_label="Opening date from",
                    progressive=True,  # interfaces with FE component for progressive date entry
                    date_ymd_separator=DATE_YMD_SEPARATOR,  # FE component uses this value as separator for ymd date entry
                ),
                FieldsConstant.OPENING_DATE_TO: ToDateField(
                    label="To",
                    active_filter_label="Opening date to",
                    progressive=True,  # interfaces with FE component for progressive date entry
                    date_ymd_separator=DATE_YMD_SEPARATOR,  # FE component uses this value as separator for ymd date entry
                ),
            }
        )

    def cross_validate(self) -> list[str]:
        error_messages = super().cross_validate()
        date_range_message = self.validate_date_range(
            self.fields.get(FieldsConstant.OPENING_DATE_FROM),
            self.fields.get(FieldsConstant.OPENING_DATE_TO),
            "Record opening dates",
        )
        error_messages.extend(date_range_message)
        return error_messages


class CatalogueSearchNonTnaForm(CatalogueSearchCommonForm):
    def add_fields(self):

        fields = super().add_fields()

        return (
            fields
            | {
                FieldsConstant.COVERING_DATE_FROM: FromDateField(
                    label="From",
                    active_filter_label="Record date from",
                    progressive=True,  # interfaces with FE component for progressive date entry
                    date_ymd_separator=DATE_YMD_SEPARATOR,  # FE component uses this value as separator for ymd date entry
                ),
                FieldsConstant.COVERING_DATE_TO: ToDateField(
                    label="To",
                    active_filter_label="Record date to",
                    progressive=True,  # interfaces with FE component for progressive date entry
                    date_ymd_separator=DATE_YMD_SEPARATOR,  # FE component uses this value as separator for ymd date entry
                ),
                FieldsConstant.HELD_BY: DynamicMultipleChoiceField(
                    label="Held by",
                    choices=[],  # no initial choices as they are set dynamically
                    active_filter_label="Held by",
                    more_filter_choices_text="See more held by",
                ),
            }
        )
