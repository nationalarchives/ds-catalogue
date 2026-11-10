from unittest.mock import patch

import responses
from django.conf import settings
from django.test import SimpleTestCase, TestCase

from app.records.markdown import record_page_to_markdown


class RecordMarkdownConversionTests(SimpleTestCase):
    def test_converts_main_content_and_preserves_structure_and_links(self):
        content = """
            <html><body>
            <header>Site header</header>
            <main>
              <h1>A record &amp; its history</h1>
              <p>A <strong>significant</strong> <em>record</em>.</p>
              <ul><li>First item</li><li>Second item</li></ul>
              <a href="/catalogue/id/C2/">Related record</a>
              <a href="https://example.org/">External link</a>
              <h2>Full description</h2>
              <dl><dt>Reference</dt><dd>ADM 1/2</dd></dl>
              <div class="etna-accordion__body"><p>Access instructions</p></div>
              <span hidden>Field guidance</span>
              <span aria-hidden="true">Decorative icon</span>
              <button>Toggle details</button>
              <input value="Hide field descriptions">
              <form>Feedback form</form>
              <script>tracking()</script><style>.unused {}</style>
              <nav>Page navigation</nav>
              <div class="etna-feedback">Survey invitation</div>
            </main>
            <footer>Site footer</footer>
            </body></html>
        """

        markdown = record_page_to_markdown(
            content, "https://catalogue.example/catalogue/id/C1/"
        )

        for expected in (
            "# A record & its history",
            "**significant**",
            "*record*",
            "- First item\n- Second item",
            "[Related record](https://catalogue.example/catalogue/id/C2/)",
            "[External link](https://example.org/)",
            "## Full description",
            "Reference",
            "ADM 1/2",
            "Access instructions",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, markdown)
        for excluded in (
            "Site header",
            "Site footer",
            "Field guidance",
            "Decorative icon",
            "Toggle details",
            "Hide field descriptions",
            "Feedback form",
            "tracking()",
            ".unused",
            "Page navigation",
            "Survey invitation",
            "<h1>",
        ):
            with self.subTest(excluded=excluded):
                self.assertNotIn(excluded, markdown)
        self.assertTrue(markdown.endswith("\n"))


