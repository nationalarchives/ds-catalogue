"""Parliamentary archives related search utilities."""

from config.utils.query_string import qs_toggle_value

from .buckets import Aggregation
from .constants import (
    MAX_FILTER_CHOICES,
    NESTED_CHILDREN_KEY,
    PARLIAMENTARY_ARCHIVE_COLLECTION_PARENT_VALUE,
    FieldsConstant,
)


def is_parliamentary_archive_parent(value):
    """Returns True if the value represents a parliamentary archive parent collection. False otherwise."""

    return value == PARLIAMENTARY_ARCHIVE_COLLECTION_PARENT_VALUE


def is_parliamentary_archive_child(value):
    """Returns True if the value represents a parliamentary archive child collection. False otherwise."""

    return value.startswith(
        PARLIAMENTARY_ARCHIVE_COLLECTION_PARENT_VALUE
    ) and not is_parliamentary_archive_parent(value)


def is_collection_filter_list_applied(form):
    """Returns True if the collection filter list is applied for the collection field. False otherwise."""

    if form.fields.get(FieldsConstant.FILTER_LIST) and form.fields[
        FieldsConstant.FILTER_LIST
    ].cleaned == Aggregation.get_long_aggs_name_for_field_name(
        FieldsConstant.COLLECTION
    ):
        return True

    return False


def build_choice_api_data_for_collection_filter(
    field_name, form, choice_api_data, request
) -> list[dict[str, str | int | list[dict]]]:
    """Builds choice API data for the collection field, handling both direct and nested choices."""

    if is_collection_filter_list_applied(form):
        # set to direct updating choices, items for long filters page that
        # do not have nested choices
        form.fields[field_name].collection_filter_list_applied = True
        choice_api_data = prepare_api_long_filter_list_entries_for_parliament_archives(
            choice_api_data, form.fields[field_name].value
        )
    else:
        # set request for nested choice more options link handling
        form.fields[field_name].request = request
        nested_choice_api_data = (
            prepare_api_parent_child_entries_for_parliamentay_archives(choice_api_data)
        )
        choice_api_data = nested_choice_api_data

    return choice_api_data


def prepare_api_parent_child_entries_for_parliamentay_archives(
    api_entries: list[dict[str, str | int]] | dict[str, str | int],
) -> list[dict[str, str | int | list[dict]]]:
    """Returns transformed entries with parent positioned correctly and children nested appropriately.

    Note:
    "Y" represents the parent collection for parliamentary archives.
    "YHC" and "YHL" represent child collections under the parent "Y".

    Format:
    1. If children exist, attach children to the parent entry under the key specified by NESTED_CHILDREN_KEY.
        E.g.:
        api entries before transformation:
            [{"value": "BT", "doc_count": 50},
            {"value": "Y", "doc_count": 15},
            {"value": "WO", "doc_count": 12},
            {"value": "YHC", "doc_count": 13},
            {"value": "YHL", "doc_count": 9}]
        api entries after transformation:
            [{"value": "BT", "doc_count": 50},
            {"value": "Y", "doc_count": 15,
                            "children": [{"value": "YHC", "doc_count": 13},
                                         {"value": "YHL", "doc_count": 9}],
            {"value": "WO", "doc_count": 12}}]
    2. Remove empty parent entry: { "value": "Y", "doc_count": 0 }
    3. Preserve original order of entries and adjust position of parent "Y" if it appears after
    MAX_FILTER_CHOICES (e.g. 10 entries) if necessary so that it remains visible (subject to FE constraints)
    4. special case: single entry for parent "Y" with zero doc_count should be returned as a
    list containing that entry to ensure bucket counts visibility.
    """

    # special case:
    # api returns single entry for parent "Y" with zero doc_count as dict.
    # e.g. when an invalid collection is queried ?collection=PIZZA
    # coearse it into a list for consistent handling
    single_entry = {"value": "Y", "doc_count": 0}
    if (
        isinstance(api_entries, dict)
        and len(api_entries) == 2
        and api_entries == single_entry
    ):
        return []

    parent = None
    children = []
    remaining = []
    original_parent_index = None

    # Identify the parent, children, and remaining entries
    for index, entry in enumerate(api_entries):
        value = entry["value"]

        if is_parliamentary_archive_parent(value):
            # special case: api returns parent entry with zero doc_count
            if entry["doc_count"] == 0:
                continue
            # keep only parents with non-zero doc_count
            parent = entry.copy()
            original_parent_index = index
        elif is_parliamentary_archive_child(value):
            children.append(entry.copy())
        else:
            remaining.append(entry.copy())

    # If no parent exists, return the entries unchanged
    if parent is None:
        return remaining

    # Attach children to the parent
    if children:
        parent[NESTED_CHILDREN_KEY] = children

    # Preserve the parent's original relative position
    adjusted_index = sum(
        1
        for entry in api_entries[:original_parent_index]
        if not is_parliamentary_archive_child(entry["value"])
    )

    # Insert the parent back into the remaining entries at its adjusted index
    remaining.insert(adjusted_index, parent)

    # Move Y to the 10th position if it is outside the first 10
    # and none of its children appeared in the original first 10
    original_first_upto_max = api_entries[:MAX_FILTER_CHOICES]
    has_child_in_first_upto_max = any(
        is_parliamentary_archive_child(entry["value"])
        for entry in original_first_upto_max
    )

    # Find the current index of the parent in the remaining entries
    parent_index = next(
        (
            i
            for i, entry in enumerate(remaining)
            if is_parliamentary_archive_parent(entry["value"])
        ),
        None,
    )

    # Move the parent to the 10th position if it is outside the first 10 and none of its children appeared in the original first 10
    if parent_index >= MAX_FILTER_CHOICES and not has_child_in_first_upto_max:
        remaining.insert(MAX_FILTER_CHOICES - 1, remaining.pop(parent_index))

    return remaining


