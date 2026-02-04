from unittest.mock import Mock, patch

import responses
from app.deliveryoptions.constants import AvailabilityCondition
from app.records.models import Record
from django.conf import settings
from django.test import RequestFactory, TestCase


class TestRecordView(TestCase):

    def setUp(self):
        """Clear cache before each test."""
        from django.core.cache import cache

        cache.clear()

    @responses.activate
    def test_record_detail_view_for_catalogue_record(self):

        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C123456",
            json={
                "data": [
                    {
                        "@template": {
                            "details": {
                                "id": "C123456",
                                "title": "Test Title",
                                "source": "CAT",
                                "heldByCount": 100,
                            }
                        }
                    }
                ]
            },
            status=200,
        )

        response = self.client.get("/catalogue/id/C123456/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.view_name, "records:details")
        self.assertTemplateUsed("records/record_detail.html")

        self.assertIsInstance(response.context_data.get("record"), Record)

    @responses.activate
    def test_record_detail_view_for_archive_record(self):

        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=A13530600",
            json={
                "data": [
                    {
                        "@template": {
                            "details": {
                                "id": "A13530600",
                                "title": "Test Title",
                                "source": "ARCHON",
                            }
                        }
                    }
                ]
            },
            status=200,
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
        # Clear cache to ensure fresh API calls
        from django.core.cache import cache

        cache.clear()

        self.sample_record_response = {
            "data": [
                {
                    "@template": {
                        "details": {
                            "id": "C123456",
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
                    }
                }
            ]
        }

    @responses.activate
    def test_subject_lozenges_are_clickable_links(self):
        """Test that subjects are rendered as clickable links to search"""
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C123456",
            json=self.sample_record_response,
            status=200,
        )

        response = self.client.get("/catalogue/id/C123456/")

        self.assertEqual(response.status_code, 200)

        # Check that subject links exist (using %20 for spaces, not +)
        self.assertContains(response, 'href="/catalogue/search/?subject=Army"')
        self.assertContains(
            response, 'href="/catalogue/search/?subject=Europe%20and%20Russia"'
        )
        self.assertContains(
            response, 'href="/catalogue/search/?subject=Conflict"'
        )

    @responses.activate
    def test_subject_links_are_url_encoded(self):
        """Test that subject names with special characters are properly encoded"""
        record_with_special_chars = {
            "data": [
                {
                    "@template": {
                        "details": {
                            "id": "C789012",
                            "source": "CAT",
                            "heldByCount": 100,
                            "subjects": [
                                "Sex and gender",
                                "Art, architecture and design",
                            ],
                        }
                    }
                }
            ]
        }

        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C789012",
            json=record_with_special_chars,
            status=200,
        )

        response = self.client.get("/catalogue/id/C789012/")

        # Check that spaces and special characters are encoded
        # urlencode uses %20 for spaces, not +
        self.assertContains(
            response, 'href="/catalogue/search/?subject=Sex%20and%20gender"'
        )
        self.assertContains(
            response,
            'href="/catalogue/search/?subject=Art%2C%20architecture%20and%20design"',
        )

    @responses.activate
    def test_subject_links_have_correct_css_class(self):
        """Test that subject links maintain the correct CSS class"""
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C123456",
            json=self.sample_record_response,
            status=200,
        )

        response = self.client.get("/catalogue/id/C123456/")

        # Check that links have the lozenge class
        self.assertContains(response, 'class="tna-dl-chips__item"')
        # Ensure subjects are wrapped in proper structure
        self.assertContains(response, '<dl class="tna-dl-chips">')
        self.assertContains(response, "<dt>Topics</dt>")

    @responses.activate
    def test_record_with_no_subjects_shows_no_subject_section(self):
        """Test that records without subjects don't show subject section"""
        record_without_subjects = {
            "data": [
                {
                    "@template": {
                        "details": {
                            "id": "C456789",
                            "source": "CAT",
                            "heldByCount": 100,
                            "subjects": [],
                        }
                    }
                }
            ]
        }

        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C456789",
            json=record_without_subjects,
            status=200,
        )

        response = self.client.get("/catalogue/id/C456789/")

        # Should not show subjects section if no subjects
        self.assertNotContains(response, "<dt>Topics</dt>")
        self.assertNotContains(response, 'class="tna-dl-chips"')

    @responses.activate
    def test_subject_links_are_not_placeholders(self):
        """Test that subject links are real URLs, not placeholder # links"""
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C123456",
            json=self.sample_record_response,
            status=200,
        )

        response = self.client.get("/catalogue/id/C123456/")
        html = response.content.decode()

        # Count actual subject links (should be 5 based on sample data)
        subject_count = html.count('class="tna-dl-chips__item"')
        self.assertEqual(subject_count, 5)

        # Extract subjects section and verify no placeholder links
        if '<dl class="tna-dl-chips">' in html:
            subjects_section_start = html.find('<dl class="tna-dl-chips">')
            subjects_section_end = html.find("</dl>", subjects_section_start)
            subjects_section = html[subjects_section_start:subjects_section_end]

            # Should not contain href="#" in subjects section
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

        # Use DigitizedDiscovery which is in AVAILABLE_ONLINE_TNA_ONLY group
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

        # Use OrderException
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

        # Test various error conditions
        test_cases = [
            # API exceptions - caught by outer try/except, returns {}
            (Exception("API Error"), "API exception", {}),
            # API returns bad data - handled by _get_delivery_api_data, returns {}, but temp context added
            ([{"no_options_key": "value"}], "Missing options key", True),
            ([], "Empty response", True),
            (None, "None response", True),
            ([{"options": 999999}], "Invalid enum value", True),
        ]

        for mock_response, description, *has_temp in test_cases:
            # has_temp will be [True] or [] depending on if it was provided
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
                context = helper._fetch_delivery_options()

                # Should NOT get API-specific keys
                self.assertNotIn("delivery_option", context)
                self.assertNotIn("do_availability_group", context)

                if expect_temp_context:
                    # When API returns bad data (not exception), temp context is still added
                    self.assertIn("delivery_options_heading", context)
                    self.assertIn("delivery_instructions", context)
                    self.assertIn("tna_discovery_link", context)
                else:
                    # When API raises exception, returns completely empty dict
                    self.assertEqual(context, {})
