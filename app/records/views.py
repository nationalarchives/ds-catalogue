"""Class-based views for displaying archive records."""

import logging

from app.records.enrichment import RecordEnrichmentHelper
from app.records.labels import FIELD_LABELS
from app.records.mixins import GlobalAlertsMixin, RecordContextMixin
from django.views.generic import TemplateView

from .constants import RecordTypes

logger = logging.getLogger(__name__)


class RecordDetailView(
    GlobalAlertsMixin,
    RecordContextMixin,
    TemplateView,
):
    """View for rendering an individual archive record's details page."""

    template_name = "records/record_detail.html"
    related_records_limit = 3

    def get_template_names(self):
        """Determine template based on record type."""
        record = self.get_record()

        if record.custom_record_type == RecordTypes.ARCHON:
            return ["records/archon_detail.html"]
        elif record.custom_record_type == RecordTypes.CREATORS:
            return ["records/creator_detail.html"]

        return [self.template_name]

    def get_context_data(self, **kwargs):
        """Build context with record and enrichment data."""
        context = super().get_context_data(**kwargs)

        record = context["record"]

        # Fetch enrichment data
        enrichment_helper = RecordEnrichmentHelper(
            record, related_limit=self.related_records_limit
        )
        enrichment = enrichment_helper.fetch_all()

        # Add enrichment to context
        record._subjects_enrichment = enrichment["subjects_enrichment"]
        context["related_records"] = enrichment["related_records"]
        context["distressing_content"] = enrichment["distressing_content"]

        if enrichment["delivery_options"]:
            context.update(enrichment["delivery_options"])

        # Add field labels and analytics
        context["field_labels"] = FIELD_LABELS
        self._add_analytics_data(context)

        return context

    def _add_analytics_data(self, context) -> None:
        """Add analytics data to context for data layer tracking."""
        record = context["record"]
        data = {}

        # Content group
        if record.is_tna:
            data["content_group"] = "TNA catalogue"
        else:
            data["content_group"] = "Other Archives catalogue"

        # Page type
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
        data["user_type"] = ""
        data["taxonomy_topic"] = ";".join(record.subjects)
        data["taxonomy_term"] = "not in use"
        data["time_period"] = "not in use"

        # Repository
        if record.is_held_by_tna:
            held_by = "66-The National Archives"
        else:
            held_by = record.held_by
        data["catalogue_repository"] = held_by

        # Level
        data["catalogue_level"] = str(record.level_code) + "-" + record.level

        # Series
        if series := record.hierarchy_series:
            data["catalogue_series"] = (
                series.reference_number + "-" + series.summary_title
            )
        else:
            data["catalogue_series"] = ""

        # Reference
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

        context["analytics_data"] = data


class RelatedRecordsView(RecordContextMixin, TemplateView):
    """View for rendering a record's related records page."""

    template_name = "records/related_records.html"


class RecordsHelpView(RecordContextMixin, TemplateView):
    """View for rendering help/guidance for users new to archives."""

    template_name = "records/new_to_archives.html"