def prepare_api_long_filter_list_entries_for_parliament_archives(
    entries, selected_values
):
    """Returns transformed entries that are used for long filter lists. Preserves the original
    order of entries and adjusts the position of parliamentary archive parent if necessary."""

    def selection_contains_parent_or_child(selected_values):
        """Returns True if the selection contains any parliamentary archive parent or child."""

        return any(
            is_parliamentary_archive_parent(value)
            or is_parliamentary_archive_child(value)
            for value in selected_values
        )

    def prepare_entries_parent_without_children(entries):
        """This is usually for entries related to the "See more collections" link.
        Keep parent entries and other entries, discarding child entries.
        Preserves the original order of entries. Adjusts parent's position if necessary."""

        # Remove child entries and entries with a doc_count of 0
        remaining = [
            entry.copy()
            for entry in entries
            if not is_parliamentary_archive_child(entry["value"])
            and entry["doc_count"] != 0
        ]

        # Find the current index of the parent in the remaining entries
        parent_index = next(
            (
                i
                for i, entry in enumerate(remaining)
                if is_parliamentary_archive_parent(entry["value"])
            ),
            None,
        )

        # Move Y to the 10th position if it is outside the first 10
        if parent_index is not None:
            if parent_index >= MAX_FILTER_CHOICES:
                remaining.insert(
                    MAX_FILTER_CHOICES - 1,
                    remaining.pop(parent_index),
                )

        return remaining

    if selection_contains_parent_or_child(selected_values):
        # This usually applies to the specific link e.g. "See more UK Parliamentary collections" link.
        parent_child_entries = [
            entry.copy() for entry in entries if entry["doc_count"] != 0
        ]
        return parent_child_entries
    else:
        # If neither parent nor child is selected, prepare entries normally.
        # This usually applies to the generic link e.g. "See more collections" link.
        return prepare_entries_parent_without_children(entries)


def remove_parliamentary_archives_parent_collection_filter(params: dict) -> dict:
    """Remove the Parliamentary Archives parent filter if any child collection filter is present.
    E.g.
    before adjustment params: {'filter': ['group:tna', 'collection:Y', 'collection:YHC']}
    after adjustment params: {'filter': ['group:tna', 'collection:YHC']}
    """

    filter_name = FieldsConstant.COLLECTION
    if filter_values := params.get("filter", []):
        # split out the collection filter values from the overall filter list
        collection_filter_values = [
            f.split(":", 1)[1] for f in filter_values if f.startswith(f"{filter_name}:")
        ]

        # remove parent collection filter if any child collection filter is present
        params["filter"] = [
            value
            for value in filter_values
            if not (
                value.startswith(f"{filter_name}:")
                and is_parliamentary_archive_parent(value.split(":", 1)[1])
                and any(
                    is_parliamentary_archive_child(child)
                    for child in collection_filter_values
                )
            )
        ]

    return params


def build_collection_active_filters(
    choice_labels, collection_field, request, existing_filters
):

    # Note: copy the input values to avoid modifying the original field value directly
    input_values = collection_field.value.copy()

    # if child and no parent is selected,
    # add parent active filter since Parent should be visible if any child is selected
    # and data contains parent
    for value in input_values:
        if is_parliamentary_archive_child(value):
            parent_value = PARLIAMENTARY_ARCHIVE_COLLECTION_PARENT_VALUE
            if parent_value not in input_values and any(
                item["value"] == parent_value for item in collection_field.items
            ):
                # modify the input values to include the parent if a child is selected
                input_values.append(parent_value)

    for item in input_values:
        href = f"?{qs_toggle_value(request.GET, collection_field.name, item)}"
        if item == PARLIAMENTARY_ARCHIVE_COLLECTION_PARENT_VALUE:
            # Remove all parent and child values from the current field if the parent is selected
            qs = request.GET.copy()
            qs.setlist(
                collection_field.name,
                [
                    value
                    for value in qs.getlist(collection_field.name)
                    if not is_parliamentary_archive_parent(value)
                    and not is_parliamentary_archive_child(value)
                ],
            )
            href = f"?{qs.urlencode()}"

        existing_filters.append(
            {
                "label": f"{collection_field.active_filter_label}: {choice_labels.get(item, item)}",
                "href": href,
                "title": f"Remove {choice_labels.get(item, item)} {collection_field.active_filter_label.lower()}",
            }
        )


def add_child_collection_values_to_first_n(item, max_items, first_n_items):
    """Add child values of the given item to the first_n_items list."""

    if item.get(NESTED_CHILDREN_KEY):
        for child in item[NESTED_CHILDREN_KEY][:max_items]:
            first_n_items.append(child["value"])
