from http import HTTPStatus
from unittest.mock import MagicMock, patch
from urllib.parse import parse_qs, urlparse

from django.template import TemplateDoesNotExist
from django.template import loader as django_loader
from django.test import TestCase, modify_settings, override_settings

REAL_GET_TEMPLATE = django_loader.get_template


@override_settings(DEBUG=False)
@modify_settings(MIDDLEWARE={"remove": "debug_toolbar.middleware.DebugToolbarMiddleware"})
class AdvancedSearchViewTests(TestCase):
    @patch("app.search.views.fetch_global_notifications", return_value=None)
    def test_get_advanced_search_page(self, _mock_fetch_global_notifications):
        response = self.client.get("/catalogue/advanced-search/")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Advanced search")
        self.assertNotContains(response, "data-js-chip-field")
        self.assertContains(response, "advanced-search-js")

    @patch("app.search.views.fetch_global_notifications", return_value=None)
    def test_get_advanced_search_js_page_falls_back_to_html_template(
        self, _mock_fetch_global_notifications
    ):
        def mock_get_template(name: str):
            if name == "search/advanced_search_js.html":
                raise TemplateDoesNotExist(name)
            return REAL_GET_TEMPLATE(name)

        with patch(
            "app.search.views.loader.get_template", side_effect=mock_get_template
        ):
            response = self.client.get("/catalogue/advanced-search-js/")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Advanced search")
        self.assertNotContains(response, "data-js-chip-field")

    @patch("app.search.views.fetch_global_notifications", return_value=None)
    def test_get_advanced_search_js_page_falls_back_when_js_render_fails(
        self, _mock_fetch_global_notifications
    ):
        failing_template = MagicMock()
        failing_template.render.side_effect = RuntimeError("render failed")

        def mock_get_template(name: str):
            if name == "search/advanced_search_js.html":
                return failing_template
            return REAL_GET_TEMPLATE(name)

        with patch(
            "app.search.views.loader.get_template", side_effect=mock_get_template
        ):
            response = self.client.get("/catalogue/advanced-search-js/")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Advanced search")
        self.assertNotContains(response, "data-js-chip-field")

    @patch("app.search.views.fetch_global_notifications", return_value=None)
    def test_get_advanced_search_js_page(self, _mock_fetch_global_notifications):
        response = self.client.get("/catalogue/advanced-search-js/")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "data-js-chip-field")

    @patch("app.search.views.fetch_global_notifications", return_value=None)
    def test_post_advanced_search_without_input_shows_error(
        self, _mock_fetch_global_notifications
    ):
        response = self.client.post("/catalogue/advanced-search/", data={})

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Enter at least one value to search.")

    @patch("app.search.views.fetch_global_notifications", return_value=None)
    def test_post_advanced_search_with_invalid_date_range_shows_error(
        self, _mock_fetch_global_notifications
    ):
        response = self.client.post(
            "/catalogue/advanced-search/",
            data={
                "date_from-year": "2001",
                "date_from-month": "1",
                "date_from-day": "2",
                "date_to-year": "2001",
                "date_to-month": "1",
                "date_to-day": "1",
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "cannot be after")

    @patch("app.search.views.fetch_global_notifications", return_value=None)
    def test_post_advanced_search_redirects_with_query_params(
        self, _mock_fetch_global_notifications
    ):
        response = self.client.post(
            "/catalogue/advanced-search/",
            data={
                "all_words": "medal card",
                "exact_words": "war diary\nsignal",
                "any_words": "army",
                "ignore_words": "navy",
                "references": "WO 95\n ADM 1 ",
                "date_from-year": "1900",
                "date_to-year": "1910",
                "date_to-month": "12",
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)

        location = response["Location"]
        parsed = urlparse(location)
        query_params = parse_qs(parsed.query)

        self.assertEqual(parsed.path, "/catalogue/search/")
        self.assertEqual(
            query_params["q"][0],
            'medal card AND "war diary" AND "signal" AND army NOT "navy"',
        )
        self.assertEqual(query_params["references"][0], "WO 95\nADM 1")
        self.assertEqual(query_params["covering_date_from-year"][0], "1900")
        self.assertEqual(query_params["covering_date_to-year"][0], "1910")
        self.assertEqual(query_params["covering_date_to-month"][0], "12")
