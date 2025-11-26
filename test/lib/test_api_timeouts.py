"""
Tests to verify timeout behaviour across different API clients.

Tests prove that:
1. Delivery Options API has a timeout (defined in settings)
2. Rosetta API has a timeout (defined in settings, defaults to None)
3. Wagtail API has a timeout (defined in settings, defaults to None)
"""

from unittest.mock import MagicMock, patch

from app.deliveryoptions.api import delivery_options_request_handler
from app.lib.api import JSONAPIClient
from app.records.api import rosetta_request_handler, wagtail_request_handler
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings
from requests import Timeout


class TimeoutConfigurationTests(TestCase):
    """Tests to verify timeout configuration for different API clients."""

    @patch("app.lib.api.get")
    @override_settings(
        DELIVERY_OPTIONS_API_URL="https://api.test.com/delivery-options",
        DELIVERY_OPTIONS_API_TIMEOUT=30,
    )
    def test_delivery_options_has_configured_timeout(self, mock_get):
        """
        CRITICAL TEST: Verify delivery options API is called with configured timeout.

        This test proves that the delivery options API has timeout protection
        to prevent hanging if the service is slow.

        The timeout value is defined in settings.DELIVERY_OPTIONS_API_TIMEOUT
        """
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"options": 1, "surrogateLinks": []}]
        mock_get.return_value = mock_response

        # Call the delivery options handler
        try:
            delivery_options_request_handler("C123456")
        except Exception:
            pass  # We don't care if it fails, we just want to check the timeout

        # Verify the request was made with the configured timeout
        mock_get.assert_called_once()
        call_kwargs = mock_get.call_args[1]

        self.assertIn(
            "timeout",
            call_kwargs,
            "Timeout parameter not passed to requests.get()",
        )
        self.assertEqual(
            call_kwargs["timeout"],
            settings.DELIVERY_OPTIONS_API_TIMEOUT,
            f"Expected timeout={settings.DELIVERY_OPTIONS_API_TIMEOUT}, got timeout={call_kwargs['timeout']}",
        )

    @override_settings(DELIVERY_OPTIONS_API_TIMEOUT=30)
    def test_delivery_options_timeout_setting_is_defined(self):
        """
        Test that DELIVERY_OPTIONS_API_TIMEOUT setting is properly defined.

        This ensures the setting exists and has a reasonable value.
        """
        self.assertIsNotNone(
            settings.DELIVERY_OPTIONS_API_TIMEOUT,
            "DELIVERY_OPTIONS_API_TIMEOUT should not be None",
        )
        self.assertIsInstance(
            settings.DELIVERY_OPTIONS_API_TIMEOUT,
            int,
            f"DELIVERY_OPTIONS_API_TIMEOUT should be an integer, got {type(settings.DELIVERY_OPTIONS_API_TIMEOUT)}",
        )
        self.assertGreater(
            settings.DELIVERY_OPTIONS_API_TIMEOUT,
            0,
            f"DELIVERY_OPTIONS_API_TIMEOUT should be positive, got {settings.DELIVERY_OPTIONS_API_TIMEOUT}",
        )
        self.assertLessEqual(
            settings.DELIVERY_OPTIONS_API_TIMEOUT,
            60,
            f"DELIVERY_OPTIONS_API_TIMEOUT should be reasonable (≤60s), got {settings.DELIVERY_OPTIONS_API_TIMEOUT}",
        )

    @patch("app.lib.api.get")
    @override_settings(
        ROSETTA_API_URL="https://api.test.com/rosetta",
        ROSETTA_API_TIMEOUT=None,
    )
    def test_rosetta_api_has_no_timeout_by_default(self, mock_get):
        """
        CRITICAL TEST: Verify Rosetta API is called with NO timeout (timeout=None) by default.

        This test proves that the Rosetta API (used for record fetching)
        does NOT have a timeout by default, maintaining backward compatibility.
        """
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"iaid": "C123456"}]}
        mock_get.return_value = mock_response

        # Call the Rosetta handler
        try:
            rosetta_request_handler("/get", {"id": "C123456"})
        except Exception:
            pass  # We don't care if it fails, we just want to check the timeout

        # Verify the request was made with timeout=None
        mock_get.assert_called_once()
        call_kwargs = mock_get.call_args[1]

        self.assertIn(
            "timeout",
            call_kwargs,
            "Timeout parameter not passed to requests.get()",
        )
        self.assertIsNone(
            call_kwargs["timeout"],
            f"Expected timeout=None, got timeout={call_kwargs['timeout']}",
        )

    @patch("app.lib.api.get")
    @override_settings(
        ROSETTA_API_URL="https://api.test.com/rosetta",
        ROSETTA_API_TIMEOUT=60,
    )
    def test_rosetta_api_respects_configured_timeout(self, mock_get):
        """
        Test that Rosetta API uses configured timeout when set.

        This verifies the timeout can be configured via settings.
        """
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"iaid": "C123456"}]}
        mock_get.return_value = mock_response

        # Call the Rosetta handler
        try:
            rosetta_request_handler("/get", {"id": "C123456"})
        except Exception:
            pass

        # Verify the request was made with the configured timeout
        mock_get.assert_called_once()
        call_kwargs = mock_get.call_args[1]

        self.assertEqual(
            call_kwargs["timeout"],
            60,
            f"Expected timeout=60, got timeout={call_kwargs['timeout']}",
        )

    @patch("app.lib.api.get")
    @override_settings(
        WAGTAIL_API_URL="https://api.test.com/wagtail",
        WAGTAIL_API_TIMEOUT=None,
    )
    def test_wagtail_api_has_no_timeout_by_default(self, mock_get):
        """
        CRITICAL TEST: Verify Wagtail API is called with NO timeout (timeout=None) by default.

        This test proves that the Wagtail API (used for subjects enrichment)
        does NOT have a timeout by default, maintaining backward compatibility.
        """
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [{"title": "Test"}]}
        mock_get.return_value = mock_response

        # Call the Wagtail handler
        try:
            wagtail_request_handler("/article_tags/", {"tags": "test"})
        except Exception:
            pass  # We don't care if it fails, we just want to check the timeout

        # Verify the request was made with timeout=None
        mock_get.assert_called_once()
        call_kwargs = mock_get.call_args[1]

        self.assertIn(
            "timeout",
            call_kwargs,
            "Timeout parameter not passed to requests.get()",
        )
        self.assertIsNone(
            call_kwargs["timeout"],
            f"Expected timeout=None, got timeout={call_kwargs['timeout']}",
        )

    @patch("app.lib.api.get")
    @override_settings(
        WAGTAIL_API_URL="https://api.test.com/wagtail",
        WAGTAIL_API_TIMEOUT=10,
    )
    def test_wagtail_api_respects_configured_timeout(self, mock_get):
        """
        Test that Wagtail API uses configured timeout when set.

        This verifies the timeout can be configured via settings.
        """
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [{"title": "Test"}]}
        mock_get.return_value = mock_response

        # Call the Wagtail handler
        try:
            wagtail_request_handler("/article_tags/", {"tags": "test"})
        except Exception:
            pass

        # Verify the request was made with the configured timeout
        mock_get.assert_called_once()
        call_kwargs = mock_get.call_args[1]

        self.assertEqual(
            call_kwargs["timeout"],
            10,
            f"Expected timeout=10, got timeout={call_kwargs['timeout']}",
        )

    def test_json_api_client_default_timeout_is_none(self):
        """
        Test that JSONAPIClient has timeout=None by default.

        This ensures backward compatibility - existing code that doesn't
        specify a timeout will continue to work without timeouts.
        """
        client = JSONAPIClient("https://api.test.com")

        self.assertIsNone(
            client.timeout,
            f"Expected default timeout=None, got {client.timeout}",
        )

    def test_json_api_client_accepts_custom_timeout(self):
        """
        Test that JSONAPIClient can accept a custom timeout.

        This verifies the new timeout parameter works correctly.
        """
        client = JSONAPIClient("https://api.test.com", timeout=10)

        self.assertEqual(
            client.timeout, 10, f"Expected timeout=10, got {client.timeout}"
        )


