from unittest.mock import Mock, patch

import responses
from app.deliveryoptions.constants import AvailabilityCondition
from django.conf import settings
from django.test import TestCase


class TestClosedRetainedAvailability(TestCase):
    """
    Tests for availability display on records with ClosedRetainedDeptKnown
    availability condition (CLOSED_RETAINED_REGISTERED_TNA_HELD_ELSEWHERE group).

    These are records that are not held by TNA but appear on the TNA register,
    and are closed and retained by a known government department.
    """

    def _make_closed_retained_rosetta_response(self, record_id, held_by=None):
        """Helper to build a Rosetta API response for a closed/retained record."""
        details = {
            "id": record_id,
            "title": "Test Closed Retained Record",
            "source": "CAT",
            "heldByCount": 1,
            "level": {
                "code": 3
            },  # Sub-sub-fonds — in DELIVERY_OPTIONS_NON_TNA_LEVELS
        }
        if held_by:
            details["heldBy"] = held_by
        return {"data": [{"@template": {"details": details}}]}

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
        mock_availability_group = Mock()
        mock_availability_group.name = (
            "CLOSED_RETAINED_REGISTERED_TNA_HELD_ELSEWHERE"
        )
        mock_get_availability_group.return_value = mock_availability_group

    @responses.activate
    @patch("app.records.enrichment.delivery_options_request_handler")
    @patch("app.records.enrichment.get_availability_group")
    def test_closed_retained_display(
        self, mock_get_availability_group, mock_delivery_handler
    ):
        """
        Test that a CLOSED_RETAINED_REGISTERED_TNA_HELD_ELSEWHERE non-TNA record
        shows the correct online/in-person availability messages and GOV.UK FOI link,
        and does not fall through to the default non-TNA catch-all messages.
        """
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C123456",
            json=self._make_closed_retained_rosetta_response(
                "C123456", held_by="Ministry of Defence"
            ),
            status=200,
        )
        self._setup_closed_retained_mocks(
            mock_get_availability_group, mock_delivery_handler
        )

        response = self.client.get("/catalogue/id/C123456/")

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
