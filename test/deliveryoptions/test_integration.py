import unittest
from unittest.mock import MagicMock, patch

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from app.deliveryoptions.api import delivery_options_request_handler
from app.deliveryoptions.constants import AvailabilityCondition

DOAPI_URL = "https://api.test.com/api/v1"

SURROGATE_LINK_HTML = (
    '<a href="https://test.nationalarchives.gov.uk/document/TEST123">View document</a>'
)


def doapi_response(**overrides):
    """A response in the shape DOAPI actually returns (a single object,
    snake_case) — not the previous service's one-item list."""
    response = {
        "delivery_option": AvailabilityCondition.DigitizedDiscovery,
        "delivery_option_name": "DIGITIZED_DISCOVERY",
        "group": "AVAILABLE_ONLINE_TNA_ONLY",
        "reader_type": "OffSite",
        "flags": {"is_digitised": True},
        "surrogate_links": [
            {
                "url": SURROGATE_LINK_HTML,
                "label": None,
                "type": "DIGITIZED_DISCOVERY",
                "description": None,
                "sort_word": None,
                "id": None,
                "code": None,
            }
        ],
        "advanced_order_url_parameters": None,
        "label": "Available online",
    }
    response.update(overrides)
    return response


def mock_http_response(json_data=None, status_code=200):
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = json_data
    return response


