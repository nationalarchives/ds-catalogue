"""
Tests for how DOAPI's delivery options reach the record page.

DOAPI's JSON goes to the templates exactly as received, as
`delivery_options`. These cover the view context, the analytics values
derived from it, and — through a full page render — each branch of the
template that reads it.
"""

from unittest.mock import Mock, patch

import responses
from django.conf import settings
from django.test import RequestFactory, TestCase

from app.deliveryoptions.constants import AvailabilityCondition
from app.records.views import (
    RecordDetailView,
    _delivery_option_name,
    _temporary_delivery_display_context,
)


def doapi_response(delivery_option, group, **overrides):
    """A response in the shape DOAPI returns."""
    response = {
        "delivery_option": int(delivery_option),
        "delivery_option_name": AvailabilityCondition(delivery_option).name.upper(),
        "group": group,
        "reader_type": "OffSite",
        "flags": {"is_digitised": False},
        "surrogate_links": [],
        "advanced_order_url_parameters": None,
        "label": "A label",
    }
    response.update(overrides)
    return response


class TestRecordDetailViewDeliveryOptions(TestCase):
    """Tests for delivery options integration in RecordDetailView."""

    def setUp(self):
        self.factory = RequestFactory()

    def _mock_record(self, **attrs):
        mock_record = Mock()
        mock_record.id = "C123456"
        mock_record.reference_number = "TEST 123"
        mock_record.custom_record_type = "CAT"
        mock_record.subjects = []
        # for a non-TNA record, series level, delivery options are included
        mock_record.is_tna = False
        mock_record.level_code = 3  # Sub-sub-fonds
        mock_record.level = "Series"
        mock_record.hierarchy_series = Mock()
        mock_record.hierarchy_series.reference_number = ""
        mock_record.hierarchy_series.summary_title = ""
        mock_record.summary_title = ""
        for name, value in attrs.items():
            setattr(mock_record, name, value)
        return mock_record

    @patch("app.records.enrichment.has_distressing_content")
    @patch("app.records.enrichment.delivery_options_request_handler")
    @patch("app.records.mixins.record_details_by_id")
    @patch("app.records.views.fetch_global_notifications")
    def test_doapi_response_is_added_to_context_untouched(
        self, mock_notifications, mock_record_details, mock_delivery, mock_distressing
    ):
        """The DOAPI JSON reaches the context exactly as received — no
        reshaping, no flattening into the context's own keys."""
        mock_notifications.return_value = {
            "global_alert": None,
            "mourning_notice": None,
        }
        mock_record_details.return_value = self._mock_record()
        doapi = doapi_response(
            AvailabilityCondition.LocalArchive,
            "RECORDS_AT_OTHER_ARCHIVES",
            surrogate_links=[{"url": "<a href='x'>x</a>", "type": "larchive"}],
            advanced_order_url_parameters={"url_params": "requestthis=A 1/2"},
        )
        mock_delivery.return_value = doapi
        mock_distressing.return_value = False

        response = RecordDetailView.as_view()(self.factory.get("/test/"), id="C123456")

        self.assertEqual(response.context_data["delivery_options"], doapi)
        # DOAPI's own field names must not leak into the context's top level
        # (a flat merge would collide: "delivery_option" is also an int here).
        for key in (
            "delivery_option",
            "group",
            "label",
            "flags",
            "do_availability_group",
        ):
            self.assertNotIn(key, response.context_data)

    @patch("app.records.enrichment.has_distressing_content")
    @patch("app.records.enrichment.delivery_options_request_handler")
    @patch("app.records.mixins.record_details_by_id")
    @patch("app.records.views.fetch_global_notifications")
    def test_temporary_display_context_is_added_alongside(
        self, mock_notifications, mock_record_details, mock_delivery, mock_distressing
    ):
        mock_notifications.return_value = {
            "global_alert": None,
            "mourning_notice": None,
        }
        mock_record_details.return_value = self._mock_record()
        mock_delivery.return_value = doapi_response(
            AvailabilityCondition.OrderOriginal, "AVAILABLE_IN_PERSON_WITH_COPYING"
        )
        mock_distressing.return_value = False

        response = RecordDetailView.as_view()(self.factory.get("/test/"), id="C123456")

        self.assertEqual(
            response.context_data["delivery_options_heading"], "How to order it"
        )
        self.assertEqual(len(response.context_data["delivery_instructions"]), 3)
        self.assertTrue(
            response.context_data["tna_discovery_link"].endswith("/details/r/C123456")
        )
        # and it is NOT mixed into the DOAPI JSON itself
        self.assertNotIn(
            "delivery_options_heading", response.context_data["delivery_options"]
        )

    @patch("app.records.enrichment.has_distressing_content")
    @patch("app.records.enrichment.delivery_options_request_handler")
    @patch("app.records.mixins.record_details_by_id")
    @patch("app.records.views.fetch_global_notifications")
    def test_nothing_is_added_when_there_are_no_delivery_options(
        self, mock_notifications, mock_record_details, mock_delivery, mock_distressing
    ):
        """A 404 from DOAPI (the handler returns None) means no delivery
        options and no temporary panel text either."""
        mock_notifications.return_value = {
            "global_alert": None,
            "mourning_notice": None,
        }
        mock_record_details.return_value = self._mock_record()
        mock_delivery.return_value = None
        mock_distressing.return_value = False

        response = RecordDetailView.as_view()(self.factory.get("/test/"), id="C123456")

        for key in (
            "delivery_options",
            "delivery_options_heading",
            "delivery_instructions",
            "tna_discovery_link",
        ):
            self.assertNotIn(key, response.context_data)

    @patch("app.records.enrichment.has_distressing_content")
    @patch("app.records.enrichment.delivery_options_request_handler")
    @patch("app.records.mixins.record_details_by_id")
    @patch("app.records.views.fetch_global_notifications")
    def test_no_delivery_options_for_archon_records(
        self, mock_notifications, mock_record_details, mock_delivery, mock_distressing
    ):
        """Test that delivery options are not fetched for ARCHON records."""
        mock_notifications.return_value = {
            "global_alert": None,
            "mourning_notice": None,
        }
        mock_record_details.return_value = self._mock_record(
            custom_record_type="ARCHON"
        )
        mock_distressing.return_value = False

        response = RecordDetailView.as_view()(self.factory.get("/test/"), id="C123456")

        # Should not call delivery options handler for ARCHON records
        mock_delivery.assert_not_called()
        self.assertNotIn("delivery_options", response.context_data)

    @patch("app.records.enrichment.has_distressing_content")
    @patch("app.records.mixins.record_details_by_id")
    @patch("app.records.views.fetch_global_notifications")
    def test_distressing_content_flag_added_to_context(
        self, mock_notifications, mock_record_details, mock_distressing
    ):
        """Test that distressing content flag is added to context."""
        mock_notifications.return_value = {
            "global_alert": None,
            "mourning_notice": None,
        }
        mock_record_details.return_value = self._mock_record(
            reference_number="HO 616/123", custom_record_type=None
        )
        mock_distressing.return_value = True

        response = RecordDetailView.as_view()(self.factory.get("/test/"), id="C123456")

        self.assertIn("distressing_content", response.context_data)
        self.assertTrue(response.context_data["distressing_content"])
        mock_distressing.assert_called_once_with("HO 616/123")


