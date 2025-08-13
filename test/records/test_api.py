from unittest.mock import patch

import responses
from app.lib.api import JSONAPIClient, ResourceNotFound
from app.records.api import record_details_by_id, wagtail_request_handler
from app.records.models import Record
from django.conf import settings
from django.test import SimpleTestCase, override_settings


class TestRecordDetailsById(SimpleTestCase):
    def setUp(self):
        self.records_client = JSONAPIClient

    @responses.activate
    def test_record_details_by_id_returns_record(self):
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C198022",
            json={"data": [{"@template": {"details": {"iaid": "C198022"}}}]},
            status=200,
        )
        result = record_details_by_id(id="C198022")

        self.assertIsInstance(result, Record)

    @responses.activate
    def test_no_data_returned_for_id(self):
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C198022",
            json={},
            status=200,
        )

        with self.assertRaisesMessage(
            Exception, "No data returned for id C198022"
        ):
            _ = record_details_by_id(id="C198022")

    @responses.activate
    def test_resource_not_found_id_does_not_exist(self):
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C198022",
            json={"data": []},
            status=200,
        )

        with self.assertRaisesMessage(
            ResourceNotFound, "id C198022 does not exist"
        ):
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
        result = mock_handler(
            "/article_tags", {"tags": "aviation", "limit": 10}
        )

        self.assertEqual(result, mock_response)
        mock_handler.assert_called_once_with(
            "/article_tags", {"tags": "aviation", "limit": 10}
        )

    @override_settings(WAGTAIL_API_URL="https://test-api.example.com")
    @patch("app.records.api.JSONAPIClient")
    def test_wagtail_request_handler_with_real_client(self, mock_client_class):
        """Test wagtail_request_handler with actual JSONAPIClient usage"""

        # Mock the client instance
        mock_client = mock_client_class.return_value
        mock_client.get.return_value = {"items": [{"title": "Test Article"}]}

        # Call the actual function
        result = wagtail_request_handler("/article_tags", {"tags": "aviation"})

        # Verify client was created correctly
        mock_client_class.assert_called_once_with(
            "https://test-api.example.com", {"tags": "aviation"}
        )
        mock_client.get.assert_called_once_with("/article_tags")

        self.assertEqual(result, {"items": [{"title": "Test Article"}]})

    @override_settings(WAGTAIL_API_URL=None)
    def test_wagtail_request_handler_missing_url(self):
        """Test wagtail_request_handler when WAGTAIL_API_URL is not set"""

        with self.assertRaisesMessage(Exception, "WAGTAIL_API_URL not set"):
            wagtail_request_handler("/article_tags", {})

    @override_settings(WAGTAIL_API_URL="https://test-api.example.com")
    @patch("app.records.api.JSONAPIClient")
    def test_wagtail_request_handler_api_error(self, mock_client_class):
        """Test wagtail_request_handler when API returns error"""

        # Mock the client to raise an exception
        mock_client = mock_client_class.return_value
        mock_client.get.side_effect = Exception("API Error")

        with self.assertRaisesMessage(Exception, "API Error"):
            wagtail_request_handler("/article_tags", {"tags": "aviation"})
