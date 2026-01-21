from http import HTTPStatus
from test.utils import prevent_request_warnings

from app.search.constants import FieldsConstant
from app.search.views import CatalogueSearchView
from django.core.exceptions import SuspiciousOperation
from django.test import RequestFactory, TestCase, override_settings


class TestCatalogueSearchViewExceptions(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    @prevent_request_warnings  # suppress test output: Internal Server Error: /catalogue/search/
    @override_settings(
        ROSETTA_API_URL="",
    )
    def test_missing_config_with_server_error(self):

        with self.assertLogs("app.errors.middleware", level="ERROR") as log:
            response = self.client.get("/catalogue/search/")

        self.assertIn("ROSETTA_API_URL not set", "".join(log.output))
        self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)

        # check content as raising exception does not allow to test template
        self.assertIn(
            "There is a problem with the service",
            response.content.decode("utf-8"),
        )

    @prevent_request_warnings
    def test_suspicious_operation(self):
        """Test that multiple values for ChoiceField and CharField
        raise SuspiciousOperation and are handled by middleware."""

        view = CatalogueSearchView.as_view()
        for label, fields_constant, test_request in (
            # testing one representation per field type is sufficient
            (
                "ChoiceField-group",
                FieldsConstant.GROUP,
                "/catalogue/search/?group=tna&group=nonTna",
            ),
            (
                "ChoiceField-group-with-empty-value",
                FieldsConstant.GROUP,
                "/catalogue/search/?group=&group=nonTna",
            ),
            (
                "CharField-q",
                FieldsConstant.Q,
                "/catalogue/search/?q=ufo&q=alien",
            ),
        ):
            with self.subTest(label):
                # test direct call to view raises SuspiciousOperation
                request = self.factory.get(test_request)
                with self.assertRaises(SuspiciousOperation):
                    view(request)

                # test full stack with middleware handles SuspiciousOperation
                with self.assertLogs("app.search.views", level="INFO") as log:
                    response = self.client.get(test_request)
                    self.assertIn(
                        f"INFO:app.search.views:Field {fields_constant} can only bind to single value",
                        "".join(log.output),
                    )

                    # check response code and content
                    self.assertEqual(
                        response.status_code, HTTPStatus.BAD_REQUEST
                    )
                    self.assertIn(
                        "Page not found",
                        response.content.decode("utf-8"),
                    )
