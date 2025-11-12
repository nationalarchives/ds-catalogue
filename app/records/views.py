"""Class-based views for displaying archive records."""

import logging

from app.records.labels import FIELD_LABELS
from app.records.mixins import (
    DeliveryOptionsMixin,
    DistressingContentMixin,
    GlobalAlertsMixin,
    RecordContextMixin,
    RelatedRecordsMixin,
    SubjectsEnrichmentMixin,
)
from django.views.generic import TemplateView

logger = logging.getLogger(__name__)


# TODO: some of these mixins are too small and should be refactored.
class RecordDetailView(
    DistressingContentMixin,
    DeliveryOptionsMixin,
    RelatedRecordsMixin,
    SubjectsEnrichmentMixin,
    GlobalAlertsMixin,
    RecordContextMixin,
    TemplateView,
):
    """
    View for rendering an individual archive record's details page.

    Fetches record data by ID, enriches it with subjects data, finds related
    records, checks for sensitive content warnings, and renders the appropriate
    template based on the record type (standard, ARCHON, or CREATORS).

    NOTE: Mixin order matters! RecordContextMixin must be closest to TemplateView
    so that it runs first and adds the record to context. Other mixins that depend
    on the record should be listed before RecordContextMixin.
    """

    template_name = "records/record_detail.html"

    # TODO: update this implementation with DataLayerMixin once Mixin's
    # for RecordDetailView is in place.
    def add_analytics_data_context(self, context) -> None:
        """Add analytics data to context for data layer tracking."""

        record = context["record"]
        data = {}

        # Common data for all records
        if record.is_tna:
            data["content_group"] = "TNA catalogue"
        else:
            data["content_group"] = "Other Archives catalogue"

        class_name = self.__class__.__name__
        if record.is_tna:
            if record.is_digitised:
                data["page_type"] = (
                    class_name + "[TNA catalogue digitised record description]"
                )
            else:
                data["page_type"] = (
                    class_name + "[TNA catalogue record description]"
                )
        else:
            data["page_type"] = (
                class_name + "[Other archive record description]"
            )

        data["reader_type"] = ""

        # Record-specific data
        data["user_type"] = ""
        data["taxonomy_topic"] = ";".join(record.subjects)
        data["taxonomy_term"] = "not in use"
        data["time_period"] = "not in use"
        if record.is_held_by_tna:
            held_by = "66-The National Archives"
        else:
            held_by = record.held_by
        data["catalogue_repository"] = held_by
        data["catalogue_level"] = str(record.level_code) + "-" + record.level
        if series := record.hierarchy_series:
            data["catalogue_series"] = (
                series.reference_number + "-" + series.summary_title
            )
        else:
            data["catalogue_series"] = ""

        if record.reference_number and record.summary_title:
            data["catalogue_reference"] = (
                record.reference_number + "-" + record.summary_title
            )
        else:
            data["catalogue_reference"] = record.reference_number
        data["catalogue_datasource"] = record.source
        data["delivery_option_category"] = context.get(
            "do_availability_group", ""
        )
        data["delivery_option"] = context.get("delivery_option", "")

        # Add the data to the context
        context["analytics_data"] = data

    def get_template_names(self):
        """
        Determine template based on record type.

        Returns:
            List containing the appropriate template name
        """
        # Get the record to determine template
        record = self.get_record()

        if record.custom_record_type == "ARCHON":
            return ["records/archon_detail.html"]
        elif record.custom_record_type == "CREATORS":
            return ["records/creator_detail.html"]

        return [self.template_name]

    def get_context_data(self, **kwargs):
        """Add field labels and all enriched data to context."""
        context = super().get_context_data(**kwargs)
        context["field_labels"] = FIELD_LABELS
        self.add_analytics_data_context(context=context)

        return context


# TODO: use this view for related records as originally intended
class RelatedRecordsView(RecordContextMixin, TemplateView):
    """
    View for rendering a record's related records page.

    Displays records that are related to the specified record through
    hierarchical or associative relationships.
    """

    template_name = "records/related_records.html"


class RecordsHelpView(RecordContextMixin, TemplateView):
    """
    View for rendering help/guidance for users new to archives.

    Provides contextual help information about understanding and using
    archive records for the specified record.
    """

    template_name = "records/new_to_archives.html"
