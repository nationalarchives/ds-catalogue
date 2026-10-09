from functools import cached_property

from app.lib.fields import DynamicMultipleChoiceField
from config.utils.query_string import qs_replace_value

from .buckets import Aggregation
from .constants import (
    PARLIAMENTARY_ARCHIVE_COLLECTION_PARENT_HINT,
    PARLIAMENTARY_ARCHIVE_COLLECTION_PARENT_VALUE,
    FieldsConstant,
)


def is_parliamentary_archive_parent(value):
    """Returns True if the value represents a parliamentary archive parent collection."""

    return value == PARLIAMENTARY_ARCHIVE_COLLECTION_PARENT_VALUE


def is_parliamentary_archive_child(value):
    """Returns True if the value represents a parliamentary archive child collection."""

    return value.startswith(
        PARLIAMENTARY_ARCHIVE_COLLECTION_PARENT_VALUE
    ) and not is_parliamentary_archive_parent(value)


class NestedCollectionDynamicMultipleChoiceField(DynamicMultipleChoiceField):
    """A dynamic multiple choice field that includes nested parliamentary archive collections."""

    def _get_more_filter_options(self):
        """Builds more filter options for the nested collection field."""

        # TODO: Determine dynamically if more filter choices are available
        more_filter_choices_available = False
        more_filter_choices_text = more_filter_choices_url = ""

        if more_filter_choices_available:
            # adds filter_list=<Aggregation long_aggs value> to existing query string

            long_aggs = Aggregation.get_long_aggs_name_for_field_name(self.name)

            more_filter_choices_url = "?" + qs_replace_value(
                existing_qs=self.request.GET,
                filter=FieldsConstant.FILTER_LIST,
                by=long_aggs,
            )

            more_filter_choices_text = "See more UK Parliamentary collections"

        return (
            more_filter_choices_available,
            more_filter_choices_text,
            more_filter_choices_url,
        )

    @cached_property
    def items(self) -> list[dict[str, str | bool | list[dict[str, str | bool]]]]:
        """Returns a transformed list of items with nested children for parliamentary archive collections."""

        items = super().items

        # return original items if filter_list is applied
        if getattr(self, "filter_list_applied", False) is True:
            return items

        # transform for nested children in standard filters
        new_items = []  # transformed list of items with nested children
        children = []

        # create new list of items except those starting with "Y" as children
        for item in items:
            if is_parliamentary_archive_child(item["value"]):
                children.append(
                    {
                        "text": item["text"],
                        "value": item["value"],
                        "checked": True,
                        "is_child": True,
                    }
                    if (item["value"] in self.value)
                    else {
                        "text": item["text"],
                        "value": item["value"],
                        "is_child": True,
                    }
                )
            else:
                new_items.append(item)

        # identify and modify the parent item for the nested children
        for new_item in new_items:
            if new_item["value"] == PARLIAMENTARY_ARCHIVE_COLLECTION_PARENT_VALUE:
                new_item["is_parent"] = True
                new_item["hint"] = PARLIAMENTARY_ARCHIVE_COLLECTION_PARENT_HINT
                (
                    new_item["more_filter_choices_available"],
                    new_item["more_filter_choices_text"],
                    new_item["more_filter_choices_url"],
                ) = self._get_more_filter_options()

                if children:
                    # child is present, attach children to the parent
                    new_item["children"] = children
                    # reinitialize the parent's checked status to True
                    # in case where the url does not include the parent
                    if not new_item.get("checked"):
                        new_item["checked"] = True
                    break

        return new_items
