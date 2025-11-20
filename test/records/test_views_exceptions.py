from http import HTTPStatus
from test.utils import prevent_request_warnings

import responses
from django.conf import settings
from django.test import TestCase, override_settings


class TestRecordViewExceptions(TestCase):

    @prevent_request_warnings  # suppress test output: Not Found: /catalogue/id//
    def test_no_id_respond_with_404(self):

        response = self.client.get("/catalogue/id//")

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    @prevent_request_warnings  # suppress test output: Not Found: /catalogue/id/C123456/
    @responses.activate
    def test_empty_data_results_responds_with_resource_not_found_404(self):
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C123456",
            json={"data": []},
            status=200,
        )

        response = self.client.get("/catalogue/id/C123456/")

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(response.resolver_match.view_name, "records:details")

    @prevent_request_warnings  # suppress test output: Internal Server Error: /catalogue/id/C123456/
    @responses.activate
    def test_unexpected_exception_responds_with_server_error_500(self):

        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C123456",
            body=Exception("THIS IS AN UNKNOWN API EXCEPTION"),
        )

        with self.assertLogs("app.lib.api", level="ERROR") as log1:
            with self.assertLogs(
                "app.errors.middleware", level="ERROR"
            ) as log2:
                response = self.client.get("/catalogue/id/C123456/")

        self.assertIn(
            "Unknown JSON API exception: THIS IS AN UNKNOWN API EXCEPTION",
            "".join(log1.output),
        )
        self.assertIn("THIS IS AN UNKNOWN API EXCEPTION", "".join(log2.output))
        self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)

        # check content as raising exception does not allow to test template
        self.assertIn(
            "There is a problem with the service",
            response.content.decode("utf-8"),
        )

    @prevent_request_warnings
    @override_settings(
        ROSETTA_API_URL="",
    )
    def test_missing_config_responds_with_server_error_500(self):

        with self.assertLogs("app.errors.middleware", level="ERROR") as log:
            response = self.client.get("/catalogue/id/C123456/")

        self.assertIn("ROSETTA_API_URL not set", "".join(log.output))
        self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)

        # check content as raising exception does not allow to test template
        self.assertIn(
            "There is a problem with the service",
            response.content.decode("utf-8"),
        )
