import logging

from app.main.global_alert import fetch_global_alert_api_data
from app.records.api import record_details_by_id
from app.records.models import Record

logger = logging.getLogger(__name__)


class RecordContextMixin:
    """Mixin for adding record to view context."""

    def get_record(self) -> Record:
        """Fetch the record by ID from URL kwargs."""
        if not hasattr(self, "_record"):
            self._record = record_details_by_id(id=self.kwargs["id"])
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
