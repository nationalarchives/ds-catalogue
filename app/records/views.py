"""Class-based views for displaying archive records."""

import logging

from app.records.api import get_subjects_enrichment, record_details_by_id
from app.records.labels import FIELD_LABELS
from app.records.mixins import (
    DeliveryOptionsMixin,
    GlobalAlertsMixin,
    ParallelAPIMixin,
    ProgressiveLoadMixin,
    RecordContextMixin,
    RelatedRecordsMixin,
)
from app.records.models import Record
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.generic import TemplateView

logger = logging.getLogger(__name__)


# TODO: some of these mixins are too small and should be refactored.
class RecordDetailView(
    ProgressiveLoadMixin,
    ParallelAPIMixin,
    DeliveryOptionsMixin,
    RelatedRecordsMixin,
    GlobalAlertsMixin,
    RecordContextMixin,
    TemplateView,
):
    """
    View for rendering an individual archive record's details page.

    Fetches record data by ID. For JS-enabled users, returns primary record data
    immediately and secondary data loads progressively via AJAX. For no-JS users,
    noscript tags in the template provide full content via parallel API calls.

    NOTE: Mixin order matters! ProgressiveLoadMixin must be first to detect load mode.
    ParallelAPIMixin should be before the data mixins. RecordContextMixin must be
    closest to TemplateView so it runs first and adds the record to context.

    Performance: 
    - JS users: Primary content renders in ~0.5s, secondary loads progressively
    - No-JS users: Parallel fetching reduces page load from ~4-6s to ~1-2s
    """

    template_name = "records/record_detail.html"
    related_records_limit = 3  # Used by ParallelAPIMixin

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
        """
        Add field labels and enriched data to context.

        In progressive mode, only primary record data is included.
        In non-progressive mode (noscript or fragment requests), all data
        is fetched in parallel.
        """
        context = super().get_context_data(**kwargs)

        # Get the record (this must complete first)
        record = context["record"]

        # Check if we're in progressive mode
        if context.get('progressive_mode'):
            # Progressive mode: Only include primary record data
            # JavaScript will load secondary content asynchronously
            # Set empty defaults for secondary data
            context["related_records"] = []
            context["distressing_content"] = False
            # Don't set subjects_enrichment - template checks for its existence
        else:
            # Non-progressive mode: Fetch all enrichment data in parallel
            # This is used for noscript fallbacks and fragment requests
            enrichment = self.fetch_enrichment_data_parallel(record)

            # Add enrichment data to context
            record._subjects_enrichment = enrichment["subjects_enrichment"]
            context["related_records"] = enrichment["related_records"]
            context.update(enrichment["delivery_options"])
            context["distressing_content"] = enrichment["distressing_content"]

        # Add field labels and analytics (always needed)
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


# Fragment views for progressive loading
class RecordFragmentMixin:
    """Base mixin for record fragment views - provides record fetching."""
    
    def get_record(self) -> Record:
        """Fetch the record by ID from URL kwargs."""
        if not hasattr(self, "_record"):
            self._record = record_details_by_id(id=self.kwargs["id"])
        return self._record


class DeliveryOptionsFragmentView(
    DeliveryOptionsMixin,
    RecordFragmentMixin,
    TemplateView
):
    """
    AJAX endpoint for loading delivery options (availability cards) fragment.
    
    Returns rendered HTML for the "Is it available online?" and 
    "Can I see it in person?" cards.
    """
    
    template_name = "records/fragments/delivery_options.html"
    
    def get(self, request, *args, **kwargs):
        """Fetch delivery options and return rendered HTML fragment."""
        record = self.get_record()
        
        context = {'record': record}
        
        # Add delivery options data if applicable for this record type
        if self.should_include_delivery_options(record):
            temp_context = self.get_temporary_delivery_options_context(record)
            do_context = self.get_delivery_options_context(record.id)
            
            # DEBUG: Print what we're adding to context
            print(f"=== DELIVERY OPTIONS FRAGMENT DEBUG ===")
            print(f"Record ID: {record.id}")
            print(f"Temp context keys: {temp_context.keys()}")
            print(f"DO context keys: {do_context.keys()}")
            print(f"do_availability_group: {do_context.get('do_availability_group')}")
            
            context.update(temp_context)
            context.update(do_context)
        
        html = render_to_string(self.template_name, context, request=request)
        return HttpResponse(html)


class RelatedRecordsFragmentView(
    RelatedRecordsMixin,
    RecordFragmentMixin,
    TemplateView
):
    """
    AJAX endpoint for loading related records fragment.
    
    Returns rendered HTML for the related records block.
    """
    
    template_name = "records/fragments/related_records.html"
    related_records_limit = 3
    
    def get(self, request, *args, **kwargs):
        """Fetch related records and return rendered HTML fragment."""
        record = self.get_record()
        related_records = self.get_related_records(record)
        
        context = {
            'record': record,
            'related_records': related_records,
        }
        
        html = render_to_string(self.template_name, context, request=request)
        return HttpResponse(html)


class SubjectsEnrichmentFragmentView(RecordFragmentMixin, TemplateView):
    """
    AJAX endpoint for loading subjects enrichment (Wagtail) fragment.
    
    Returns rendered HTML for the related content block based on record subjects.
    """
    
    template_name = "records/fragments/subjects_enrichment.html"
    
    def get(self, request, *args, **kwargs):
        """Fetch subjects enrichment and return rendered HTML fragment."""
        record = self.get_record()
        
        subjects_enrichment = {}
        if record.subjects:
            try:
                subjects_enrichment = get_subjects_enrichment(
                    record.subjects, 
                    limit=settings.MAX_SUBJECTS_PER_RECORD
                )
            except Exception as e:
                logger.warning(
                    f"Failed to fetch subjects enrichment for record {record.id}: {e}"
                )
        
        # Set enrichment data on record for template access
        record._subjects_enrichment = subjects_enrichment
        
        context = {'record': record}
        
        html = render_to_string(self.template_name, context, request=request)
        return HttpResponse(html)