class TestDeliveryOptionName(TestCase):
    """The analytics data layer carries the CamelCase AvailabilityCondition
    name, not DOAPI's UPPER_SNAKE delivery_option_name — so its values
    don't change."""

    def test_known_condition(self):
        self.assertEqual(
            _delivery_option_name({"delivery_option": 26}), "OrderOriginal"
        )

    def test_condition_zero_is_not_treated_as_missing(self):
        self.assertEqual(
            _delivery_option_name({"delivery_option": 0}), "InvigilationSafeRoom"
        )

    def test_unrecognised_condition_gives_empty_string(self):
        self.assertEqual(_delivery_option_name({"delivery_option": 999}), "")

    def test_missing_or_null_condition_gives_empty_string(self):
        self.assertEqual(_delivery_option_name({}), "")
        self.assertEqual(_delivery_option_name({"delivery_option": None}), "")

    def test_ignores_doapis_own_name_field(self):
        self.assertEqual(
            _delivery_option_name(
                {"delivery_option": 26, "delivery_option_name": "SOMETHING_ELSE"}
            ),
            "OrderOriginal",
        )


class TestTemporaryDisplayContext(TestCase):
    def test_link_points_at_the_records_discovery_page(self):
        record = Mock()
        record.id = "C999"
        context = _temporary_delivery_display_context(record)
        self.assertTrue(context["tna_discovery_link"].endswith("/details/r/C999"))
        self.assertEqual(context["delivery_options_heading"], "How to order it")


