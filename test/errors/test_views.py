from http import HTTPStatus
from unittest.mock import patch

from django.http import HttpResponse, HttpResponseServerError
from django.template import TemplateDoesNotExist
from django.test import RequestFactory, SimpleTestCase

from app.errors.constants import PAGE_NOT_FOUND_TEMPLATE, SERVER_ERROR_TEMPLATE
from app.errors.views import page_not_found_error_view, server_error_view


class PageNotFoundErrorViewTestCase(SimpleTestCase):
    def setUp(self):
        self.request = RequestFactory().get("/missing/")

    @patch("app.errors.views.render")
    def test_renders_template_with_404_status(self, mock_render):
        mock_render.return_value = HttpResponse(b"not found")
        response = page_not_found_error_view(self.request)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        mock_render.assert_called_once_with(
            self.request,
            PAGE_NOT_FOUND_TEMPLATE,
            context={"status_code": HTTPStatus.NOT_FOUND},
        )

    @patch("app.errors.views.render")
    def test_explicit_status_code_propagates(self, mock_render):
        mock_render.return_value = HttpResponse(b"gone")
        response = page_not_found_error_view(self.request, status_code=HTTPStatus.GONE)
        self.assertEqual(response.status_code, HTTPStatus.GONE)
        mock_render.assert_called_once_with(
            self.request,
            PAGE_NOT_FOUND_TEMPLATE,
            context={"status_code": HTTPStatus.GONE},
        )

    @patch("app.errors.views.render")
    def test_falls_back_to_500_when_template_missing(self, mock_render):
        mock_render.side_effect = TemplateDoesNotExist(PAGE_NOT_FOUND_TEMPLATE)
        response = page_not_found_error_view(self.request)
        self.assertIsInstance(response, HttpResponseServerError)
        self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertIn(b"Template not found", response.content)


class ServerErrorViewTestCase(SimpleTestCase):
    def setUp(self):
        self.request = RequestFactory().get("/boom/")

    @patch("app.errors.views.render")
    def test_renders_template_with_500_status(self, mock_render):
        mock_render.return_value = HttpResponse(b"server error")
        response = server_error_view(self.request)
        self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)
        mock_render.assert_called_once_with(
            self.request,
            SERVER_ERROR_TEMPLATE,
            context={"status_code": HTTPStatus.INTERNAL_SERVER_ERROR},
        )

    @patch("app.errors.views.render")
    def test_falls_back_to_500_when_template_missing(self, mock_render):
        mock_render.side_effect = TemplateDoesNotExist(SERVER_ERROR_TEMPLATE)
        response = server_error_view(self.request)
        self.assertIsInstance(response, HttpResponseServerError)
        self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertIn(b"Template not found", response.content)
