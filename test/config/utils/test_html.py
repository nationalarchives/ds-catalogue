from types import SimpleNamespace

from django.test import SimpleTestCase

from config.utils.html import tna_html


class TnaHtmlTestCase(SimpleTestCase):
    def test_empty_returns_input_unchanged(self):
        self.assertEqual(tna_html(""), "")
        self.assertIsNone(tna_html(None))

    def test_adds_tna_list_classes(self):
        self.assertEqual(
            tna_html("<ul><li>a</li></ul>"),
            '<ul class="tna-ul"><li>a</li></ul>',
        )
        self.assertEqual(
            tna_html("<ol><li>a</li></ol>"),
            '<ol class="tna-ol"><li>a</li></ol>',
        )

    def test_converts_bold_to_strong(self):
        self.assertEqual(
            tna_html('<b>x</b> and <b class="y">z</b>'),
            '<strong>x</strong> and <strong class="y">z</strong>',
        )

    def test_strips_wagtail_block_keys(self):
        self.assertEqual(tna_html('<p data-block-key="abc">hi</p>'), "<p>hi</p>")

    def test_converts_crlf_to_break(self):
        self.assertEqual(tna_html("one\r\ntwo"), "one<br>two")

    def test_adds_rel_to_external_links(self):
        self.assertEqual(
            tna_html('<a href="https://example.com/x">e</a>'),
            '<a rel="noreferrer nofollow noopener" href="https://example.com/x">e</a>',
        )

    def test_leaves_tna_https_links_untouched(self):
        for host in ("www", "discovery", "webarchive"):
            link = f'<a href="https://{host}.nationalarchives.gov.uk/x">i</a>'
            with self.subTest(host=host):
                self.assertEqual(tna_html(link), link)