class TestRecordPageRendersDeliveryOptions(TestCase):
    """Full page renders: each branch of record_detail.html that reads
    `delivery_options`."""

    ACCESS_UNAVAILABLE = "Access information is unavailable"
    HOW_TO_ORDER = "How to order it"

    def _tna_piece(self, record_id="C1731303"):
        """A TNA-held Piece, so delivery options are fetched."""
        return {
            "data": [
                {
                    "@template": {
                        "details": {
                            "id": record_id,
                            "referenceNumber": "CO 166/2",
                            "source": "CAT",
                            "groupArray": [{"value": "record"}, {"value": "tna"}],
                            "heldBy": "The National Archives, Kew",
                            "level": {"code": 6, "value": "Piece"},
                            "summaryTitle": "Military and Naval",
                            "@hierarchy": [
                                {
                                    "@admin": {"id": record_id},
                                    "identifier": [{"reference_number": "CO 166/2"}],
                                    "level": {"code": 6},
                                    "source": {"value": "CAT"},
                                    "summary": {"title": "Military and Naval"},
                                }
                            ],
                        }
                    }
                }
            ]
        }

    def _render(self, delivery_response, record_id="C1731303"):
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id={record_id}",
            json=self._tna_piece(record_id),
            status=200,
        )
        with patch(
            "app.records.enrichment.delivery_options_request_handler",
            return_value=delivery_response,
        ):
            response = self.client.get(f"/catalogue/id/{record_id}/")
        self.assertEqual(response.status_code, 200)
        return response

    @responses.activate
    def test_group_drives_the_view_options_box(self):
        response = self._render(
            doapi_response(
                AvailabilityCondition.DigitizedDiscovery, "AVAILABLE_ONLINE_TNA_ONLY"
            )
        )

        self.assertContains(
            response, "This record is available online and can be downloaded."
        )
        self.assertContains(response, self.HOW_TO_ORDER)
        self.assertNotContains(response, self.ACCESS_UNAVAILABLE)

    @responses.activate
    def test_condition_zero_still_shows_the_panel_and_view_options(self):
        """InvigilationSafeRoom is the integer 0, which is falsy. The
        template must test the dict, not delivery_options.delivery_option,
        or this condition would silently lose its panel."""
        response = self._render(
            doapi_response(
                AvailabilityCondition.InvigilationSafeRoom,
                "AVAILABLE_IN_PERSON_WITH_COPYING",
            )
        )

        self.assertContains(
            response, "available to see in person or you can order a copy"
        )
        self.assertContains(response, self.HOW_TO_ORDER)

    @responses.activate
    def test_pending_classification_falls_through_to_access_unavailable(self):
        """PENDING_CLASSIFICATION isn't shown as a view option; for a record
        TNA holds that means the 'unavailable' message — but the panel still
        shows, since there are delivery options."""
        response = self._render(
            doapi_response(
                AvailabilityCondition.DigitizedAvailableButNotDownloadableAtPieceLevel,
                "PENDING_CLASSIFICATION",
            )
        )

        self.assertContains(response, self.ACCESS_UNAVAILABLE)
        self.assertContains(response, self.HOW_TO_ORDER)

    @responses.activate
    def test_no_delivery_options_shows_unavailable_and_no_panel(self):
        response = self._render(None)

        self.assertContains(response, self.ACCESS_UNAVAILABLE)
        self.assertNotContains(response, self.HOW_TO_ORDER)

    @responses.activate
    def test_a_failing_service_does_not_break_the_page(self):
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C1731303",
            json=self._tna_piece(),
            status=200,
        )
        with patch(
            "app.records.enrichment.delivery_options_request_handler",
            side_effect=Exception("Delivery Options database is currently unavailable"),
        ):
            response = self.client.get("/catalogue/id/C1731303/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.ACCESS_UNAVAILABLE)
        self.assertNotContains(response, self.HOW_TO_ORDER)
