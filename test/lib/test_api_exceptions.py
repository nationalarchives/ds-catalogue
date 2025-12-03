import unittest.mock as mock

import responses
from app.lib.api import JSONAPIClient, ResourceNotFound, rosetta_request_handler
from django.conf import settings
from django.test import SimpleTestCase, override_settings
from requests import Timeout, TooManyRedirects


class TestRosettaRequestHandlerException(SimpleTestCase):

    @override_settings(
        ROSETTA_API_URL="",
    )
    @responses.activate
    def test_config_api_url_not_set(self):

        with self.assertRaisesMessage(Exception, "ROSETTA_API_URL not set"):
            _ = rosetta_request_handler(uri="somevalue", params={})


class TestJSONAPIClientExceptionsGetRequest(SimpleTestCase):
    def setUp(self):
        self.records_client = JSONAPIClient

    @responses.activate
    def test_non_json_with_200(self):
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C123456",
            status=200,  # 200:Ok
            body="",  # no content JSON: Expecting value: line 1 column 1 (char 0)
        )

        with self.assertRaisesMessage(Exception, "Non-JSON response provided"):
            with self.assertLogs("app.lib.api", level="ERROR") as lc:
                _ = rosetta_request_handler(uri="get", params={"id": "C123456"})
        self.assertIn(
            "ERROR:app.lib.api:JSON API provided non-JSON response", lc.output
        )

        with self.assertRaisesMessage(Exception, "Non-JSON response provided"):
            with self.assertLogs("app.lib.api", level="DEBUG") as lc:
                _ = rosetta_request_handler(uri="get", params={"id": "C123456"})
        self.assertIn("DEBUG:app.lib.api:Non-JSON response: ", lc.output)

    @responses.activate
    def test_non_json_with_truncation(self):
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C123456",
            status=200,  # 200:Ok
            body="{ invalid json - "  # malformed JSON
            "This is a test response that is not JSON."
            " It contains more than 100 characters to test the truncation "
            "logic in the logging functionality. "
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        )

        with self.assertRaisesMessage(Exception, "Non-JSON response provided"):
            with self.assertLogs("app.lib.api", level="ERROR") as lc:
                _ = rosetta_request_handler(uri="get", params={"id": "C123456"})
        self.assertIn(
            "ERROR:app.lib.api:JSON API provided non-JSON response", lc.output
        )

        with self.assertRaisesMessage(Exception, "Non-JSON response provided"):
            with self.assertLogs("app.lib.api", level="DEBUG") as lc:
                _ = rosetta_request_handler(uri="get", params={"id": "C123456"})
        self.assertIn(
            "DEBUG:app.lib.api:Non-JSON response: "
            "{ invalid json - This is a test response that is not JSON. "
            "It contains more than 100 characters to t ... [truncated]",
            lc.output,
        )

    @responses.activate
    def test_bad_request_with_400(self):
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C123456",
            status=400,  # 400:Bad request
        )

        with self.assertRaisesMessage(Exception, "Bad request"):
            with self.assertLogs("app.lib.api", level="ERROR") as lc:
                _ = rosetta_request_handler(uri="get", params={"id": "C123456"})
        self.assertIn(
            "ERROR:app.lib.api:Bad request: https://rosetta.test/data/get?id=C123456",
            lc.output,
        )

    @responses.activate
    def test_resource_not_found_with_404(self):
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C123456",
            status=404,  # 404:not found
        )

        with self.assertRaisesMessage(ResourceNotFound, "Resource not found"):
            with self.assertLogs("app.lib.api", level="WARNING") as lc:
                _ = rosetta_request_handler(uri="get", params={"id": "C123456"})
        self.assertIn("WARNING:app.lib.api:Resource not found", lc.output)

    @responses.activate
    def test_request_failed_with_204(self):
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C123456",
            status=204,  # 204:No content
        )

        with self.assertRaisesMessage(Exception, "Request failed"):
            with self.assertLogs("app.lib.api", level="ERROR") as lc:
                _ = rosetta_request_handler(uri="get", params={"id": "C123456"})
        self.assertIn(
            "ERROR:app.lib.api:JSON API responded with 204", lc.output
        )

    @responses.activate
    def test_request_failed_with_500(self):
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C123456",
            status=500,  # 500:Internal Server Error
        )

        with self.assertRaisesMessage(Exception, "Request failed"):
            with self.assertLogs("app.lib.api", level="ERROR") as lc:
                _ = rosetta_request_handler(uri="get", params={"id": "C123456"})
        self.assertIn(
            "ERROR:app.lib.api:JSON API responded with 500", lc.output
        )

    @responses.activate
    def test_connection_error(self):
        responses.add(
            responses.GET,
            # if you attempt to fetch a url which doesn't hit a match, responses will raise a ConnectionError
            "http://this-api-url-does-not-exist/pull?id=C123456",
        )

        with self.assertRaisesMessage(Exception, "A connection error occured"):
            with self.assertLogs("app.lib.api", level="ERROR") as lc:
                _ = rosetta_request_handler(uri="get", params={"id": "C123456"})
        self.assertIn("ERROR:app.lib.api:JSON API connection error", lc.output)

    @mock.patch("requests.get", side_effect=Timeout())
    @responses.activate
    def test_timeout(self, mock_get):
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C123456",
            body=Timeout(),
        )

        with self.assertRaisesMessage(Exception, "The request timed out"):
            with self.assertLogs("app.lib.api", level="ERROR") as lc:
                _ = rosetta_request_handler(uri="get", params={"id": "C123456"})
        self.assertIn("ERROR:app.lib.api:JSON API timeout", lc.output)

    @mock.patch("requests.get", side_effect=TooManyRedirects())
    @responses.activate
    def test_too_many_redirects(self, mock_get):
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C123456",
            body=TooManyRedirects(),
        )

        with self.assertRaisesMessage(Exception, "Too many redirects"):
            with self.assertLogs("app.lib.api", level="ERROR") as lc:
                _ = rosetta_request_handler(uri="get", params={"id": "C123456"})
        self.assertIn(
            "ERROR:app.lib.api:JSON API had too many redirects", lc.output
        )

    @responses.activate
    def test_unknown_json_api_exception(self):
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C123456",
            body=Exception("THIS IS AN UNKNOWN API EXCEPTION"),
        )

        with self.assertRaisesMessage(
            Exception, "THIS IS AN UNKNOWN API EXCEPTION"
        ):
            with self.assertLogs("app.lib.api", level="ERROR") as lc:
                _ = rosetta_request_handler(uri="get", params={"id": "C123456"})
        self.assertIn(
            "ERROR:app.lib.api:Unknown JSON API exception: THIS IS AN UNKNOWN API EXCEPTION",
            lc.output,
        )
