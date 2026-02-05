"""Class-based views for displaying archive records with progressive loading."""

import logging

from app.records.enrichment import RecordEnrichmentHelper
from app.records.labels import FIELD_LABELS
from app.records.mixins import GlobalAlertsMixin, RecordContextMixin
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views import View
from django.views.generic import TemplateView

logger = logging.getLogger(__name__)


class RecordDetailView(
    GlobalAlertsMixin,
    RecordContextMixin,
    TemplateView,
):
    """View for rendering an individual archive record's details page with progressive loading."""

    template_name = "records/record_detail.html"
    related_records_limit = 3

    def get_template_names(self):
        """Determine template based on record type."""
        record = self.get_record()

        if record.custom_record_type == "ARCHON":
            return ["records/archon_detail.html"]
        elif record.custom_record_type == "CREATORS":
            return ["records/creator_detail.html"]

        return [self.template_name]

    def get_context_data(self, **kwargs):
        """Build context with record data. Enrichment fetched based on JS capability."""
        context = super().get_context_data(**kwargs)

        record = context["record"]

        # Add field labels
        context["field_labels"] = FIELD_LABELS

        # Check if JavaScript is enabled (cookie set by JS on previous visit)
        js_enabled = self.request.COOKIES.get("js_enabled") == "true"
        context["js_enabled"] = js_enabled

        # Determine if delivery options should be loaded (not for high-level records)
        high_level_records = ["Series", "Division", "Department", "Sub-series", "Sub-sub-series"]
        context["should_load_delivery"] = record.level not in high_level_records

        if js_enabled:
            # JS is enabled - skip enrichment, let JavaScript load progressively
            # Only fetch distressing_content as it's needed for initial page padding
            enrichment_helper = RecordEnrichmentHelper(record)
            context["distressing_content"] = (
                enrichment_helper.fetch_distressing()
            )

            # Set empty defaults for template
            context["related_records"] = []
            context["do_availability_group"] = None
            context["delivery_option"] = None
            context["delivery_options_heading"] = "How to order it"
            context["delivery_instructions"] = []
            context["tna_discovery_link"] = None

            # Add analytics data without delivery options (JS will update these)
            self._add_analytics_data(context, None)
        else:
            # No JS cookie - fetch ALL enrichment data server-side for no-JS fallback
            enrichment_helper = RecordEnrichmentHelper(
                record, related_limit=self.related_records_limit
            )
            enrichment_data = enrichment_helper.fetch_all()

            # Add enrichment data to context
            context["distressing_content"] = enrichment_data.get(
                "distressing_content", False
            )
            context["related_records"] = enrichment_data.get(
                "related_records", []
            )

            # Apply subjects enrichment to record for template access
            record._subjects_enrichment = enrichment_data.get(
                "subjects_enrichment", {}
            )

            # Process delivery options
            delivery_options = enrichment_data.get("delivery_options", {})
            context["do_availability_group"] = delivery_options.get(
                "do_availability_group"
            )
            context["delivery_option"] = delivery_options.get("delivery_option")
            context["delivery_options_heading"] = delivery_options.get(
                "delivery_options_heading", "How to order it"
            )
            context["delivery_instructions"] = delivery_options.get(
                "delivery_instructions", []
            )
            context["tna_discovery_link"] = delivery_options.get(
                "tna_discovery_link"
            )

            # Add analytics data with delivery options
            self._add_analytics_data(context, delivery_options)

        return context

    def _add_analytics_data(self, context, delivery_options=None) -> None:
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

        # Delivery options from enrichment data
        if delivery_options:
            data["delivery_option_category"] = delivery_options.get(
                "do_availability_group", ""
            )
            data["delivery_option"] = delivery_options.get(
                "delivery_option", ""
            )
        else:
            data["delivery_option_category"] = ""
            data["delivery_option"] = ""

        context["analytics_data"] = data


class RecordSubjectsEnrichmentView(RecordContextMixin, View):
    """API endpoint for Wagtail subjects enrichment (related content)."""

    def get(self, request, *args, **kwargs):
        """Fetch and return subjects enrichment with rendered HTML."""
        record = self.get_record()

        # Fetch subjects enrichment
        enrichment_helper = RecordEnrichmentHelper(record)
        subjects_enrichment = enrichment_helper.fetch_subjects()

        # Apply to record
        record._subjects_enrichment = subjects_enrichment

        # Render HTML
        html = ""
        if record.has_subjects_enrichment:
            html = render_to_string(
                "records/related_content_block_wrapper.html",
                {"record": record},
                request=request,
            )

        return JsonResponse(
            {"success": True, "html": html, "has_content": bool(html)}
        )


class RecordRelatedRecordsView(RecordContextMixin, View):
    """API endpoint for related records."""

    related_records_limit = 3

    def get(self, request, *args, **kwargs):
        """Fetch and return related records with rendered HTML."""
        record = self.get_record()

        # Fetch related records
        enrichment_helper = RecordEnrichmentHelper(
            record, related_limit=self.related_records_limit
        )
        related_records = enrichment_helper.fetch_related()

        # Render HTML
        html = ""
        if related_records:
            html = render_to_string(
                "records/related_records_block_wrapper.html",
                {"record": record, "related_records": related_records},
                request=request,
            )

        return JsonResponse(
            {
                "success": True,
                "html": html,
                "has_content": bool(related_records),
            }
        )


class RecordDeliveryOptionsView(RecordContextMixin, View):
    """API endpoint for delivery options - updates multiple page sections."""

    def get(self, request, *args, **kwargs):
        """Fetch delivery options and return rendered HTML for all affected sections."""
        record = self.get_record()

        # Fetch delivery options
        enrichment_helper = RecordEnrichmentHelper(record)
        delivery_data = enrichment_helper.fetch_delivery_options()

        response = {
            "success": True,
            "has_content": True,  # Always true because we always want to show the sections
            "sections": {},
        }

        # Extract data (will be None for non-TNA records without API data)
        do_availability_group = (
            delivery_data.get("do_availability_group")
            if delivery_data
            else None
        )
        delivery_option = (
            delivery_data.get("delivery_option") if delivery_data else None
        )

        # Render "Available online" section
        response["sections"]["available_online"] = render_to_string(
            "records/available_online_wrapper.html",
            {"record": record, "do_availability_group": do_availability_group},
            request=request,
        )

        # Render "Available in person" section
        response["sections"]["available_in_person"] = render_to_string(
            "records/available_in_person_wrapper.html",
            {"record": record, "do_availability_group": do_availability_group},
            request=request,
        )

        # Render "How to order" accordion item (only if we have delivery_option)
        if delivery_option:
            response["sections"]["how_to_order"] = render_to_string(
                "records/how_to_order_wrapper.html",
                {
                    "delivery_instructions": delivery_data.get(
                        "delivery_instructions", []
                    ),
                    "tna_discovery_link": delivery_data.get(
                        "tna_discovery_link"
                    ),
                },
                request=request,
            )
            response["sections"]["how_to_order_title"] = delivery_data.get(
                "delivery_options_heading", "How to order it"
            )

        # Include analytics data
        response["analytics"] = {
            "delivery_option": delivery_option or "",
            "delivery_option_category": do_availability_group or "",
        }

        return JsonResponse(response)


class RelatedRecordsView(RecordContextMixin, TemplateView):
    """View for rendering a record's related records page."""

    template_name = "records/related_records.html"


class RecordsHelpView(RecordContextMixin, TemplateView):
    """View for rendering help/guidance for users new to archives."""

    template_name = "records/new_to_archives.html"
