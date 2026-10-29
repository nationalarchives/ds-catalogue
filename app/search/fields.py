from functools import cached_property

from app.lib.fields import DynamicMultipleChoiceField
from config.utils.query_string import qs_replace_value

from .buckets import Aggregation
from .collection_names import COLLECTION_NAMES
from .constants import (
    HINT_KEY,
    MAX_FILTER_CHOICES,
    NESTED_CHILDREN_KEY,
    NESTED_IS_CHILD_KEY,
    NESTED_IS_PARENT_KEY,
    PARLIAMENTARY_ARCHIVE_COLLECTION_PARENT_HINT,
    PARLIAMENTARY_ARCHIVE_COLLECTION_PARENT_VALUE,
    FieldsConstant,
)
from .parliamentary_archives import (
    is_parliamentary_archive_child,
    is_parliamentary_archive_parent,
)


class NestedCollectionDynamicMultipleChoiceField(DynamicMultipleChoiceField):
    """A dynamic multiple choice field that includes nested parliamentary archive collections.
    parent collection - the top-level parliamentary archive collection.
                        Y is the value representing the parent collection.
    child collections - sub-level parliamentary archive collections.
                        value begins with the parent collection value.]
                        E.g.: YHL, YHC.
    The field handles the display and selection of both parent and child collections in the UI.
    """

    def __init__(self, choices: list[tuple[str, str]], **kwargs):
        super().__init__(choices, **kwargs)
        # additional arributes for long filter and nested choices link handling.
        self.collection_filter_list_applied = False
        self.request = None

    def _build_more_filter_options_for_parliamentary_archives(
        self, item: dict[str, str | int]
    ):
        """Returns the text and URL for more filter options related to nested parliamentary
        archive collections.
        """

        # adds filter_list=<Aggregation long_aggs value> to existing query string.
        long_aggs = Aggregation.get_long_aggs_name_for_field_name(self.name)

        # add the parent collection parameter to the query string.
        parent_collection_param = f"&{FieldsConstant.COLLECTION}={PARLIAMENTARY_ARCHIVE_COLLECTION_PARENT_VALUE}"

        # check if parent collection parameter is already present in the query string.
        if parent_collection_param in self.request.GET.urlencode():
            parent_collection_param = ""

        more_filter_choices_url = (
            "?"
            + qs_replace_value(
                existing_qs=self.request.GET,
                filter=FieldsConstant.FILTER_LIST,
                by=long_aggs,
            )
            + parent_collection_param
        )

        more_filter_choices_text = f"See more {COLLECTION_NAMES[PARLIAMENTARY_ARCHIVE_COLLECTION_PARENT_VALUE]} collections"

        item["more_filter_choices_available"] = True
        item["more_filter_choices_text"] = more_filter_choices_text
        item["more_filter_choices_url"] = more_filter_choices_url

    def remove_parent_from_selected_values(self, selected_values):
        """Removes the parent collection from the selected values if the long filter is applied."""
        selected_values = [
            value
            for value in selected_values
            if not is_parliamentary_archive_parent(value)
        ]
        return selected_values

    def get_missing_choices(
        self,
        selected_values,
        choice_vals_with_hits: set,
    ):
        if self.collection_filter_list_applied:
            selected_values = self.remove_parent_from_selected_values(selected_values)
            return super().get_missing_choices(selected_values, choice_vals_with_hits)

        missing_choices = []
        for missing_value in [
            v for v in selected_values if v not in choice_vals_with_hits
        ]:
            try:
                label_base = self.configured_choice_labels[missing_value]
            except KeyError:
                label_base = missing_value
            missing_choices.append((missing_value, f"{label_base} (0)", None))

        return missing_choices

    def update_choices(
        self,
        choice_api_data: list[dict[str, str | int | list[dict]]],
        selected_values,
    ):
        """
        Handles choice field data for nested and long filters selections.
        Updates this fields `choices` list using aggregation data from the most recent
        API result. If `selected_values` is provided, options with values matching items
        in that list will be preserved in the new `choices` list, even if they are not
        present in `choice_api_data`.

        Updated choice formats:
        1) Regular choices:
        [("Value", "Display", None)] - None indicates no children
        2) Nested choices with children:
        [("Value", "Display", [("ChildValue", "ChildDisplay", None)]),]

        Examples:
        1) api: [{"value": "BT","doc_count": 10},]
           updated: [("BT", "BT - Board of Trade and successors (10)", None)]
        2) api: [{"value": "Y","doc_count": 15,"children": [{"value": "YHC", "doc_count": 10},]},]
           updated:[("Y", "Y - UK Parliament (15)'", [("YHC", "YHC - Records of the House of Commons (10)", None)]),]
        3) missing:[("PIZZA", "PIZZA (0)", None)]
        """

        # If there is no API data and no selected values, clear choices and return early.
        if not choice_api_data and not selected_values:
            self.choices = []
            self.choices_updated = True
            return

        # Long filter pages do show nested choices, so fall back to the default implementation.
        if self.collection_filter_list_applied:
            # remove parent from choice_api_data for long filter pages
            # when parent only, or child without parent, remove the parent from API data
            has_parent = False
            has_child = False
            for value in selected_values:
                if is_parliamentary_archive_child(value):
                    has_child = True
                if is_parliamentary_archive_parent(value):
                    has_parent = True
            if (
                (has_parent and not has_child)
                or (has_child and not has_parent)
                or (has_parent and has_child)
            ):
                choice_api_data = [
                    item
                    for item in choice_api_data
                    if not is_parliamentary_archive_parent(item["value"])
                ]
            super().update_choices(choice_api_data, selected_values)
            return

        # Generate a new list of choices.
        choices = []  # List of choices to be used for the field.
        choice_vals_with_hits = set()  # Track values that have hits in the API data.

        for item in choice_api_data:
            # initialize the list of choices for children of the current item.
            choices_of_children = []

            if NESTED_CHILDREN_KEY in item:
                children = item[NESTED_CHILDREN_KEY]
                # Process children of the current item.
                for child in children:
                    choices_of_children.append(
                        (child["value"], self.choice_label_from_api_data(child), None)
                    )
                    choice_vals_with_hits.add(child["value"])

                # Append the parent item with its children choices.
                choices.append(
                    (
                        item["value"],
                        self.choice_label_from_api_data(item),
                        choices_of_children,
                    )
                )
            else:
                # Not a parent, regular entry.
                choices.append(
                    (item["value"], self.choice_label_from_api_data(item), None)
                )
            choice_vals_with_hits.add(item["value"])

        missing_choices = self.get_missing_choices(
            selected_values, choice_vals_with_hits
        )
        choices.extend(missing_choices)

        # Replace the field's attribute value.
        self.choices = choices
        self.choices_updated = True

    @cached_property
    def items(self):

        def is_parent_choice(children_choices: list | None):
            """Return True if the choice represents a parent, even without children.
            children_choices is the third element of the choice tuple.
            None, [...] - possible values for the third element of the choice tuple
            E.g.:
            1) [("value", "label", None)] - parent choice without children
               None is not a parent choice
            2) [("value", "label", [...])] - parent choice with children
               [...] i.e. [("value", "label", None)] is a child choice without its children
               currently there is only one level of parent-child relationships.
            """
            return children_choices is not None

        def selection_contains_parent_or_child(selected_values):
            """Returns True if the selection contains any parliamentary archive parent or child."""

            return any(
                is_parliamentary_archive_parent(value)
                or is_parliamentary_archive_child(value)
                for value in selected_values
            )

        # Long filter pages do show nested choices, so fall back to the default implementation
        if self.collection_filter_list_applied:
            return super().items

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

        items = []
        for value, display_value, children_choices in self.choices:
            item = {}
            if value in self.value:
                item = {"text": display_value, "value": value, "checked": True}
            else:
                item = {"text": display_value, "value": value}

            display_children_items = []

            if is_parent_choice(children_choices):
                item[NESTED_IS_PARENT_KEY] = True

                # show hint for parent choice when it has children choices
                if len(children_choices) > 0:
                    item[HINT_KEY] = PARLIAMENTARY_ARCHIVE_COLLECTION_PARENT_HINT

                # add children choices to display only if the selection contains any parent or child
                if selection_contains_parent_or_child(self.value):
                    for child_value, child_display_value, _ in children_choices:
                        child_item = {"text": child_display_value, "value": child_value}
                        if child_value in self.value:
                            child_item["checked"] = True
                        child_item[NESTED_IS_CHILD_KEY] = True
                        display_children_items.append(child_item)

                    item[NESTED_CHILDREN_KEY] = display_children_items

                    # Special case: manually mark the parent as checked if any of its children
                    # exist but the parent itself is not checked or absence from url is not flagged
                    if (
                        len(children_choices) > 0
                        and getattr(item, "checked", None) is None
                        and PARLIAMENTARY_ARCHIVE_COLLECTION_PARENT_VALUE
                        not in self.value
                    ):
                        item["checked"] = True

                # build more filter options for parliamentary archives if the number of
                # display children items exceeds the maximum allowed
                if len(display_children_items) > MAX_FILTER_CHOICES:
                    self._build_more_filter_options_for_parliamentary_archives(item)

            items.append(item)

        return items
