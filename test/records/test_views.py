from unittest.mock import Mock, patch

import responses
from django.conf import settings
from django.test import TestCase

from app.records.models import Record


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
                                "description": {
                                    "raw": "<contacts><addressline1><![CDATA[Kew]]></addressline1></contacts>"
                                },
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
        self.assertContains(response, 'href="/catalogue/search/?subject=Conflict"')

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

        # Check that links have the tags component class
        self.assertContains(response, 'class="tna-tags__link"')
        # Ensure subjects are wrapped in the tags component structure
        self.assertContains(response, '<ul class="tna-tags tna-tags--small"')

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
        self.assertNotContains(response, 'class="tna-tags__link"')

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
        subject_count = html.count('class="tna-tags__link"')
        self.assertEqual(subject_count, 5)

        # Extract subjects section and verify no placeholder links
        if '<ul class="tna-tags tna-tags--small"' in html:
            subjects_section_start = html.find('<ul class="tna-tags tna-tags--small"')
            subjects_section_end = html.find("</ul>", subjects_section_start)
            subjects_section = html[subjects_section_start:subjects_section_end]

            # Should not contain href="#" in subjects section
            self.assertNotIn('href="#"', subjects_section)


class FetchDeliveryOptionsTestCase(TestCase):
    """The enrichment helper hands DOAPI's response on exactly as received;
    anything unusable becomes an empty dict, never an exception."""

    @patch("app.records.enrichment.delivery_options_request_handler")
    def test_handles_errors_gracefully(self, mock_delivery_handler):
        from app.records.enrichment import RecordEnrichmentHelper

        test_cases = [
            (Exception("API Error"), "API exception"),
            (None, "No delivery options (404)"),
            ({}, "Empty response"),
        ]

        for mock_response, description in test_cases:
            with self.subTest(description=description):
                if isinstance(mock_response, Exception):
                    mock_delivery_handler.side_effect = mock_response
                else:
                    mock_delivery_handler.return_value = mock_response
                    mock_delivery_handler.side_effect = None

                mock_record = Mock()
                mock_record.id = "TEST123"

                context = RecordEnrichmentHelper(mock_record)._fetch_delivery_options()

                self.assertEqual(context, {})


class TestNonTNARecordAvailability(TestCase):
    """Tests for availability display on records held by other archives."""

    @responses.activate
    def test_non_tna_record_shows_availability_boxes(self):
        """Test that non-TNA records show the consolidated 'View options' box."""
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C123456",
            json={
                "data": [
                    {
                        "@template": {
                            "details": {
                                "id": "C123456",
                                "title": "Test Record at Other Archive",
                                "source": "CAT",
                                "level": "Item",
                                "heldBy": "British Library",
                                "heldById": "A13530841",
                            }
                        }
                    }
                ]
            },
            status=200,
        )

        response = self.client.get("/catalogue/id/C123456/")

        self.assertEqual(response.status_code, 200)

        # Should show the consolidated "View options" box
        self.assertContains(response, "View options")

        # Should show the correct message for non-TNA records
        self.assertContains(
            response,
            "This record is held at British Library. You may be able to view it in person or online.",
        )

        # Should NOT show the "Access information is unavailable" message
        self.assertNotContains(response, "Access information is unavailable")

    @responses.activate
    def test_non_tna_record_shows_held_by_url_link(self):
        """Test that non-TNA records show 'How to view it' link when held_by_url is available."""
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C123456",
            json={
                "data": [
                    {
                        "@template": {
                            "details": {
                                "id": "C123456",
                                "title": "Test Record at Other Archive",
                                "source": "CAT",
                                "level": "Item",
                                "heldBy": "British Library",
                                "heldById": "A13530841",
                            }
                        }
                    }
                ]
            },
            status=200,
        )

        response = self.client.get("/catalogue/id/C123456/")

        self.assertEqual(response.status_code, 200)

        # Should contain the "How to view it" link pointing to the archive
        self.assertContains(
            response,
            '<a href="/catalogue/id/A13530841/">How to view it</a>',
        )

    @responses.activate
    def test_non_tna_record_without_held_by_url_no_link(self):
        """Test that non-TNA records without held_by_url don't show 'How to view it' link."""
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C123456",
            json={
                "data": [
                    {
                        "@template": {
                            "details": {
                                "id": "C123456",
                                "title": "Test Record at Other Archive",
                                "source": "CAT",
                                "level": "Item",
                                "heldBy": "Some Other Archive",
                                # No heldById means no held_by_url
                            }
                        }
                    }
                ]
            },
            status=200,
        )

        response = self.client.get("/catalogue/id/C123456/")

        self.assertEqual(response.status_code, 200)

        # Should show the consolidated "View options" box
        self.assertContains(response, "View options")

        # Should show the archive name
        self.assertContains(response, "Some Other Archive")

        # Should NOT contain "How to view it" link in the availability boxes
        # (We check for the specific pattern in the availability message)
        self.assertNotContains(response, ">How to view it</a>")
