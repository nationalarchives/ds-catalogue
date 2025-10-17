from unittest.mock import Mock, patch

import responses
from app.deliveryoptions.constants import AvailabilityCondition
from app.records.models import Record
from app.records.views import _get_delivery_options_context
from django.conf import settings
from django.template.response import TemplateResponse
from django.test import RequestFactory, TestCase


class TestRecordView(TestCase):

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
                                "iaid": "C123456",
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
                                "iaid": "A13530600",
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
        self.sample_record_response = {
            "data": [
                {
                    "@template": {
                        "details": {
                            "iaid": "C123456",
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
                            "iaid": "C789012",
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
                            "iaid": "C456789",
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

    def test_do_availability_group_present_when_found(self):
        """Test that do_availability_group is included when get_availability_group returns a value."""
        # Use DigitizedDiscovery which is in AVAILABLE_ONLINE_TNA_ONLY group
        mock_delivery_response = [
            {
                "options": AvailabilityCondition.DigitizedDiscovery.value,
                "surrogateLinks": [],
                "advancedOrderUrlParameters": "",
            }
        ]

        mock_availability_group = Mock()
        mock_availability_group.name = "AVAILABLE_ONLINE_TNA_ONLY"

        with (
            patch(
                "app.records.views.delivery_options_request_handler",
                return_value=mock_delivery_response,
            ),
            patch(
                "app.records.views.get_availability_group",
                return_value=mock_availability_group,
            ),
        ):

            context = _get_delivery_options_context("TEST123")

            self.assertIn("delivery_option", context)
            self.assertEqual(context["delivery_option"], "DigitizedDiscovery")
            self.assertIn("do_availability_group", context)
            self.assertEqual(
                context["do_availability_group"], "AVAILABLE_ONLINE_TNA_ONLY"
            )

    def test_do_availability_group_absent_when_not_found(self):
        """Test that do_availability_group is excluded when get_availability_group returns None."""
        # Use OrderException which is in REDUNDANT_OR_IRRELEVANT group
        mock_delivery_response = [
            {
                "options": AvailabilityCondition.OrderException.value,
                "surrogateLinks": [],
                "advancedOrderUrlParameters": "",
            }
        ]

        with (
            patch(
                "app.records.views.delivery_options_request_handler",
                return_value=mock_delivery_response,
            ),
            patch(
                "app.records.views.get_availability_group", return_value=None
            ),
        ):

            context = _get_delivery_options_context("TEST123")

            self.assertIn("delivery_option", context)
            self.assertEqual(context["delivery_option"], "OrderException")
            self.assertNotIn("do_availability_group", context)

    def test_get_delivery_options_handles_errors_gracefully(self):
        """Test that errors return empty dict without crashing."""
        # Test various error conditions
        test_cases = [
            (Exception("API Error"), "API exception"),
            ([{"no_options_key": "value"}], "Missing options key"),
            ([], "Empty response"),
            (None, "None response"),
            (
                [{"options": 999999}],
                "Invalid enum value",
            ),  # Invalid AvailabilityCondition value
        ]

        for mock_response, description in test_cases:
            with self.subTest(description=description):
                if isinstance(mock_response, Exception):
                    with patch(
                        "app.records.views.delivery_options_request_handler",
                        side_effect=mock_response,
                    ):
                        context = _get_delivery_options_context("TEST123")
                else:
                    with patch(
                        "app.records.views.delivery_options_request_handler",
                        return_value=mock_response,
                    ):
                        context = _get_delivery_options_context("TEST123")

                self.assertEqual(context, {})
                self.assertNotIn("do_availability_group", context)
