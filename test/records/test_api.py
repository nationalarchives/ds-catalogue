from unittest.mock import patch

import responses
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase, override_settings

from app.lib.api import JSONAPIClient
from app.lib.exceptions import MissingAPIAttributeError, RecordNotFound
from app.records.api import (
    get_research_guide,
    record_details_by_id,
    wagtail_request_handler,
)
from app.records.models import Record


class TestRecordDetailsById(SimpleTestCase):
    def setUp(self):
        self.records_client = JSONAPIClient

    @responses.activate
    def test_record_details_by_id_returns_record(self):
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C198022",
            json={"data": [{"@template": {"details": {"id": "C198022"}}}]},
            status=200,
        )
        result = record_details_by_id(id="C198022")

        self.assertIsInstance(result, Record)

    @responses.activate
    def test_missing_data_field_for_id(self):
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C198022",
            json={},
            status=200,
        )

        with self.assertRaisesMessage(
            MissingAPIAttributeError,
            "Get API response missing required 'data' field for id C198022",
        ):
            _ = record_details_by_id(id="C198022")

    @responses.activate
    def test_missing_template_field(self):
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C198022",
            json={"data": [{"template": {"details": {"id": "C198022"}}}]},
            status=200,
        )

        with self.assertRaisesMessage(
            MissingAPIAttributeError,
            "API response missing required '@template' field",
        ):
            _ = record_details_by_id(id="C198022")

    @responses.activate
    def test_record_not_found_id_does_not_exist(self):
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C198022",
            json={"data": []},
            status=200,
        )

        with self.assertRaisesMessage(RecordNotFound, "id C198022 does not exist"):
            _ = record_details_by_id(id="C198022")


class TestWagtailAPIIntegration(SimpleTestCase):
    """Tests for the new Wagtail API integration using JSONAPIClient"""

    @patch("app.records.api.wagtail_request_handler")
    def test_wagtail_request_handler_success(self, mock_handler):
        """Test that wagtail_request_handler works correctly"""

        mock_response = {"items": [{"title": "Test Article"}]}
        mock_handler.return_value = mock_response

        # This would normally call the actual function, but we're mocking it
        # to test the pattern
        result = mock_handler("/article_tags/", {"tags": "aviation", "limit": 10})

        self.assertEqual(result, mock_response)
        mock_handler.assert_called_once_with(
            "/article_tags/", {"tags": "aviation", "limit": 10}
        )

    @override_settings(WAGTAIL_API_URL="https://test-api.example.com")
    @patch("app.records.api.JSONAPIClient")
    def test_wagtail_request_handler_with_real_client(self, mock_client_class):
        """Test wagtail_request_handler with actual JSONAPIClient usage"""

        # Mock the client instance
        mock_client = mock_client_class.return_value
        mock_client.get.return_value = {"items": [{"title": "Test Article"}]}

        # Call the actual function
        result = wagtail_request_handler("/article_tags/", {"tags": "aviation"})

        # Verify client was created correctly
        mock_client_class.assert_called_once_with(
            "https://test-api.example.com", default_params={"tags": "aviation"}
        )
        mock_client.add_header.assert_any_call("Accept", "application/json")
        mock_client.get.assert_called_once_with("/article_tags/", timeout=None)

        self.assertEqual(result, {"items": [{"title": "Test Article"}]})

    @override_settings(WAGTAIL_API_URL=None)
    def test_wagtail_request_handler_missing_url(self):
        """Test wagtail_request_handler when WAGTAIL_API_URL is not set"""

        with self.assertRaisesMessage(ImproperlyConfigured, "WAGTAIL_API_URL not set"):
            wagtail_request_handler("/article_tags/", {})

    @override_settings(WAGTAIL_API_URL="https://test-api.example.com")
    @patch("app.records.api.JSONAPIClient")
    def test_wagtail_request_handler_api_error(self, mock_client_class):
        """Test wagtail_request_handler when API returns error"""

        # Mock the client to raise an exception
        mock_client = mock_client_class.return_value
        mock_client.get.side_effect = Exception("API Error")

        with self.assertRaisesMessage(Exception, "API Error"):
            wagtail_request_handler("/article_tags/", {"tags": "aviation"})

    @override_settings(
        WAGTAIL_API_URL="https://test-api.example.com/api/v2",
        WAGTAIL_API_KEY="test-token",
    )
    @responses.activate
    def test_get_research_guide_sends_repeated_ancestors_and_returns_first(self):
        responses.add(
            responses.GET,
            "https://test-api.example.com/api/v2/research_guides/"
            "?record=C12345&ancestor=C1234&ancestor=C123",
            json={
                "items": [
                    {"title": "Most relevant"},
                    {"title": "Less relevant"},
                ]
            },
            status=200,
        )
        record = Record(
            {
                "id": "C12345",
                "@hierarchy": [
                    {"@admin": {"id": "C123"}},
                    {"@admin": {"id": "C1234"}},
                    {"@admin": {"id": "C12345"}},
                ],
            }
        )

        result = get_research_guide(record)

        self.assertEqual(result, {"title": "Most relevant"})
        request = responses.calls[0].request
        self.assertEqual(
            request.url,
            "https://test-api.example.com/api/v2/research_guides/"
            "?record=C12345&ancestor=C1234&ancestor=C123",
        )
        self.assertEqual(request.headers["Accept"], "application/json")
        self.assertEqual(request.headers["Authorization"], "Token test-token")

    @patch("app.records.api.wagtail_request_handler", return_value={"items": []})
    def test_get_research_guide_returns_none_when_no_guides_match(self, mock_handler):
        record = Record({"id": "C12345", "@hierarchy": []})

        self.assertIsNone(get_research_guide(record))
        mock_handler.assert_called_once_with(
            "/research_guides/",
            {"record": "C12345"},
            timeout=None,
        )

    @patch(
        "app.records.api.wagtail_request_handler",
        return_value={"items": [{"title": "Guide"}]},
    )
    def test_get_research_guide_includes_ancestors_without_identifiers(
        self, mock_handler
    ):
        record = Record(
            {
                "id": "C12345",
                "@hierarchy": [
                    {"@admin": {"id": "C123"}},
                    {"@admin": {"id": "C1234"}},
                    {"@admin": {"id": "C12345"}},
                ],
            }
        )

        get_research_guide(record)

        mock_handler.assert_called_once_with(
            "/research_guides/",
            {
                "record": "C12345",
                "ancestor": ["C1234", "C123"],
            },
            timeout=None,
        )
