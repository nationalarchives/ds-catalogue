from django.test import SimpleTestCase

from config.utils.string_processing import (
    none_to_empty_string,
    remove_string_case_insensitive,
)


class RemoveStringCaseInsensitiveTestCase(SimpleTestCase):
    def test_single(self):
        # Removes case-insensitive occurrences without trimming surrounding whitespace.
        self.assertEqual(
            remove_string_case_insensitive("Hello World", "world"),
            "Hello ",
        )

    def test_multiple(self):
        self.assertEqual(
            remove_string_case_insensitive("Foo foo FOO", "fOo"),
            "  ",
        )

    def test_not_found(self):
        self.assertEqual(
            remove_string_case_insensitive("Sample Text", "absent"),
            "Sample Text",
        )

    def test_empty_target(self):
        # No change if target is empty.
        self.assertEqual(
            remove_string_case_insensitive("Nothing Changes", ""),
            "Nothing Changes",
        )

    def test_empty_source(self):
        self.assertEqual(
            remove_string_case_insensitive("", "anything"),
            "",
        )

    def test_substring(self):
        # Only full matches removed.
        self.assertEqual(
            remove_string_case_insensitive("fooffo", "foo"),
            "ffo",
        )


class NoneToEmptyStringTestCase(SimpleTestCase):
    def test_none_to_empty_string(self):
        self.assertEqual(none_to_empty_string(None), "")
        self.assertEqual(none_to_empty_string("some value"), "some value")
