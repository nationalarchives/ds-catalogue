from django.test import SimpleTestCase

from config.utils.markup_truncation import truncate_preserve_mark_tags


class TruncatePreserveMarkTagsTestCase(SimpleTestCase):
    def test_no_truncation(self):
        self.assertEqual(
            truncate_preserve_mark_tags("Hello world", 50),
            "Hello world",
        )

    def test_simple_truncation(self):
        self.assertEqual(
            truncate_preserve_mark_tags("Hello world", 5),
            "Hello…",
        )

    def test_with_mark_no_truncation(self):
        self.assertEqual(
            truncate_preserve_mark_tags("Hello <mark>world</mark>", 20),
            "Hello <mark>world</mark>",
        )

    def test_truncate_after_mark(self):
        self.assertEqual(
            truncate_preserve_mark_tags("Hi <mark>there</mark> friend", 9),
            "Hi <mark>there</mark> …",
        )

    def test_truncate_inside_mark_content(self):
        self.assertEqual(
            truncate_preserve_mark_tags("<mark>abcdefghij</mark>", 5),
            "<mark>abcde</mark>…",
        )

    def test_multiple_marks(self):
        self.assertEqual(
            truncate_preserve_mark_tags(
                "A <mark>quick</mark> brown <mark>fox</mark> jumps", 17
            ),
            "A <mark>quick</mark> brown <mark>fox</mark>…",
        )

    def test_adjacent_marks(self):
        self.assertEqual(
            truncate_preserve_mark_tags(
                "<mark>alpha</mark><mark>beta</mark><mark>gamma</mark>", 12
            ),
            "<mark>alpha</mark><mark>beta</mark><mark>gam</mark>…",
        )

    def test_empty_string(self):
        self.assertEqual(
            truncate_preserve_mark_tags("", 10),
            "",
        )

    def test_zero_length(self):
        self.assertEqual(
            truncate_preserve_mark_tags("Content", 0),
            "",
        )

    def test_only_mark_tag(self):
        # Reaching the limit exactly still counts as truncation (ellipsis added).
        self.assertEqual(
            truncate_preserve_mark_tags("<mark>content</mark>", 7),
            "<mark>content</mark>…",
        )

    def test_uses_default_max_length_when_omitted(self):
        long_text = "a" * 300
        self.assertEqual(
            truncate_preserve_mark_tags(long_text),
            "a" * 250 + "…",
        )
