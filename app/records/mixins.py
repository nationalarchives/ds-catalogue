"""Mixins for record views."""

import logging
from typing import Dict

from app.deliveryoptions.api import delivery_options_request_handler
from app.deliveryoptions.constants import AvailabilityCondition
from app.deliveryoptions.delivery_options import (
    get_availability_group,
    has_distressing_content,
)
from app.lib.api import JSONAPIClient
from app.records.api import get_subjects_enrichment, record_details_by_id
from app.records.models import Record
from app.records.related import (
    get_related_records_by_series,
    get_related_records_by_subjects,
)
from django.conf import settings

logger = logging.getLogger(__name__)


class RecordContextMixin:
    """Mixin for adding record to view context."""

    def get_record(self) -> Record:
        """
        Fetch the record by ID from URL kwargs.

        Returns:
            Record object
        """
        if not hasattr(self, "_record"):
            self._record = record_details_by_id(id=self.kwargs["id"])
        return self._record

    def get_context_data(self, **kwargs):
        """Add record to context."""
        context = super().get_context_data(**kwargs)
        # Fetch record once and make it available for other mixins
        context["record"] = self.get_record()
        return context


class GlobalAlertsMixin:
    """Mixin for adding global alerts to context."""

    def get_global_alerts(self) -> dict:
        """
        Fetch global alerts and mourning notices from Wagtail.

        Returns:
            Dictionary containing global_alert data, or empty dict on error
        """
        global_alerts_client = JSONAPIClient(settings.WAGTAIL_API_URL)
        global_alerts_client.add_parameters(
            {"fields": "_,global_alert,mourning_notice"}
        )
        try:
            return global_alerts_client.get(
                f"/pages/{settings.WAGTAIL_HOME_PAGE_ID}"
            )
        except Exception as e:
            logger.error(f"Failed to fetch global alerts: {e}")
            return {}

    def get_context_data(self, **kwargs):
        """Add global alerts to context."""
        context = super().get_context_data(**kwargs)
        context["global_alert"] = self.get_global_alerts()
        return context


class SubjectsEnrichmentMixin:
    """Mixin for enriching records with subjects data."""

    def enrich_record_subjects(self, record: Record) -> None:
        """
        Enrich a record with subjects data in-place.

        Fetches related articles and content for the record's subject tags
        from the Wagtail CMS and attaches them to the record object.

        Args:
            record: The record to enrich (modified in-place)
        """
        if record.subjects:
            logger.info(
                f"Enriching record {record.iaid} with {len(record.subjects)} subjects"
            )
            subjects_enrichment = get_subjects_enrichment(
                record.subjects, limit=settings.MAX_SUBJECTS_PER_RECORD
            )
            record._subjects_enrichment = subjects_enrichment
            logger.info(f"Enrichment data: {subjects_enrichment}")
        else:
            logger.info(f"No subjects to enrich for record {record.iaid}")
            record._subjects_enrichment = {}

    def get_context_data(self, **kwargs):
        """Enrich record with subjects before adding to context."""
        context = super().get_context_data(**kwargs)
        if "record" in context:
            self.enrich_record_subjects(context["record"])
        else:
            logger.warning(
                "No record found in context for SubjectsEnrichmentMixin"
            )
        return context


class RelatedRecordsMixin:
    """Mixin for adding related records to context."""

    related_records_limit = 3

    def get_related_records(self, record: Record) -> list[Record]:
        """
        Fetch related records using subjects first, then series as fallback.

        Attempts to find related records by shared subjects. If fewer than the
        requested limit are found, backfills the remaining slots with records
        from the same archival series.

        Args:
            record: The record to find relations for

        Returns:
            List of related Record objects (up to limit)
        """
        logger.info(f"Fetching related records for {record.iaid}")
        related_records = get_related_records_by_subjects(
            record, limit=self.related_records_limit
        )
        logger.info(f"Found {len(related_records)} related records by subjects")

        # Backfill from series if needed
        if len(related_records) < self.related_records_limit:
            remaining_slots = self.related_records_limit - len(related_records)
            series_records = get_related_records_by_series(
                record, limit=remaining_slots
            )
            logger.info(
                f"Found {len(series_records)} related records by series"
            )
            related_records.extend(series_records)

        logger.info(f"Total related records: {len(related_records)}")
        return related_records

    def get_context_data(self, **kwargs):
        """Add related records to context."""
        context = super().get_context_data(**kwargs)
        if "record" in context:
            context["related_records"] = self.get_related_records(
                context["record"]
            )
            logger.info(
                f"Added {len(context['related_records'])} related records to context"
            )
        else:
            logger.warning("No record found in context for RelatedRecordsMixin")
        return context


