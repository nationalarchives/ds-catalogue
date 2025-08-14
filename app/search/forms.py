from app.lib.fields import (
    CharField,
    ChoiceField,
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


class CatalogueSearchForm(BaseForm):

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
                validate_input=True,  # validate input with choices before querying the API
            ),
            FieldsConstant.COLLECTION: DynamicMultipleChoiceField(
                label="Collections",
                choices=COLLECTION_CHOICES,
                validate_input=False,  # do not validate input COLLECTION_CHOICES fixed or dynamic
            ),
        }
