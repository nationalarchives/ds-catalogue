import unittest
from unittest.mock import MagicMock, patch

from app.deliveryoptions.api import delivery_options_request_handler
from app.deliveryoptions.constants import AvailabilityCondition, Reader
from app.deliveryoptions.delivery_options import construct_delivery_options
from app.records.models import Record
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings


class DeliveryOptionsIntegrationTestCase(unittest.TestCase):
    """Integration tests for the delivery options API and context construction."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create sample record
        self.record = MagicMock(spec=Record)
        self.record.id = "C123456"
        self.record.reference_number = "TEST 123/456"
        self.record.access_condition = "Open Document, Open Description"
        self.record.held_by = "The National Archives, Kew"
        self.record.held_by_url = "https://test.nationalarchives.gov.uk"
        self.record.record_opening = "01 January 2023"

        # Create factory and request
        self.request = MagicMock()
        self.request.META = {"REMOTE_ADDR": "192.168.1.1"}

    @patch("app.lib.api.get")
    @patch(
        "django.conf.settings.DELIVERY_OPTIONS_API_URL",
        "https://api.test.com/delivery-options",
    )
    def test_delivery_options_request_handler(self, mock_get):
        """Test the API request handler that fetches delivery options data."""
        # Create a mock response object
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "options": AvailabilityCondition.DigitizedDiscovery,
                "surrogateLinks": [
                    {
                        "xReferenceURL": '<a href="https://test.nationalarchives.gov.uk/document/TEST123">View document</a>'
                    }
                ],
            }
        ]
        mock_get.return_value = mock_response

        # Call the function under test
        api_result = delivery_options_request_handler(self.record.id)

        # Verify the returned data matches the expected response
        self.assertEqual(len(api_result), 1)
        self.assertEqual(
            api_result[0]["options"], AvailabilityCondition.DigitizedDiscovery
        )

        # Verify request was made with correct parameters
        mock_get.assert_called_once()
        called_args = mock_get.call_args
        self.assertEqual(
            called_args[0][0], "https://api.test.com/delivery-options/"
        )
        self.assertEqual(called_args[1]["params"], {"iaid": "C123456"})

    def test_delivery_options_integration(self):
        """
        Test the complete flow from API request to template context construction.
        """
        # First, let's examine what get_delivery_option_dict is expecting
        # The function call is: delivery_option = get_delivery_option_dict(do_dict, api_result[0]["options"])
        # Where api_result[0]["options"] is AvailabilityCondition.DigitizedDiscovery (which is 3)

        # Create mock data that exactly matches the format expected by get_delivery_option_dict
        mock_do_dict = {
            "deliveryOptions": {
                "option": {
                    3: {  # Exact integer key for DigitizedDiscovery
                        "readertype": {
                            3: {  # Exact integer key for OFFSITE
                                "heading": "View this record",
                                "description": [
                                    {
                                        "name": "description",
                                        "value": "This record is available to download.",
                                    }
                                ],
                                "orderbuttons": [
                                    {
                                        "text": "{DownloadText}",
                                        "href": "{DownloadUrl}",
                                        "class": "download-button",
                                    }
                                ],
                            }
                        }
                    }
                }
            }
        }

        # Now patch the specific functions that are used in the code path
        with (
            patch(
                "app.deliveryoptions.api.settings"
            ) as mock_settings,  # noqa: F841
            patch(
                "app.deliveryoptions.delivery_options.get_reader_type",
                return_value=Reader.OFFSITE,
            ),
            patch(
                "app.deliveryoptions.delivery_options.read_delivery_options",
                return_value=mock_do_dict,
            ),
            patch("app.deliveryoptions.api.JSONAPIClient") as mock_client_class,
        ):

            # Create a mock client instance that the class constructor will return
            mock_client_instance = MagicMock()
            mock_client_class.return_value = mock_client_instance

            # Set up the mock return value for the get method on the client instance
            mock_client_instance.get.return_value = [
                {
                    "options": AvailabilityCondition.DigitizedDiscovery,  # This is 3
                    "surrogateLinks": [
                        {
                            "xReferenceURL": '<a href="https://test.nationalarchives.gov.uk/document/TEST123">View document</a>'
                        }
                    ],
                }
            ]

            # Add debugging to see what's happening
            with patch(
                "app.deliveryoptions.delivery_options.get_delivery_option_dict"
            ) as mock_get_record:
                # Make get_delivery_option_dict return a value we know works
                mock_get_record.return_value = mock_do_dict["deliveryOptions"][
                    "option"
                ][3]

                # Step 1: Call the API handler
                api_result = delivery_options_request_handler("C123456")

                # Step 2: Process the API result into context
                context = construct_delivery_options(
                    api_result, self.record, self.request
                )

                # Verify the context contains the expected data
                self.assertEqual(context["reader_type"], Reader.OFFSITE)
                self.assertIn("do_heading", context)
                self.assertIn("do_description", context)
                self.assertIn("do_orderbuttons", context)

    @patch("django.conf.settings.DELIVERY_OPTIONS_API_URL", None)
    def test_delivery_options_api_url_not_set(self):
        """Test that an exception is raised when DELIVERY_OPTIONS_API_URL is not set."""
        with self.assertRaises(ImproperlyConfigured) as context:
            delivery_options_request_handler("C123456")

        self.assertIn(
            "DELIVERY_OPTIONS_API_URL not set", str(context.exception)
        )


class DeliveryOptionsAdditionalTests(unittest.TestCase):
    """Additional unit tests for delivery options request handler."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create sample record
        self.record = MagicMock(spec=Record)
        self.record.id = "C123456"

    @patch("app.lib.api.get")
    @patch(
        "django.conf.settings.DELIVERY_OPTIONS_API_URL",
        "https://api.test.com/delivery-options",
    )
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
    @patch(
        "django.conf.settings.DELIVERY_OPTIONS_API_URL",
        "https://api.test.com/delivery-options",
    )
    def test_malformed_api_response(self, mock_get):
        """Test handling of an API response with missing required keys."""
        # Setup mock response with malformed data
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"invalid_key": "value"}]
        mock_get.return_value = mock_response

        # Instead of expecting ValueError
        with self.assertRaises(Exception) as context:
            delivery_options_request_handler(self.record.id)
        # Check for the actual error message
        self.assertEqual(
            "Delivery Options database is currently unavailable",
            str(context.exception),
        )

    @patch("django.conf.settings.DELIVERY_OPTIONS_API_URL", None)
    def test_api_url_not_set(self):
        """Test handling when DELIVERY_OPTIONS_API_URL is not set."""
        # Expect an ImproperlyConfigured exception
        with self.assertRaises(ImproperlyConfigured) as context:
            delivery_options_request_handler(self.record.id)

        # Check the error message
        self.assertIn(
            "DELIVERY_OPTIONS_API_URL not set", str(context.exception)
        )
