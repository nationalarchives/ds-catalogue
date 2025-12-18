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

class ProgressiveLoadMixin:
    """
    Mixin to support progressive page loading.

    For initial page loads, always enables progressive mode (returns minimal data).
    JavaScript will then load secondary content asynchronously.
    For users without JavaScript, the <noscript> tags in templates provide full content.

    No cookies or server-side JS detection needed - graceful degradation is handled
    entirely in the template layer.
    """

    def is_progressive_load_request(self) -> bool:
        """
        Determine if this is a progressive load initial request.

        Returns:
            True for initial page loads (progressive mode - minimal data),
            False for AJAX fragment requests (which need full data)
        """
        # AJAX fragment requests should get full data
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return False

        # All initial page loads are progressive (JS will load secondary content)
        # No-JS users will see noscript fallbacks in the template
        return True

    def get_context_data(self, **kwargs):
        """Add progressive loading flag to context."""
        context = super().get_context_data(**kwargs)
        context["progressive_mode"] = self.is_progressive_load_request()
        return context
