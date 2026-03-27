from unittest.mock import Mock, patch

import responses
from app.deliveryoptions.constants import AvailabilityCondition
from app.records.models import Record
from django.conf import settings
from django.test import RequestFactory, TestCase


def _make_record(details: dict) -> Record:
    """Helper to build a Record instance directly from a details dict."""
    return Record(details)


class TestRecordView(TestCase):

    def setUp(self):
        """Clear cache before each test."""
        from django.core.cache import cache

        cache.clear()

    @patch("app.records.mixins.record_details_by_id")
    def test_record_detail_view_for_catalogue_record(self, mock_record_details):
        mock_record_details.return_value = _make_record(
            {
                "id": "C999999",
                "title": "Test Title",
                "source": "CAT",
                "heldByCount": 100,
            }
        )

        response = self.client.get("/catalogue/id/C999999/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.view_name, "records:details")
        self.assertTemplateUsed("records/record_detail.html")
        self.assertIsInstance(response.context_data.get("record"), Record)

    @patch("app.records.mixins.record_details_by_id")
    def test_record_detail_view_for_archive_record(self, mock_record_details):
        mock_record_details.return_value = _make_record(
            {
                "id": "A13530600",
                "title": "Test Title",
                "source": "ARCHON",
            }
        )

        response = self.client.get("/catalogue/id/A13530600/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.view_name, "records:details")
        self.assertTemplateUsed("records/archon_detail.html")
        self.assertIsInstance(response.context_data.get("record"), Record)


class TestSubjectLinks(TestCase):
    """Tests for clickable subject lozenges linking to search"""

    def setUp(self):
        """Set up common test data"""
        from django.core.cache import cache

        cache.clear()

        self.sample_record_details = {
            "id": "C999999",
            "referenceNumber": "ADM 363/540/126",
            "title": "Test Record with Subjects",
            "summaryTitle": "Test Record",
            "source": "CAT",
            "heldByCount": 100,
            "subjects": [
                "Army",
                "Europe and Russia",
                "Conflict",
                "Diaries",
                "Armed Forces (General Administration)",
            ],
        }

    @patch("app.records.mixins.record_details_by_id")
    def test_subject_lozenges_are_clickable_links(self, mock_record_details):
        """Test that subjects are rendered as clickable links to search"""
        mock_record_details.return_value = _make_record(
            self.sample_record_details
        )

        response = self.client.get("/catalogue/id/C999999/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/catalogue/search/?subject=Army"')
        self.assertContains(
            response, 'href="/catalogue/search/?subject=Europe%20and%20Russia"'
        )
        self.assertContains(
            response, 'href="/catalogue/search/?subject=Conflict"'
        )

    @patch("app.records.mixins.record_details_by_id")
    def test_subject_links_are_url_encoded(self, mock_record_details):
        """Test that subject names with special characters are properly encoded"""
        mock_record_details.return_value = _make_record(
            {
                "id": "C789012",
                "source": "CAT",
                "heldByCount": 100,
                "subjects": [
                    "Sex and gender",
                    "Art, architecture and design",
                ],
            }
        )

        response = self.client.get("/catalogue/id/C789012/")

        self.assertContains(
            response, 'href="/catalogue/search/?subject=Sex%20and%20gender"'
        )
        self.assertContains(
            response,
            'href="/catalogue/search/?subject=Art%2C%20architecture%20and%20design"',
        )

    @patch("app.records.mixins.record_details_by_id")
    def test_subject_links_have_correct_css_class(self, mock_record_details):
        """Test that subject links maintain the correct CSS class"""
        mock_record_details.return_value = _make_record(
            self.sample_record_details
        )

        response = self.client.get("/catalogue/id/C999999/")

        self.assertContains(response, 'class="tna-dl-chips__item"')
        self.assertContains(response, '<dl class="tna-dl-chips">')
        self.assertContains(response, "<dt>Topics</dt>")

    @patch("app.records.mixins.record_details_by_id")
    def test_record_with_no_subjects_shows_no_subject_section(
        self, mock_record_details
    ):
        """Test that records without subjects don't show subject section"""
        mock_record_details.return_value = _make_record(
            {
                "id": "C456789",
                "source": "CAT",
                "heldByCount": 100,
                "subjects": [],
            }
        )

        response = self.client.get("/catalogue/id/C456789/")

        self.assertNotContains(response, "<dt>Topics</dt>")
        self.assertNotContains(response, 'class="tna-dl-chips"')

    @patch("app.records.mixins.record_details_by_id")
    def test_subject_links_are_not_placeholders(self, mock_record_details):
        """Test that subject links are real URLs, not placeholder # links"""
        mock_record_details.return_value = _make_record(
            self.sample_record_details
        )

        response = self.client.get("/catalogue/id/C999999/")
        html = response.content.decode()

        subject_count = html.count('class="tna-dl-chips__item"')
        self.assertEqual(subject_count, 5)

        if '<dl class="tna-dl-chips">' in html:
            subjects_section_start = html.find('<dl class="tna-dl-chips">')
            subjects_section_end = html.find("</dl>", subjects_section_start)
            subjects_section = html[subjects_section_start:subjects_section_end]
            self.assertNotIn('href="#"', subjects_section)


class DoAvailabilityGroupTestCase(TestCase):
    """Tests for delivery options functionality"""

    def setUp(self):
        self.factory = RequestFactory()

    @patch("app.records.enrichment.delivery_options_request_handler")
    @patch("app.records.enrichment.get_availability_group")
    def test_do_availability_group_present_when_found(
        self, mock_get_availability_group, mock_delivery_handler
    ):
        """Test that do_availability_group is included when get_availability_group returns a value."""
        from app.records.enrichment import RecordEnrichmentHelper

        mock_delivery_handler.return_value = [
            {
                "options": AvailabilityCondition.DigitizedDiscovery.value,
                "surrogateLinks": [],
                "advancedOrderUrlParameters": "",
            }
        ]

        mock_availability_group = Mock()
        mock_availability_group.name = "AVAILABLE_ONLINE_TNA_ONLY"
        mock_get_availability_group.return_value = mock_availability_group

        mock_record = Mock()
        mock_record.id = "TEST123"

        helper = RecordEnrichmentHelper(mock_record)
        context = helper._get_delivery_api_data()

        self.assertIn("delivery_option", context)
        self.assertEqual(context["delivery_option"], "DigitizedDiscovery")
        self.assertIn("do_availability_group", context)
        self.assertEqual(
            context["do_availability_group"], "AVAILABLE_ONLINE_TNA_ONLY"
        )

    @patch("app.records.enrichment.delivery_options_request_handler")
    @patch("app.records.enrichment.get_availability_group")
    def test_do_availability_group_absent_when_not_found(
        self, mock_get_availability_group, mock_delivery_handler
    ):
        """Test that do_availability_group is excluded when get_availability_group returns None."""
        from app.records.enrichment import RecordEnrichmentHelper

        mock_delivery_handler.return_value = [
            {
                "options": AvailabilityCondition.OrderException.value,
                "surrogateLinks": [],
                "advancedOrderUrlParameters": "",
            }
        ]

        mock_get_availability_group.return_value = None

        mock_record = Mock()
        mock_record.id = "TEST123"

        helper = RecordEnrichmentHelper(mock_record)
        context = helper._get_delivery_api_data()

        self.assertIn("delivery_option", context)
        self.assertEqual(context["delivery_option"], "OrderException")
        self.assertNotIn("do_availability_group", context)

    @patch("app.records.enrichment.delivery_options_request_handler")
    def test_get_delivery_options_handles_errors_gracefully(
        self, mock_delivery_handler
    ):
        """Test that errors are handled gracefully."""
        from app.records.enrichment import RecordEnrichmentHelper

        test_cases = [
            (Exception("API Error"), "API exception", {}),
            ([{"no_options_key": "value"}], "Missing options key", True),
            ([], "Empty response", True),
            (None, "None response", True),
            ([{"options": 999999}], "Invalid enum value", True),
        ]

        for mock_response, description, *has_temp in test_cases:
            expect_temp_context = has_temp[0] if has_temp else False

            with self.subTest(description=description):
                if isinstance(mock_response, Exception):
                    mock_delivery_handler.side_effect = mock_response
                else:
                    mock_delivery_handler.return_value = mock_response
                    mock_delivery_handler.side_effect = None

                mock_record = Mock()
                mock_record.id = "TEST123"

                helper = RecordEnrichmentHelper(mock_record)
                context = helper.fetch_delivery_options()

                self.assertNotIn("delivery_option", context)
                self.assertNotIn("do_availability_group", context)

                if expect_temp_context:
                    self.assertIn("delivery_options_heading", context)
                    self.assertIn("delivery_instructions", context)
                    self.assertIn("tna_discovery_link", context)
                else:
                    self.assertEqual(context, {})


class TestNonTNARecordAvailability(TestCase):
    """Tests for availability display on records held by other archives."""

    def setUp(self):
        from django.core.cache import cache

        cache.clear()

    @patch("app.records.mixins.record_details_by_id")
    def test_non_tna_record_shows_availability_boxes(self, mock_record_details):
        """Test that non-TNA records show the availability boxes."""
        mock_record_details.return_value = _make_record(
            {
                "id": "C999999",
                "title": "Test Record at Other Archive",
                "source": "CAT",
                "level": "Item",
                "heldBy": "British Library",
                "heldById": "A13530841",
            }
        )

        response = self.client.get("/catalogue/id/C999999/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Is it available online?")
        self.assertContains(response, "Can I see it in person?")
        self.assertContains(
            response,
            "Maybe, but not on The National Archives website. This record is held at British Library.",
        )
        self.assertContains(
            response,
            "Not at The National Archives, but you may be able to view it in person at British Library.",
        )
        self.assertNotContains(response, "Access information is unavailable")

    @patch("app.records.mixins.record_details_by_id")
    def test_non_tna_record_shows_held_by_url_link(self, mock_record_details):
        """Test that non-TNA records show 'How to view it' link when held_by_url is available."""
        mock_record_details.return_value = _make_record(
            {
                "id": "C999999",
                "title": "Test Record at Other Archive",
                "source": "CAT",
                "level": "Item",
                "heldBy": "British Library",
                "heldById": "A13530841",
            }
        )

        response = self.client.get("/catalogue/id/C999999/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<a href="https://discovery.nationalarchives.gov.uk/details/a/A13530841">How to view it</a>',
        )

    @patch("app.records.mixins.record_details_by_id")
    def test_non_tna_record_without_held_by_url_no_link(
        self, mock_record_details
    ):
        """Test that non-TNA records without held_by_url don't show 'How to view it' link."""
        mock_record_details.return_value = _make_record(
            {
                "id": "C999999",
                "title": "Test Record at Other Archive",
                "source": "CAT",
                "level": "Item",
                "heldBy": "Some Other Archive",
                # No heldById means no held_by_url
            }
        )

        response = self.client.get("/catalogue/id/C999999/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Is it available online?")
        self.assertContains(response, "Can I see it in person?")
        self.assertContains(response, "Some Other Archive")
        self.assertNotContains(response, ">How to view it</a>")
