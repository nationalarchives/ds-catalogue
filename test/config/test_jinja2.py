from config.jinja2 import (
    dump_json,
    format_number,
    qs_append_value,
    qs_is_value_active,
    qs_remove_value,
    qs_replace_value,
    qs_toggle_value,
    sanitise_record_field,
    slugify,
    remove_string_case_insensitive,
)
from django.http import QueryDict
from django.test import TestCase


class Jinja2TestCase(TestCase):
    def test_sanitise_record_field(self):
        source = """  <p>Test</p> <p>Test</p>     <p>Test</p> """
        self.assertEqual(
            sanitise_record_field(source),
            "<p>Test</p><p>Test</p><p>Test</p>",
        )

    def test_dump_json(self):
        source = {
            "foo1": "bar",
            "foo2": True,
            "foo3": 123,
            "foo4": ["a", "b", "c"],
            "foo5": {"a": 1, "b": 2},
            "foo6": None,
        }
        self.assertEqual(
            dump_json(source),
            """{
  "foo1": "bar",
  "foo2": true,
  "foo3": 123,
  "foo4": [
    "a",
    "b",
    "c"
  ],
  "foo5": {
    "a": 1,
    "b": 2
  },
  "foo6": null
}""",
        )

    def test_format_number(self):
        self.assertEqual(format_number(1), "1")
        self.assertEqual(format_number("1"), "1")
        self.assertEqual(format_number("a"), "a")
        self.assertEqual(format_number(999), "999")
        self.assertEqual(format_number(1000), "1,000")
        self.assertEqual(format_number(1234567890), "1,234,567,890")

    def test_slugify(self):
        self.assertEqual(slugify(""), "")
        self.assertEqual(slugify("test"), "test")
        self.assertEqual(slugify("  test TEST"), "test-test")
        self.assertEqual(slugify("test 12 3 -4 "), "test-12-3-4")
        self.assertEqual(slugify("test---test"), "test-test")
        self.assertEqual(slugify("test---"), "test")
        self.assertEqual(slugify("test---$"), "test")
        self.assertEqual(slugify("test---$---"), "test")

    def test_qs_is_value_active(self):
        TEST_QS = QueryDict("", mutable=True)
        TEST_QS.update({"a": "1", "b": "1"})
        TEST_QS.update({"b": "2"})
        self.assertTrue(qs_is_value_active(TEST_QS, "a", "1"))
        self.assertTrue(qs_is_value_active(TEST_QS, "b", "1"))
        self.assertTrue(qs_is_value_active(TEST_QS, "b", "2"))
        self.assertFalse(qs_is_value_active(TEST_QS, "a", "2"))
        self.assertFalse(qs_is_value_active(TEST_QS, "c", "3"))
        self.assertFalse(qs_is_value_active(TEST_QS, "c", ""))
        self.assertFalse(qs_is_value_active(TEST_QS, "a", ""))
        self.assertFalse(qs_is_value_active(TEST_QS, "", ""))
        self.assertFalse(qs_is_value_active(QueryDict(""), "a", "1"))
        self.assertFalse(qs_is_value_active(QueryDict(""), "", ""))

    def test_qs_toggle_value(self):
        TEST_QS = QueryDict("", mutable=True)
        TEST_QS.update({"a": "1", "b": "1"})
        TEST_QS.update({"b": "2"})
        self.assertEqual(
            "a=1&b=1&b=2&b=3", qs_toggle_value(TEST_QS.copy(), "b", "3")
        )
        self.assertEqual(
            "a=1&b=1&b=2&c=3", qs_toggle_value(TEST_QS.copy(), "c", "3")
        )
        self.assertEqual("b=1&b=2", qs_toggle_value(TEST_QS.copy(), "a", "1"))
        self.assertEqual("a=1", qs_toggle_value(QueryDict(""), "a", "1"))
        self.assertEqual("a=", qs_toggle_value(QueryDict(""), "a", ""))

    def test_qs_replace_value(self):
        TEST_QS = QueryDict("", mutable=True)
        TEST_QS.update({"a": "1", "b": "1"})
        TEST_QS.update({"b": "2"})
        self.assertEqual(
            "a=1&b=1&b=2", qs_replace_value(TEST_QS.copy(), "a", "1")
        )
        self.assertEqual(
            "a=2&b=1&b=2", qs_replace_value(TEST_QS.copy(), "a", "2")
        )
        self.assertEqual("a=1&b=1", qs_replace_value(TEST_QS.copy(), "b", "1"))
        self.assertEqual("a=1&b=3", qs_replace_value(TEST_QS.copy(), "b", "3"))
        self.assertEqual(
            "a=1&b=1&b=2&c=3", qs_replace_value(TEST_QS.copy(), "c", "3")
        )
        self.assertEqual(
            "a=&b=1&b=2", qs_replace_value(TEST_QS.copy(), "a", "")
        )
        self.assertEqual("a=1&b=", qs_replace_value(TEST_QS.copy(), "b", ""))
        self.assertEqual(
            "a=1&b=1&b=2&c=", qs_replace_value(TEST_QS.copy(), "c", "")
        )

    def test_qs_append_value(self):
        TEST_QS = QueryDict("", mutable=True)
        TEST_QS.update({"a": "1", "b": "1"})
        TEST_QS.update({"b": "2"})
        self.assertEqual(
            "a=1&b=1&b=2", qs_append_value(TEST_QS.copy(), "a", "1")
        )
        self.assertEqual(
            "a=1&a=2&b=1&b=2", qs_append_value(TEST_QS.copy(), "a", "2")
        )
        self.assertEqual(
            "a=1&b=1&b=2&c=3", qs_append_value(TEST_QS.copy(), "c", "3")
        )
        self.assertEqual(
            "a=1&b=1&b=2", qs_append_value(TEST_QS.copy(), "", "1")
        )
        self.assertEqual(
            "a=1&a=&b=1&b=2", qs_append_value(TEST_QS.copy(), "a", "")
        )
        self.assertEqual(
            "a=1&b=1&b=2&b=", qs_append_value(TEST_QS.copy(), "b", "")
        )
        self.assertEqual(
            "a=1&b=1&b=2&c=", qs_append_value(TEST_QS.copy(), "c", "")
        )

    def test_qs_remove_value(self):
        TEST_QS = QueryDict("", mutable=True)
        TEST_QS.update({"a": "1", "b": "1"})
        TEST_QS.update({"b": "2"})
        self.assertEqual("b=1&b=2", qs_remove_value(TEST_QS.copy(), "a"))
        self.assertEqual("a=1", qs_remove_value(TEST_QS.copy(), "b"))
        self.assertEqual("a=1&b=1&b=2", qs_remove_value(TEST_QS.copy(), "c"))
        self.assertEqual("a=1&b=1&b=2", qs_remove_value(TEST_QS.copy(), ""))

    def test_remove_string_case_insensitive_single(self):
        # Assumes function removes all case-insensitive occurrences without trimming surrounding whitespace.
        self.assertEqual(
            remove_string_case_insensitive("Hello World", "world"),
            "Hello ",
        )

    def test_remove_string_case_insensitive_multiple(self):
        self.assertEqual(
            remove_string_case_insensitive("Foo foo FOO", "fOo"),
            "  ",
        )

    def test_remove_string_case_insensitive_not_found(self):
        self.assertEqual(
            remove_string_case_insensitive("Sample Text", "absent"),
            "Sample Text",
        )

    def test_remove_string_case_insensitive_empty_target(self):
        # Expect no change if target empty.
        self.assertEqual(
            remove_string_case_insensitive("Nothing Changes", ""),
            "Nothing Changes",
        )

    def test_remove_string_case_insensitive_empty_source(self):
        self.assertEqual(
            remove_string_case_insensitive("", "anything"),
            "",
        )

    def test_remove_string_case_insensitive_substring(self):
        # Ensure only full matches removed.
        self.assertEqual(
            remove_string_case_insensitive("fooffo", "foo"),
            "ffo",
        )
