"""Helper for fetching record enrichment data."""

import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict

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
from app.records.constants import API_TIMEOUT
from app.records.models import Record
from app.records.related import (
    get_related_records_by_series,
    get_tna_related_records_by_subjects,
)
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

    def _fetch_parallel(self) -> Dict[str, Any]:
        """Fetch enrichment data in parallel using thread pool."""
        results = self._empty_results()

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                "subjects": executor.submit(self._fetch_subjects),
                "related": executor.submit(self._fetch_related),
                "distressing": executor.submit(self._fetch_distressing),
            }

            if self._should_include_delivery_options():
                futures["delivery"] = executor.submit(
                    self._fetch_delivery_options
                )

            for name, future in futures.items():
                try:
                    result = future.result(timeout=API_TIMEOUT)
                    if name == "subjects":
                        results["subjects_enrichment"] = result
                    elif name == "related":
                        results["related_records"] = result
                    elif name == "delivery":
                        results["delivery_options"] = result
                    elif name == "distressing":
                        results["distressing_content"] = result
                except Exception as e:
                    logger.warning(
                        f"Failed to fetch {name} for record {self.record.id}: {e}"
                    )

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
        """Fetch subjects enrichment from Wagtail."""
        return get_subjects_enrichment(
            self.record.subjects, limit=settings.MAX_SUBJECTS_PER_RECORD
        )

    def _fetch_related(self) -> list:
        """Fetch related records using subjects and series."""
        try:
            related = get_tna_related_records_by_subjects(
                self.record, limit=self.related_limit
            )

            if len(related) < self.related_limit:
                remaining = self.related_limit - len(related)
                series_records = get_related_records_by_series(
                    self.record, limit=remaining
                )
                related.extend(series_records)

            return related
        except Exception as e:
            logger.warning(
                f"Failed to fetch related records for {self.record.id}: {e}"
            )
            return []

    def _fetch_delivery_options(self) -> dict:
        """Fetch delivery options if applicable."""
        try:
            # Get API data
            api_context = self._get_delivery_api_data()

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
        """Fetch delivery options from API."""
        delivery_result = delivery_options_request_handler(self.record.id)

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

        context = {"delivery_option": delivery_option_name}

        do_availability_group = get_availability_group(delivery_option_value)
        if do_availability_group is not None:
            context["do_availability_group"] = do_availability_group.name

        return context

    def _fetch_distressing(self) -> bool:
        """Check for distressing content warnings."""
        try:
            return has_distressing_content(self.record.reference_number)
        except Exception as e:
            logger.warning(
                f"Failed to check distressing content for {self.record.id}: {e}"
            )
            return False

    def _should_include_delivery_options(self) -> bool:
        """Determine if delivery options should be fetched."""
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
        """Return empty results structure."""
        return {
            "subjects_enrichment": {},
            "related_records": [],
            "delivery_options": {},
            "distressing_content": False,
        }