class RecordDetailNegotiationTests(TestCase):
    def setUp(self):
        self.enterContext(
            patch("app.records.views.fetch_global_notifications", return_value={})
        )
        self.enterContext(
            patch(
                "app.records.views.RecordEnrichmentHelper.fetch_all",
                return_value={
                    "subjects_enrichment": {},
                    "related_records": [],
                    "delivery_options": {},
                },
            )
        )
        self.enterContext(
            patch(
                "app.records.views.RecordEnrichmentHelper.fetch_distressing",
                return_value=None,
            )
        )
        self.record = {
            "id": "C123456",
            "title": "Test record",
            "cleanTitle": "Test record",
            "summaryTitle": "Test record",
            "source": "CAT",
            "referenceNumber": "ADM 1/2",
            "description": {"raw": "<p>A description with <em>emphasis</em>.</p>"},
            "dateCovering": "1900-1901",
            "heldBy": "The National Archives, Kew",
            "heldByCount": 100,
            "subjects": ["Army"],
        }

    def add_record(self):
        responses.get(
            f"{settings.ROSETTA_API_URL}/get?id=C123456",
            json={"data": [{"@template": {"details": self.record}}]},
        )

    @responses.activate
    def test_accept_negotiation(self):
        self.add_record()
        cases = (
            (None, "text/html"),
            ("*/*", "text/html"),
            ("text/*", "text/html"),
            ("text/html", "text/html"),
            ("text/markdown", "text/markdown"),
            ("TEXT/MARKDOWN", "text/markdown"),
            ("text/markdown; charset=utf-8", "text/markdown"),
            ("text/markdown, text/html;q=0.8", "text/markdown"),
            ("text/markdown;q=0.5, text/html;q=0.9", "text/html"),
            ("text/markdown, text/html", "text/markdown"),
            ("text/html, text/markdown", "text/html"),
            ("text/markdown;q=0, text/html", "text/html"),
            ("text/html;q=0, text/markdown", "text/markdown"),
            ("text/markdown;q=0, */*;q=1", "text/html"),
            ("text/html;q=0, */*;q=1", "text/markdown"),
            ("text/*;q=0, */*;q=1, text/markdown", "text/markdown"),
            ("text/markdown;q=0, text/*;q=0.5", "text/html"),
            ("text/markdown;q=0.8, text/*;q=0.9", "text/html"),
            ("text/*;q=0.8, text/markdown;q=0.8", "text/markdown"),
            (
                (
                    "text/html,application/xhtml+xml,application/xml;q=0.9,"
                    "image/avif,image/webp,*/*;q=0.8"
                ),
                "text/html",
            ),
        )
        for accept, content_type in cases:
            with self.subTest(accept=accept):
                headers = {} if accept is None else {"HTTP_ACCEPT": accept}
                response = self.client.get("/catalogue/id/C123456/", **headers)

                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    response["Content-Type"], f"{content_type}; charset=utf-8"
                )
                self.assertIn("Accept", response["Vary"])
                if content_type == "text/html":
                    self.assertContains(response, "<h1")
                else:
                    self.assertContains(response, "# Test record")
                    self.assertNotContains(response, "<html")

    def test_unacceptable_formats_return_406_without_fetching_record(self):
        for accept in (
            "",
            "application/json",
            "text/markdown;q=0",
            "text/html;q=0, text/markdown;q=0",
            "text/*;q=0, */*;q=1",
            "text/markdown; charset=iso-8859-1",
            "*/*;q=0",
        ):
            with self.subTest(accept=accept):
                with patch("app.records.mixins.record_details_by_id") as fetch:
                    response = self.client.get(
                        "/catalogue/id/C123456/", HTTP_ACCEPT=accept
                    )

                self.assertEqual(response.status_code, 406)
                self.assertIn("Accept", response["Vary"])
                self.assertContains(
                    response, "Available representations:", status_code=406
                )
                fetch.assert_not_called()

    @responses.activate
    def test_markdown_contains_record_details_and_absolute_links(self):
        self.add_record()

        response = self.client.get(
            "/catalogue/id/C123456/", HTTP_ACCEPT="text/markdown"
        )

        for expected in (
            "# Test record",
            "ADM 1/2",
            "1900-1901",
            "A description with emphasis.",
            "[Army](http://testserver/catalogue/search/?subject=Army)",
            "Access information is unavailable",
            "Catalogue hierarchy",
        ):
            with self.subTest(expected=expected):
                self.assertContains(response, expected)
        self.assertNotContains(response, "Hide field descriptions")
        self.assertNotContains(response, "Help us improve this website")

    @responses.activate
    def test_archive_and_creator_details_support_markdown(self):
        for source, template in (
            ("ARCHON", "records/archon_detail.html"),
            ("CREATORS", "records/creator_detail.html"),
        ):
            with self.subTest(source=source):
                responses.reset()
                self.record["source"] = source
                self.record["description"] = {
                    "raw": "<contacts><addressline1>Kew</addressline1></contacts>"
                }
                self.add_record()

                response = self.client.get(
                    "/catalogue/id/C123456/", HTTP_ACCEPT="text/markdown"
                )

                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    response["Content-Type"], "text/markdown; charset=utf-8"
                )
                self.assertEqual(response.template_name, [template])
                self.assertContains(response, "# Test record")
                if source == "ARCHON":
                    self.assertContains(response, "Kew")
                    self.assertContains(response, "Contact information")

    @responses.activate
    def test_head_negotiates_markdown_without_a_body(self):
        self.add_record()

        response = self.client.head(
            "/catalogue/id/C123456/", HTTP_ACCEPT="text/markdown"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/markdown; charset=utf-8")
        self.assertIn("Accept", response["Vary"])
        self.assertEqual(response.content, b"")

    @responses.activate
    def test_related_and_help_pages_remain_html(self):
        self.add_record()
        for suffix in ("related/", "help/"):
            with self.subTest(suffix=suffix):
                response = self.client.get(
                    f"/catalogue/id/C123456/{suffix}", HTTP_ACCEPT="text/markdown"
                )

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response["Content-Type"], "text/html; charset=utf-8")

    @responses.activate
    def test_missing_record_keeps_existing_error_response(self):
        responses.get(f"{settings.ROSETTA_API_URL}/get?id=C123456", json={"data": []})

        response = self.client.get(
            "/catalogue/id/C123456/", HTTP_ACCEPT="text/markdown"
        )

        self.assertEqual(response.status_code, 404)
