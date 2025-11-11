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
