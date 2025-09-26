from http import HTTPStatus
from test.utils import prevent_request_warnings

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
    def test_choice_field_filter_list_multi_param(self):
        """Simulate SuspiciousOperation from multiple filter_list params."""

        # test direct call to view raises SuspiciousOperation
        request = self.factory.get(
            "/catalogue/search/?group=tna&filter_list=longCollections&filter_list=longCollections"
        )
        view = CatalogueSearchView.as_view()
        with self.assertRaises(SuspiciousOperation):
            view(request)

        # test full stack with middleware handles SuspiciousOperation
        with self.assertLogs("app.search.views", level="INFO") as log:
            response = self.client.get(
                "/catalogue/search/?group=tna&filter_list=longCollections&filter_list=longCollections"
            )
        self.assertIn(
            "INFO:app.search.views:ChoiceField filter_list can only bind to single value",
            "".join(log.output),
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertIn(
            "Page not found",
            response.content.decode("utf-8"),
        )
