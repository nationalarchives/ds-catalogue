from http import HTTPStatus
from test.utils import prevent_request_warnings

from app.lib.fields import DATE_YMD_SEPARATOR, DateKeys
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
        """Test that multiple values for ChoiceField, CharField, FromDateField, ToDateField
        raise SuspiciousOperation and are handled by middleware."""

        view = CatalogueSearchView.as_view()
        for label, fields_constant, test_request in (
            # testing one representation per field type only
            # ChoiceField+variant
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
            # CharField
            (
                "CharField-q",
                FieldsConstant.Q,
                "/catalogue/search/?q=ufo&q=alien",
            ),
            # FromDateField parts
            (
                "FromDateField-covering_date_from-year",
                f"{FieldsConstant.COVERING_DATE_FROM}{DATE_YMD_SEPARATOR}{DateKeys.YEAR}",
                "/catalogue/search/?covering_date_from-year=2020&covering_date_from-year=2021",
            ),
            (
                "FromDateField-covering_date_from-month",
                f"{FieldsConstant.COVERING_DATE_FROM}{DATE_YMD_SEPARATOR}{DateKeys.MONTH}",
                "/catalogue/search/?covering_date_from-month=11&covering_date_from-month=12",
            ),
            (
                "FromDateField-covering_date_from-day",
                f"{FieldsConstant.COVERING_DATE_FROM}{DATE_YMD_SEPARATOR}{DateKeys.DAY}",
                "/catalogue/search/?covering_date_from-day=30&covering_date_from-day=1231",
            ),
            # ToDateField parts
            (
                "ToDateField-opening_date_to-year",
                f"{FieldsConstant.OPENING_DATE_TO}{DATE_YMD_SEPARATOR}{DateKeys.YEAR}",
                "/catalogue/search/?opening_date_to-year=2020&opening_date_to-year=2021",
            ),
            (
                "ToDateField-opening_date_to-month",
                f"{FieldsConstant.OPENING_DATE_TO}{DATE_YMD_SEPARATOR}{DateKeys.MONTH}",
                "/catalogue/search/?opening_date_to-month=11&opening_date_to-month=12",
            ),
            (
                "ToDateField-opening_date_to-day",
                f"{FieldsConstant.OPENING_DATE_TO}{DATE_YMD_SEPARATOR}{DateKeys.DAY}",
                "/catalogue/search/?opening_date_to-day=30&opening_date_to-day=31",
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