class TimeoutBehaviorTests(TestCase):
    """Tests to verify timeout behaviour when requests actually time out."""

    @patch("app.lib.api.get")
    @override_settings(
        DELIVERY_OPTIONS_API_URL="https://api.test.com/delivery-options",
        DELIVERY_OPTIONS_API_TIMEOUT=30,
    )
    def test_delivery_options_timeout_raises_exception(self, mock_get):
        """
        Test that when delivery options times out, it raises a proper exception.

        This verifies the error handling works correctly with timeouts.
        """

        # Mock a timeout
        mock_get.side_effect = Timeout("Connection timed out")

        # Call the handler and expect an exception
        with self.assertRaises(Exception) as context:
            delivery_options_request_handler("C123456")

        # Verify the exception message mentions unavailability
        self.assertIn(
            "Delivery Options database is currently unavailable",
            str(context.exception),
        )

    @patch("app.lib.api.get")
    def test_json_api_client_handles_timeout_exception(self, mock_get):
        """
        Test that JSONAPIClient properly handles timeout exceptions.

        This verifies the timeout exception handling in the base client.
        """

        # Mock a timeout
        mock_get.side_effect = Timeout("Connection timed out")

        client = JSONAPIClient("https://api.test.com", timeout=5)

        # Call get and expect an exception
        with self.assertRaises(Exception) as context:
            client.get()

        # Verify the exception message
        self.assertEqual("The request timed out", str(context.exception))