class DeliveryOptionsMixin:
    """Mixin for adding delivery options to context."""

    def get_delivery_options_context(self, iaid: str) -> dict:
        """
        Fetch and process delivery options for a record.

        Calls the delivery options API to determine how a record can be accessed
        (e.g., available online, orderable, closed, etc.) and maps the result to
        an availability group for display purposes.

        Args:
            iaid: The document IAID (Information Asset Identifier)

        Returns:
            Dictionary with delivery options context containing:
            - delivery_option: The AvailabilityCondition name as string (if valid)
            - do_availability_group: The availability group name (if mapped to a group)
            Returns empty dict if unavailable or on error.
        """
        try:
            delivery_result = delivery_options_request_handler(iaid)

            # Ensure we have at least one delivery_result in the returned list
            if not isinstance(delivery_result, list) or not delivery_result:
                return {}

            # Extract the delivery option value
            first_result = delivery_result[0]
            delivery_option_value = first_result.get("options")

            if delivery_option_value is None:
                return {}

            # Convert to AvailabilityCondition enum and get name
            try:
                delivery_option_enum = AvailabilityCondition(
                    delivery_option_value
                )
                delivery_option_name = delivery_option_enum.name
            except ValueError:
                logger.warning(
                    f"Unknown delivery option value {delivery_option_value} "
                    f"for iaid {iaid}"
                )
                return {}

            # Build context with the delivery option name
            context = {"delivery_option": delivery_option_name}

            # Get the availability group for this delivery option
            do_availability_group = get_availability_group(
                delivery_option_value
            )

            # Add availability group to context if it exists
            if do_availability_group is not None:
                context["do_availability_group"] = do_availability_group.name

            return context

        except Exception as e:
            logger.error(
                f"Failed to get delivery options for iaid {iaid}: {str(e)}",
                exc_info=True,
            )
            return {}

    def should_include_delivery_options(self, record: Record) -> bool:
        """
        Determine if delivery options should be included for this record type.

        Args:
            record: The record to check

        Returns:
            True if delivery options should be included, False otherwise
        """
        # Don't include for ARCHON or CREATORS record types
        return record.custom_record_type not in ["ARCHON", "CREATORS"]

    def get_context_data(self, **kwargs):
        """Add delivery options to context if applicable."""
        context = super().get_context_data(**kwargs)
        if "record" in context:
            record = context["record"]
            if self.should_include_delivery_options(record):
                context.update(self.get_delivery_options_context(record.iaid))
        return context


class DistressingContentMixin:
    """Mixin for checking and adding distressing content flag to context."""

    def check_distressing_content(self, record: Record) -> bool:
        """
        Check if record has distressing/sensitive content.

        Logs an info message if a content warning is found for the record.

        Args:
            record: The record to check

        Returns:
            True if distressing content warning exists, False otherwise
        """
        has_warning = has_distressing_content(record.reference_number)

        if has_warning:
            logger.info(
                f"Document {record.reference_number} has a sensitive "
                f"content warning"
            )

        return has_warning

    def get_context_data(self, **kwargs):
        """Add distressing content flag to context."""
        context = super().get_context_data(**kwargs)
        if "record" in context:
            context["distressing_content"] = self.check_distressing_content(
                context["record"]
            )
        return context
