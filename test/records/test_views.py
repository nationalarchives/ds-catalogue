import responses
from app.records.models import Record
from django.conf import settings
from django.test import TestCase


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
        self.assertContains(response, 'href="/catalogue/search/?subjects=Army"')
        self.assertContains(
            response, 'href="/catalogue/search/?subjects=Europe%20and%20Russia"'
        )
        self.assertContains(
            response, 'href="/catalogue/search/?subjects=Conflict"'
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
            response, 'href="/catalogue/search/?subjects=Sex%20and%20gender"'
        )
        self.assertContains(
            response,
            'href="/catalogue/search/?subjects=Art%2C%20architecture%20and%20design"',
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
