"""Helper for fetching record enrichment data."""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps
from typing import Any, Dict

import sentry_sdk
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
from app.records.api import get_subjects_enrichment
from app.records.constants import API_TIMEOUTS, THREADPOOL_MAX_WORKERS
from app.records.models import Record
from app.records.related import (
    get_related_records_by_series,
    get_tna_related_records_by_subjects,
)
from app.records.utils import log_enrichment_execution_time
from django.conf import settings

logger = logging.getLogger(__name__)


class RecordEnrichmentHelper:
    """
    Helper class for fetching enrichment data for record detail pages.

    Supports both parallel and sequential fetching based on feature flag.
    """

    def __init__(self, record: Record, related_limit: int = 3):
        self.record = record
        self.related_limit = related_limit

    @log_enrichment_execution_time
    def fetch_all(self) -> Dict[str, Any]:
        """
        Fetch all enrichment data.

        Uses parallel or sequential execution based on
        settings.ENABLE_PARALLEL_API_CALLS.

        Returns:
            Dictionary with keys: subjects_enrichment, related_records,
            delivery_options, distressing_content
        """
        if settings.ENABLE_PARALLEL_API_CALLS:
            return self._fetch_parallel()
        else:
            return self._fetch_sequential()

    def _submit_fetch_tasks(self, executor) -> dict:
        """Submit all fetch tasks to the executor and return futures map."""
        futures_map = {}

        # Submit subjects fetch
        try:
            futures_map[executor.submit(self._fetch_subjects)] = "subjects"
        except RuntimeError:
            message = (
                f"Failed to submit subjects task for record {self.record.id}"
            )
            logger.error(message)

        # Submit related fetch
        try:
            futures_map[executor.submit(self._fetch_related)] = "related"
        except RuntimeError:
            message = (
                f"Failed to submit related task for record {self.record.id}"
            )
            logger.error(message)

        # Submit delivery options if applicable
        if self._should_include_delivery_options():
            try:
                futures_map[executor.submit(self._fetch_delivery_options)] = (
                    "delivery"
                )
            except RuntimeError:
                message = f"Failed to submit delivery task for record {self.record.id}"
                logger.error(message)

        return futures_map

    def _process_future_result(self, future, name, timeout, results):
        """Process a single future result and update results dict."""
        try:
            result = future.result(timeout=timeout)
            if name == "subjects":
                results["subjects_enrichment"] = result
            elif name == "related":
                results["related_records"] = result
            elif name == "delivery":
                results["delivery_options"] = result
        except Exception as e:
            message = f"ThreadPoolExecutor: Failed to fetch {name} for record {self.record.id}"
            logger.warning(message)
            sentry_sdk.capture_exception(e)
            sentry_sdk.set_context(
                "threadpool_fetch_failure",
                {"record_id": self.record.id, "task": name, "timeout": timeout},
            )

    def _log_completion_timing(self, completion_order, completion_times):
        """Log completion timing if enabled."""
        if settings.ENRICHMENT_TIMING_ENABLED and completion_order:
            timing_details = ", ".join(
                f"{name}: {completion_times[name]:.3f}s"
                for name in completion_order
            )
            logger.info(
                f"Record {self.record.id} completion order: [{timing_details}]"
            )

    def _fetch_parallel(self) -> Dict[str, Any]:
        """Fetch enrichment data in parallel using thread pool."""
        results = self._empty_results()
        completion_order = []
        completion_times = {}

        with ThreadPoolExecutor(max_workers=THREADPOOL_MAX_WORKERS) as executor:
            futures_map = self._submit_fetch_tasks(executor)
            start_time = time.time()

            # Process futures as they complete
            for future in as_completed(futures_map):
                name = futures_map[future]
                timeout = API_TIMEOUTS[name]
                elapsed = time.time() - start_time
                completion_order.append(name)
                completion_times[name] = elapsed

                self._process_future_result(future, name, timeout, results)

            self._log_completion_timing(completion_order, completion_times)

        # Fetch distressing content directly (not an API call, no need for threading)
        results["distressing_content"] = self._fetch_distressing()

        return results

    def _fetch_sequential(self) -> Dict[str, Any]:
        """Fetch enrichment data sequentially."""
        results = {
            "subjects_enrichment": self._fetch_subjects(),
            "related_records": self._fetch_related(),
            "delivery_options": {},
            "distressing_content": self._fetch_distressing(),
        }

        if self._should_include_delivery_options():
            results["delivery_options"] = self._fetch_delivery_options()

        return results

    def _fetch_subjects(self) -> dict:
        return get_subjects_enrichment(
            self.record.subjects,
            limit=settings.MAX_SUBJECTS_PER_RECORD,
            timeout=settings.WAGTAIL_API_TIMEOUT,
        )

    def _fetch_related(self) -> list:
        """
        Fetch related records using subject matching with series backfill.

        Strategy:
        1. Search for records sharing subjects (random selection from candidates)
        2. If fewer than limit found, backfill from same series

        Returns:
            List of related Record objects (up to related_limit), or empty list
        """
        related = get_tna_related_records_by_subjects(
            self.record,
            limit=self.related_limit,
            timeout=settings.ROSETTA_ENRICHMENT_API_TIMEOUT,
        )

        # Backfill from series if needed
        if len(related) < self.related_limit:
            remaining = self.related_limit - len(related)
            series_records = get_related_records_by_series(
                self.record,
                limit=remaining,
                timeout=settings.ROSETTA_ENRICHMENT_API_TIMEOUT,
            )
            related.extend(series_records)

        return related

    def _fetch_delivery_options(self) -> dict:
        """
        Fetch delivery options and add temporary display context.

        Combines API data (availability conditions/groups) with hardcoded
        display text and Discovery link. The temporary context is a placeholder
        pending UX decisions on final presentation.

        Returns:
            Dictionary with delivery_option, do_availability_group, display
            heading, instructions, and Discovery link. Empty dict on any error.
        """
        try:
            # Get API data
            api_context = self._get_delivery_api_data()

            # TODO: This is an alternative action on delivery options whilst we wait on decisions on how we are going to present it.

            # Add temporary display context
            temp_context = {
                "delivery_options_heading": "How to order it",
                "delivery_instructions": [
                    "View this record page in our current catalogue",
                    "Check viewing and downloading options",
                    "Select an option and follow instructions",
                ],
                "tna_discovery_link": (
                    f"{BASE_TNA_DISCOVERY_URL}/details/r/{self.record.id}"
                ),
            }

            api_context.update(temp_context)
            return api_context
        except Exception as e:
            logger.warning(
                f"Failed to fetch delivery options for {self.record.id}: {e}"
            )
            return {}

    def _get_delivery_api_data(self) -> dict:
        """
        Fetch and process delivery options data from the API.

        Queries the delivery options API and extracts the availability condition
        and availability group for the record. Handles various error cases gracefully
        by returning an empty dict.

        Returns:
            Dictionary with delivery option data:
            - 'delivery_option': Name of the AvailabilityCondition enum
            - 'do_availability_group': Name of the availability group enum, if applicable

            Returns empty dict if:
            - API returns non-list or empty result
            - First result has no 'options' field
            - Delivery option value is not a valid AvailabilityCondition
        """

        delivery_result = delivery_options_request_handler(
            self.record.id, timeout=settings.DELIVERY_OPTIONS_API_TIMEOUT
        )

        if not isinstance(delivery_result, list) or not delivery_result:
            return {}

        first_result = delivery_result[0]
        delivery_option_value = first_result.get("options")

        if delivery_option_value is None:
            return {}

        try:
            delivery_option_enum = AvailabilityCondition(delivery_option_value)
            delivery_option_name = delivery_option_enum.name
        except ValueError:
            logger.warning(
                f"Unknown delivery option value {delivery_option_value} "
                f"for iaid {self.record.id}"
            )
            return {}

        data = {"delivery_option": delivery_option_name}

        do_availability_group = get_availability_group(delivery_option_value)
        if do_availability_group is not None:
            data["do_availability_group"] = do_availability_group.name

        return data

    def _fetch_distressing(self) -> bool:
        try:
            return has_distressing_content(self.record.reference_number)
        except Exception as e:
            logger.warning(
                f"Failed to check distressing content for {self.record.id}: {e}"
            )
            return False

    def _should_include_delivery_options(self) -> bool:
        if self.record.custom_record_type in ["ARCHON", "CREATORS"]:
            return False

        if (
            self.record.is_tna
            and self.record.level_code in DELIVERY_OPTIONS_TNA_LEVELS
        ):
            return True
        elif (
            not self.record.is_tna
            and self.record.level_code in DELIVERY_OPTIONS_NON_TNA_LEVELS
        ):
            return True

        return False

    @staticmethod
    def _empty_results() -> Dict[str, Any]:
        return {
            "subjects_enrichment": {},
            "related_records": [],
            "delivery_options": {},
            "distressing_content": False,
        }
