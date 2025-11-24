import unittest
from unittest.mock import MagicMock, patch

from app.lib.api import JSONAPIClient, ResourceNotFound
from django.conf import settings


class DeliveryOptionsApiClientTests(unittest.TestCase):
    def setUp(self):
        self.api_client = JSONAPIClient(settings.DELIVERY_OPTIONS_API_URL)
        self.headers = {"Cache-Control": "no-cache"}

    def tearDown(self):
        self.api_client.params.clear()

    # Mocking requests.get to test get method
    @patch(
        "app.lib.api.get"
    )  # Patch the correct path where requests.get is used
    def test_get_results_success(self, mock_get):
        # Mock response setup
        mock_response = MagicMock()
        mock_response.json.return_value = {"delivery_options": ["abc", "def"]}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Add parameter before calling get_results()
        self.api_client.add_parameter("iaid", "C12345")

        # Call the inherited method
        result = self.api_client.get()

        # Assert the mocked call
        mock_get.assert_called_with(
            f"{settings.DELIVERY_OPTIONS_API_URL}/",
            params={"iaid": "C12345"},
            headers=self.headers,
            timeout=None,
        )

        # Check the returned data
        self.assertEqual(result, {"delivery_options": ["abc", "def"]})

    @patch("app.lib.api.get")
    def test_get_results_without_iaid(self, mock_get):
        # Mock API response when no IAID is passed
        mock_response = MagicMock()
        mock_response.json.return_value = {"error": "Missing IAID"}
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # self.api_client = DeliveryOptionsAPI()

        with self.assertRaises(ResourceNotFound) as context:
            self.api_client.get()

        # Assert the exception message
        self.assertEqual(str(context.exception), "Resource not found")

        # Ensure correct request call
        mock_get.assert_called_with(
            f"{settings.DELIVERY_OPTIONS_API_URL}/",
            params={},
            headers=self.headers,
            timeout=None,
        )

    @patch("app.lib.api.get")
    def test_get_results_multiple_parameters(self, mock_get):
        # Mock response for multiple parameters
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "success",
            "filters": ["option1", "option2"],
        }
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # The API actually doesn't care about unknown parameters!
        self.api_client.add_parameter("iaid", "C67890")
        self.api_client.add_parameter("category", "books")

        result = self.api_client.get()

        mock_get.assert_called_with(
            f"{settings.DELIVERY_OPTIONS_API_URL}/",
            params={"iaid": "C67890", "category": "books"},
            headers=self.headers,
            timeout=None,
        )

        self.assertEqual(
            result, {"status": "success", "filters": ["option1", "option2"]}
        )
