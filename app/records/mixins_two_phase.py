"""
Two-phase optimization for record detail page.

Phase 1: Fetch record (sequential - required first)
Phase 2: Fetch everything else in parallel (5 calls across 3 APIs)

This works with WSGI because we're hitting different domains in parallel.
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor

from app.deliveryoptions.api import delivery_options_request_handler
from app.deliveryoptions.constants import (
    DELIVERY_OPTIONS_NON_TNA_LEVELS,
    DELIVERY_OPTIONS_TNA_LEVELS,
    AvailabilityCondition,
)
from app.deliveryoptions.delivery_options import (
    get_availability_group,
    has_distressing_content,
)
from app.deliveryoptions.helpers import BASE_TNA_DISCOVERY_URL
from app.lib.api import JSONAPIClient
from app.records.api import get_subjects_enrichment, record_details_by_id

# Import original mixins for backward compatibility
from app.records.mixins import (
    DeliveryOptionsMixin,
    DistressingContentMixin,
    GlobalAlertsMixin,
    RecordContextMixin,
    RelatedRecordsMixin,
    SubjectsEnrichmentMixin,
)
from app.records.models import Record
from app.records.related import (
    get_related_records_by_series,
    get_tna_related_records_by_subjects,
)
from django.conf import settings

logger = logging.getLogger(__name__)


class TwoPhaseParallelMixin:
    """
    Two-phase optimization:

    Phase 1 (sequential): Fetch the record
    Phase 2 (parallel): Fetch everything that depends on the record

    This creates 5 parallel threads in Phase 2, hitting 3 different APIs:
    - Wagtail (alerts + related content)
    - Rosetta (2x related record searches)
    - Delivery Options (1x delivery options)
    """

    related_records_limit = 3

    def get_context_data(self, **kwargs):
        """Fetch data in two phases."""
        context = super().get_context_data(**kwargs)

        total_start = time.time()
        record_id = self.kwargs["id"]

        # Phase 1: Fetch the record (must be first)
        record = self._execute_phase1(record_id, context)

        # Phase 2: Fetch everything else in parallel (5 calls)
        self._execute_phase2(record, context)

        total_time = (time.time() - total_start) * 1000
        logger.info(f"[PERFORMANCE] Total: {total_time:.0f}ms")

        return context

    def _execute_phase1(self, record_id: str, context: dict) -> Record:
        """Execute Phase 1: Fetch the record."""
        phase1_start = time.time()

        try:
            record = record_details_by_id(id=record_id)
            context["record"] = record
            self._record = record
        except Exception as e:
            logger.error(f"Failed to fetch record: {e}")
            raise

        phase1_time = (time.time() - phase1_start) * 1000
        logger.info(f"[PERFORMANCE] Phase 1 (get record): {phase1_time:.0f}ms")

        return record

    def _execute_phase2(self, record: Record, context: dict) -> None:
        """Execute Phase 2: Fetch everything else in parallel."""
        phase2_start = time.time()

        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all parallel tasks
            futures = self._submit_phase2_tasks(executor, record)

            # Collect results
            self._collect_phase2_results(futures, record, context)

        phase2_time = (time.time() - phase2_start) * 1000
        logger.info(
            f"[PERFORMANCE] Phase 2 (5 parallel calls): {phase2_time:.0f}ms"
        )

    def _submit_phase2_tasks(self, executor, record: Record) -> dict:
        """Submit all Phase 2 tasks to the executor."""
        return {
            "alerts": executor.submit(self._fetch_global_alerts),
            "subjects": executor.submit(
                self._fetch_subjects_enrichment, record
            ),
            "delivery": executor.submit(self._fetch_delivery_options, record),
            "related_subjects": executor.submit(
                get_tna_related_records_by_subjects,
                record,
                self.related_records_limit,
            ),
            "related_series": executor.submit(
                get_related_records_by_series,
                record,
                self.related_records_limit,
            ),
        }

    def _collect_phase2_results(
        self, futures: dict, record: Record, context: dict
    ) -> None:
        """Collect and process results from Phase 2 tasks."""
        # Global alerts
        context["global_alert"] = self._get_result_safe(
            futures["alerts"], {}, "global alerts"
        )

        # Subjects enrichment
        record._subjects_enrichment = self._get_result_safe(
            futures["subjects"], {}, "subjects enrichment"
        )

        # Delivery options
        delivery_context = self._get_result_safe(
            futures["delivery"], {}, "delivery options"
        )
        if delivery_context and self._should_include_delivery_options(record):
            context.update(delivery_context)
            context.update(self._get_temporary_delivery_options_context(record))

        # Related records
        subjects_records = self._get_result_safe(
            futures["related_subjects"], [], "subject-based related records"
        )
        series_records = self._get_result_safe(
            futures["related_series"], [], "series-based related records"
        )
        context["related_records"] = self._combine_related_records(
            subjects_records, series_records
        )

        # Distressing content
        try:
            context["distressing_content"] = has_distressing_content(
                record.reference_number
            )
        except Exception as e:
            logger.warning(f"Failed to check distressing content: {e}")
            context["distressing_content"] = False

    def _get_result_safe(self, future, default, description: str):
        """Safely get result from a future with error handling."""
        try:
            return future.result()
        except Exception as e:
            logger.warning(f"Failed to fetch {description}: {e}")
            return default

    def _combine_related_records(
        self, subjects_records: list, series_records: list
    ) -> list:
        """Combine subject and series related records."""
        related_records = subjects_records

        if len(related_records) < self.related_records_limit:
            existing_iaids = {r.iaid for r in related_records}
            for series_record in series_records:
                if series_record.iaid not in existing_iaids:
                    related_records.append(series_record)
                    if len(related_records) >= self.related_records_limit:
                        break

        return related_records

    # ========================================================================
    # Helper methods for Phase 2 parallel calls
    # ========================================================================

    def _fetch_global_alerts(self) -> dict:
        """2a. Fetch global alerts from Wagtail."""
        try:
            client = JSONAPIClient(settings.WAGTAIL_API_URL)
            client.add_parameters({"fields": "_,global_alert,mourning_notice"})
            return client.get(f"/pages/{settings.WAGTAIL_HOME_PAGE_ID}/")
        except Exception as e:
            logger.error(f"Failed to fetch global alerts: {e}")
            return {}

    def _fetch_subjects_enrichment(self, record: Record) -> dict:
        """2b. Fetch subjects enrichment from Wagtail."""
        if not record.subjects:
            return {}

        try:
            return get_subjects_enrichment(
                record.subjects, limit=settings.MAX_SUBJECTS_PER_RECORD
            )
        except Exception as e:
            logger.warning(f"Failed to fetch subjects enrichment: {e}")
            return {}

    def _fetch_delivery_options(self, record: Record) -> dict:
        """2c. Fetch delivery options."""
        if not self._should_include_delivery_options(record):
            return {}

        try:
            delivery_result = delivery_options_request_handler(record.iaid)

            if not isinstance(delivery_result, list) or not delivery_result:
                return {}

            first_result = delivery_result[0]
            delivery_option_value = first_result.get("options")

            if delivery_option_value is None:
                return {}

            try:
                delivery_option_enum = AvailabilityCondition(
                    delivery_option_value
                )
                delivery_option_name = delivery_option_enum.name
            except ValueError:
                logger.warning(
                    f"Unknown delivery option value {delivery_option_value} "
                    f"for iaid {record.iaid}"
                )
                return {}

            context = {"delivery_option": delivery_option_name}

            do_availability_group = get_availability_group(
                delivery_option_value
            )
            if do_availability_group is not None:
                context["do_availability_group"] = do_availability_group.name

            return context

        except Exception as e:
            logger.error(
                f"Failed to get delivery options for iaid {record.iaid}: {e}",
                exc_info=True,
            )
            return {}

    def _should_include_delivery_options(self, record: Record) -> bool:
        """Check if delivery options should be included."""
        if record.custom_record_type in ["ARCHON", "CREATORS"]:
            return False

        if record.is_tna and record.level_code in DELIVERY_OPTIONS_TNA_LEVELS:
            return True

        if (
            not record.is_tna
            and record.level_code in DELIVERY_OPTIONS_NON_TNA_LEVELS
        ):
            return True

        return False

    def _get_temporary_delivery_options_context(self, record: Record) -> dict:
        """Get temporary delivery options display context."""
        return {
            "delivery_options_heading": "How to order it",
            "delivery_instructions": [
                "View this record page in our current catalogue",
                "Check viewing and downloading options",
                "Select an option and follow instructions",
            ],
            "tna_discovery_link": f"{BASE_TNA_DISCOVERY_URL}/details/r/{record.iaid}",
        }
