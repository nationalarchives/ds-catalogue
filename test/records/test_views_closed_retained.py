from unittest.mock import Mock, patch

from app.deliveryoptions.constants import AvailabilityCondition
from app.records.models import Record
from django.test import TestCase


def _make_record(details: dict) -> Record:
    """Helper to build a Record instance directly from a details dict."""
    return Record(details)


class TestClosedRetainedAvailability(TestCase):
    """
    Tests for availability display on records with ClosedRetainedDeptKnown
    availability condition (CLOSED_RETAINED_REGISTERED_TNA_HELD_ELSEWHERE group).

    These are records that are not held by TNA but appear on the TNA register,
    and are closed and retained by a known government department.
    """

    def setUp(self):
        from django.core.cache import cache

        cache.clear()

    def _make_closed_retained_record(self, held_by=None):
        """Helper to build a Record for a closed/retained record."""
        details = {
            "id": "C999999",
            "title": "Test Closed Retained Record",
            "source": "CAT",
            "heldByCount": 1,
            "level": {
                "code": 3
            },  # Sub-sub-fonds — in DELIVERY_OPTIONS_NON_TNA_LEVELS
        }
        if held_by:
            details["heldBy"] = held_by
        return _make_record(details)

    def _setup_closed_retained_mocks(
        self, mock_get_availability_group, mock_delivery_handler
    ):
        """Configure mocks for a ClosedRetainedDeptKnown record."""
        mock_delivery_handler.return_value = [
            {
                "options": AvailabilityCondition.ClosedRetainedDeptKnown.value,
                "surrogateLinks": [],
                "advancedOrderUrlParameters": "",
            }
        ]
        mock_get_availability_group.return_value.name = (
            "CLOSED_RETAINED_REGISTERED_TNA_HELD_ELSEWHERE"
        )

    @patch("app.records.mixins.record_details_by_id")
    @patch("app.records.enrichment.get_subjects_enrichment", return_value={})
    @patch(
        "app.records.enrichment.get_related_records_by_series", return_value=[]
    )
    @patch(
        "app.records.enrichment.get_tna_related_records_by_subjects",
        return_value=[],
    )
    @patch("app.records.enrichment.has_distressing_content", return_value=False)
    @patch("app.records.enrichment.delivery_options_request_handler")
    @patch("app.records.enrichment.get_availability_group")
    @patch("app.records.views.fetch_global_notifications", return_value={})
    def test_closed_retained_display(
        self,
        mock_notifications,
        mock_get_availability_group,
        mock_delivery_handler,
        mock_distressing,
        mock_related_by_subjects,
        mock_related_by_series,
        mock_subjects,
        mock_record_details,
    ):
        """
        Test that a CLOSED_RETAINED_REGISTERED_TNA_HELD_ELSEWHERE non-TNA record
        shows the correct online/in-person availability messages and GOV.UK FOI link,
        and does not fall through to the default non-TNA catch-all messages.
        """
        mock_record_details.return_value = self._make_closed_retained_record(
            held_by="Ministry of Defence"
        )
        self._setup_closed_retained_mocks(
            mock_get_availability_group, mock_delivery_handler
        )

        response = self.client.get("/catalogue/id/C999999/")

        self.assertEqual(response.status_code, 200)
        # Online availability
        self.assertContains(response, "Is it available online?")
        self.assertContains(
            response,
            "Not on The National Archives website. This record is held at Creating government department or its successor.",
        )
        # In-person availability
        self.assertContains(response, "Can I see it in person?")
        self.assertContains(
            response,
            "Not at The National Archives. This record is closed and retained by Ministry of Defence.",
        )
        # FOI link
        self.assertContains(
            response,
            'href="https://www.gov.uk/make-a-freedom-of-information-request"',
        )
        self.assertContains(response, "Visit GOV.UK for more information")
        # Confirm the default non-TNA catch-all messages are not rendered
        self.assertNotContains(
            response,
            "Maybe, but not on The National Archives website.",
        )
        self.assertNotContains(
            response,
            "Not at The National Archives, but you may be able to view it in person",
        )