class DeliveryOptionsIntegrationTestCase(unittest.TestCase):
    """Tests for the request handler that fetches delivery options from DOAPI."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.record = MagicMock()
        self.record.id = "C123456"

    @patch("app.lib.api.get")
    @patch("django.conf.settings.DELIVERY_OPTIONS_API_URL", DOAPI_URL)
    def test_delivery_options_request_handler(self, mock_get):
        """Test the API request handler that fetches delivery options data."""
        mock_get.return_value = mock_http_response(doapi_response())

        # Call the function under test
        api_result = delivery_options_request_handler(self.record.id)

        # DOAPI's response comes back exactly as received — no reshaping
        self.assertEqual(api_result, doapi_response())

        # The iaid goes in the path, the key in a header, and no reader type
        # (or any other parameter) is sent: DOAPI determines that itself.
        mock_get.assert_called_once()
        called_args = mock_get.call_args
        self.assertEqual(
            called_args[0][0],
            "https://api.test.com/api/v1/delivery-options/rosetta/C123456",
        )
        self.assertEqual(called_args[1]["params"], {})
        self.assertEqual(
            called_args[1]["headers"]["X-API-Key"], settings.DELIVERY_OPTIONS_API_KEY
        )

    @patch("django.conf.settings.DELIVERY_OPTIONS_API_URL", None)
    def test_delivery_options_api_url_not_set(self):
        """Test that an exception is raised when DELIVERY_OPTIONS_API_URL is not set."""
        with self.assertRaises(ImproperlyConfigured) as context:
            delivery_options_request_handler("C123456")

        self.assertIn("DELIVERY_OPTIONS_API_URL not set", str(context.exception))


class DeliveryOptionsAdditionalTests(unittest.TestCase):
    """Additional unit tests for delivery options request handler."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.record = MagicMock()
        self.record.id = "C123456"

    @patch("app.lib.api.get")
    @patch("django.conf.settings.DELIVERY_OPTIONS_API_URL", DOAPI_URL)
    def test_empty_api_response(self, mock_get):
        """Test handling of an empty API response."""
        # Setup mock response with an empty list
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        # Instead of expecting ValueError
        with self.assertRaises(Exception) as context:
            delivery_options_request_handler(self.record.id)
        # Check for the actual error message
        self.assertEqual(
            "Delivery Options database is currently unavailable",
            str(context.exception),
        )

    @patch("app.lib.api.get")
    @patch("django.conf.settings.DELIVERY_OPTIONS_API_URL", DOAPI_URL)
    def test_malformed_api_response(self, mock_get):
        """Test handling of an API response with missing required keys."""
        mock_get.return_value = mock_http_response({"invalid_key": "value"})

        with self.assertRaises(Exception) as context:
            delivery_options_request_handler(self.record.id)
        self.assertEqual(
            "Delivery Options database is currently unavailable",
            str(context.exception),
        )

    @patch("app.lib.api.get")
    @patch("django.conf.settings.DELIVERY_OPTIONS_API_URL", DOAPI_URL)
    def test_previous_services_list_shape_is_rejected(self, mock_get):
        """If the URL were ever pointed back at the previous service (a
        list), that must fail loudly rather than be half-understood."""
        mock_get.return_value = mock_http_response(
            [{"options": 3, "surrogateLinks": [], "advancedOrderUrlParameters": None}]
        )

        with self.assertRaises(Exception) as context:
            delivery_options_request_handler(self.record.id)
        self.assertEqual(
            "Delivery Options database is currently unavailable",
            str(context.exception),
        )

    @patch("app.lib.api.get")
    @patch("django.conf.settings.DELIVERY_OPTIONS_API_URL", DOAPI_URL)
    def test_not_found_returns_none(self, mock_get):
        """A 404 means this record has no delivery options — normal, not an
        error."""
        mock_get.return_value = mock_http_response(status_code=404)

        self.assertIsNone(delivery_options_request_handler(self.record.id))

    @patch("app.lib.api.get")
    @patch("django.conf.settings.DELIVERY_OPTIONS_API_URL", DOAPI_URL)
    def test_other_failures_raise_the_generic_unavailable_error(self, mock_get):
        """DOAPI's 401 (bad key), 422 (unsupported level), 429 (rate limited)
        and 503 (its upstreams down) are not told apart by JSONAPIClient —
        they all surface as the same generic failure."""
        for status_code in (401, 422, 429, 503):
            with self.subTest(status_code=status_code):
                mock_get.return_value = mock_http_response(status_code=status_code)
                with self.assertRaises(Exception) as context:
                    delivery_options_request_handler(self.record.id)
                self.assertEqual(
                    "Delivery Options database is currently unavailable",
                    str(context.exception),
                )

    @patch("django.conf.settings.DELIVERY_OPTIONS_API_KEY", "")
    @patch("django.conf.settings.DELIVERY_OPTIONS_API_URL", DOAPI_URL)
    def test_api_key_not_set(self):
        """Without a key every call would be rejected by DOAPI as a bare
        422/401 — fail clearly on our side instead."""
        with self.assertRaises(ImproperlyConfigured) as context:
            delivery_options_request_handler(self.record.id)

        self.assertIn("DELIVERY_OPTIONS_API_KEY not set", str(context.exception))

    @patch("app.lib.api.get")
    @patch("django.conf.settings.DELIVERY_OPTIONS_API_URL", DOAPI_URL + "/")
    def test_trailing_slash_in_api_url_does_not_double_up(self, mock_get):
        mock_get.return_value = mock_http_response(doapi_response())

        delivery_options_request_handler(self.record.id)

        self.assertEqual(
            mock_get.call_args[0][0],
            "https://api.test.com/api/v1/delivery-options/rosetta/C123456",
        )

    @patch("app.lib.api.get")
    @patch("django.conf.settings.DELIVERY_OPTIONS_API_URL", DOAPI_URL)
    def test_iaid_is_url_quoted_into_the_path(self, mock_get):
        mock_get.return_value = mock_http_response(doapi_response())

        delivery_options_request_handler("C1/../cache/C1")

        self.assertEqual(
            mock_get.call_args[0][0],
            "https://api.test.com/api/v1/delivery-options/rosetta/C1%2F..%2Fcache%2FC1",
        )

    @patch("app.lib.api.get")
    @patch("django.conf.settings.DELIVERY_OPTIONS_API_URL", DOAPI_URL)
    def test_response_is_returned_untouched(self, mock_get):
        """Every field DOAPI sends reaches the caller as sent: surrogate
        links with all their fields (including nulls), flags, the order
        parameters object, the reader type used — nothing reshaped, dropped
        or renamed."""
        full_response = doapi_response(
            delivery_option=AvailabilityCondition.OrderOriginal,
            delivery_option_name="ORDER_ORIGINAL",
            group="AVAILABLE_IN_PERSON_WITH_COPYING",
            reader_type="StaffIn",
            flags={"is_digitised": False, "is_in_use": True},
            surrogate_links=[
                {
                    "url": SURROGATE_LINK_HTML,
                    "label": "A label",
                    "type": "DIGITIZED_LIA",
                    "description": "A description",
                    "sort_word": "a-sort",
                    "id": "ID1",
                    "code": "CODE1",
                },
                {
                    "url": None,
                    "label": None,
                    "type": None,
                    "description": None,
                    "sort_word": None,
                    "id": None,
                    "code": None,
                },
            ],
            advanced_order_url_parameters={
                "url_params": "requestthis=ADM 1/3&linkback="
            },
            label="Order original",
        )
        mock_get.return_value = mock_http_response(full_response)

        self.assertEqual(
            delivery_options_request_handler(self.record.id), full_response
        )

    @patch("app.lib.api.get")
    @patch("django.conf.settings.DELIVERY_OPTIONS_API_URL", DOAPI_URL)
    def test_condition_zero_is_a_valid_response(self, mock_get):
        """InvigilationSafeRoom is 0 — falsy, but a real condition, not a
        missing one."""
        mock_get.return_value = mock_http_response(
            doapi_response(delivery_option=AvailabilityCondition.InvigilationSafeRoom)
        )

        result = delivery_options_request_handler(self.record.id)

        self.assertEqual(result["delivery_option"], 0)
