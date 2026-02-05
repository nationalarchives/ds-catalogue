import logging

from app.main.global_alert import fetch_global_alert_api_data
from app.records.api import record_details_by_id
from app.records.models import Record
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Cache timeout for record data (in seconds)
RECORD_CACHE_TIMEOUT = 60


class RecordContextMixin:
    """Mixin for adding record to view context."""

    def get_record(self) -> Record:
        """Fetch the record by ID, using cache if available."""
        if not hasattr(self, "_record"):
            record_id = self.kwargs["id"]
            cache_key = f"ds-catalogue:record:{record_id}"

            # Try to get from cache first
            self._record = cache.get(cache_key)

            if self._record is None:
                # Not in cache, fetch from API
                self._record = record_details_by_id(id=record_id)
                # Cache for subsequent requests (enrichment endpoints)
                cache.set(cache_key, self._record, timeout=RECORD_CACHE_TIMEOUT)

        return self._record

    def get_context_data(self, **kwargs):
        """Add record to context."""
        context = super().get_context_data(**kwargs)
        context["record"] = self.get_record()
        return context


class GlobalAlertsMixin:
    """Mixin for adding global alerts to context."""

    def get_global_alerts(self) -> dict:
        """Fetch global alerts and mourning notices from Wagtail."""
        return fetch_global_alert_api_data()

    def get_context_data(self, **kwargs):
        """Add global alerts to context."""
        context = super().get_context_data(**kwargs)
        context["global_alert"] = self.get_global_alerts()
        return context
