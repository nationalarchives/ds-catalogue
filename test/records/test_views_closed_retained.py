from unittest.mock import Mock, patch

import responses
from app.deliveryoptions.constants import AvailabilityCondition
from django.conf import settings
from django.test import TestCase


class TestClosedRetainedAvailability(TestCase):
    """
    Tests for availability display on records with ClosedRetainedDeptKnown
    availability condition (CLOSED_RETAINED group).

    These are records that are not held by TNA but appear on the TNA register,
    and are closed and retained by a known government department.
    """

    def _make_rosetta_response(self, record_id, held_by=None, held_by_id=None):
        """Helper to build a Rosetta API response for a non-TNA closed/retained record."""
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
        if held_by_id:
            details["heldById"] = held_by_id
        return {"data": [{"@template": {"details": details}}]}

    @responses.activate
    @patch("app.records.enrichment.delivery_options_request_handler")
    @patch("app.records.enrichment.get_availability_group")
    def test_closed_retained_online_availability_message(
        self, mock_get_availability_group, mock_delivery_handler
    ):
        """
        Test that a CLOSED_RETAINED non-TNA record shows the correct
        'Is it available online?' message.
        """
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C123456",
            json=self._make_rosetta_response(
                "C123456", held_by="Ministry of Defence"
            ),
            status=200,
        )

        mock_delivery_handler.return_value = [
            {
                "options": AvailabilityCondition.ClosedRetainedDeptKnown.value,
                "surrogateLinks": [],
                "advancedOrderUrlParameters": "",
            }
        ]

        mock_availability_group = Mock()
        mock_availability_group.name = "CLOSED_RETAINED"
        mock_get_availability_group.return_value = mock_availability_group

        response = self.client.get("/catalogue/id/C123456/")

        print("mock called:", mock_get_availability_group.called)
        print("mock call count:", mock_get_availability_group.call_count)
        print("delivery handler called:", mock_delivery_handler.called)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Is it available online?")
        self.assertContains(
            response,
            "Not on The National Archives website. This record is held at Creating government department or its successor.",
        )

    @responses.activate
    @patch("app.records.enrichment.delivery_options_request_handler")
    @patch("app.records.enrichment.get_availability_group")
    def test_closed_retained_in_person_availability_message(
        self, mock_get_availability_group, mock_delivery_handler
    ):
        """
        Test that a CLOSED_RETAINED non-TNA record shows the correct
        'Can I see it in person?' message, including the held_by name.
        """
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C123456",
            json=self._make_rosetta_response(
                "C123456", held_by="Ministry of Defence"
            ),
            status=200,
        )

        mock_delivery_handler.return_value = [
            {
                "options": AvailabilityCondition.ClosedRetainedDeptKnown.value,
                "surrogateLinks": [],
                "advancedOrderUrlParameters": "",
            }
        ]

        mock_availability_group = Mock()
        mock_availability_group.name = "CLOSED_RETAINED"
        mock_get_availability_group.return_value = mock_availability_group

        response = self.client.get("/catalogue/id/C123456/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Can I see it in person?")
        self.assertContains(
            response,
            "Not at The National Archives. This record is closed and retained by Ministry of Defence.",
        )

    @responses.activate
    @patch("app.records.enrichment.delivery_options_request_handler")
    @patch("app.records.enrichment.get_availability_group")
    def test_closed_retained_shows_foi_link(
        self, mock_get_availability_group, mock_delivery_handler
    ):
        """
        Test that a CLOSED_RETAINED non-TNA record shows the GOV.UK FOI link
        in the 'Can I see it in person?' box.
        """
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C123456",
            json=self._make_rosetta_response(
                "C123456", held_by="Ministry of Defence"
            ),
            status=200,
        )

        mock_delivery_handler.return_value = [
            {
                "options": AvailabilityCondition.ClosedRetainedDeptKnown.value,
                "surrogateLinks": [],
                "advancedOrderUrlParameters": "",
            }
        ]

        mock_availability_group = Mock()
        mock_availability_group.name = "CLOSED_RETAINED"
        mock_get_availability_group.return_value = mock_availability_group

        response = self.client.get("/catalogue/id/C123456/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'href="https://www.gov.uk/make-a-freedom-of-information-request"',
        )
        self.assertContains(response, "Visit GOV.UK for more information")

    @responses.activate
    @patch("app.records.enrichment.delivery_options_request_handler")
    @patch("app.records.enrichment.get_availability_group")
    def test_closed_retained_does_not_show_non_tna_default_messages(
        self, mock_get_availability_group, mock_delivery_handler
    ):
        """
        Test that a CLOSED_RETAINED record does not fall through to the
        default non-TNA messages ('Maybe, but not on The National Archives website').
        """
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C123456",
            json=self._make_rosetta_response(
                "C123456", held_by="Ministry of Defence"
            ),
            status=200,
        )

        mock_delivery_handler.return_value = [
            {
                "options": AvailabilityCondition.ClosedRetainedDeptKnown.value,
                "surrogateLinks": [],
                "advancedOrderUrlParameters": "",
            }
        ]

        mock_availability_group = Mock()
        mock_availability_group.name = "CLOSED_RETAINED"
        mock_get_availability_group.return_value = mock_availability_group

        response = self.client.get("/catalogue/id/C123456/")

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            "Maybe, but not on The National Archives website.",
        )
        self.assertNotContains(
            response,
            "Not at The National Archives, but you may be able to view it in person",
        )
