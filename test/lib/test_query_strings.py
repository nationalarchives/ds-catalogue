import unittest

from config.jinja import (
    qs_append_value,
    qs_is_value_active,
    qs_remove_value,
    qs_replace_value,
    qs_toggle_value,
)
from django.http import QueryDict


class ContentParserTestCase(unittest.TestCase):
    def test_qs_is_value_active(self):
        TEST_QS = QueryDict("a=1&b=2&d=4&d=5")
        self.assertTrue(qs_is_value_active(TEST_QS, "a", "1"))
        self.assertTrue(qs_is_value_active(TEST_QS, "b", "2"))
        self.assertFalse(qs_is_value_active(TEST_QS, "a", "2"))
        self.assertFalse(qs_is_value_active(TEST_QS, "b", "1"))
        self.assertFalse(qs_is_value_active(TEST_QS, "c", "3"))
        self.assertTrue(qs_is_value_active(TEST_QS, "d", "4"))
        self.assertTrue(qs_is_value_active(TEST_QS, "d", "5"))
        self.assertFalse(qs_is_value_active(TEST_QS, "d", "6"))
        # Handles empty query strings
        self.assertFalse(qs_is_value_active(QueryDict(""), "a", "1"))
        self.assertFalse(qs_is_value_active(QueryDict(""), "", ""))
        self.assertFalse(qs_is_value_active(QueryDict("a=1"), "", ""))

    def test_qs_toggle_value(self):
        TEST_QS = QueryDict("a=1&b=2&d=4&d=5")
        # Adds a new qs
        self.assertEqual(
            "a=1&b=2&d=4&d=5&c=3", qs_toggle_value(TEST_QS.copy(), "c", "3")
        )
        # Adds to an existing qs
        self.assertEqual(
            "a=1&b=2&b=1&d=4&d=5", qs_toggle_value(TEST_QS.copy(), "b", "1")
        )
        # Removes a qs of the same value
        self.assertEqual(
            "b=2&d=4&d=5", qs_toggle_value(TEST_QS.copy(), "a", "1")
        )
        # Remove a value from a qs list
        self.assertEqual(
            "a=1&b=2&d=5", qs_toggle_value(TEST_QS.copy(), "d", "4")
        )
        # Add a value to a qs list
        self.assertEqual(
            "a=1&b=2&d=4&d=5&d=6", qs_toggle_value(TEST_QS.copy(), "d", "6")
        )
        # Chain multiple qs modifications
        self.assertEqual(
            "b=2&d=4&d=5&a=2",
            qs_toggle_value(
                qs_toggle_value(TEST_QS.copy(), "a", "1", True), "a", "2"
            ),
        )

    def test_qs_replace_value(self):
        TEST_QS = QueryDict("a=1&b=2&d=4&d=5")
        self.assertEqual(
            "a=2&b=2&d=4&d=5", qs_replace_value(TEST_QS.copy(), "a", "2")
        )
        self.assertEqual(
            "a=1&b=2&d=4&d=5&c=3", qs_replace_value(TEST_QS.copy(), "c", "3")
        )
        self.assertEqual(
            "a=1&b=2&d=6", qs_replace_value(TEST_QS.copy(), "d", "6")
        )

    def test_qs_append_value(self):
        TEST_QS = QueryDict("a=1&b=2&d=4&d=5")
        self.assertEqual(
            "a=1&a=2&b=2&d=4&d=5", qs_append_value(TEST_QS.copy(), "a", "2")
        )
        self.assertEqual(
            "a=1&b=2&d=4&d=5&c=3", qs_append_value(TEST_QS.copy(), "c", "3")
        )
        self.assertEqual(
            "a=1&b=2&d=4&d=5&d=6", qs_append_value(TEST_QS.copy(), "d", "6")
        )

    def test_qs_remove_value(self):
        TEST_QS = QueryDict("a=1&b=2&d=4&d=5")
        self.assertEqual("b=2&d=4&d=5", qs_remove_value(TEST_QS.copy(), "a"))
        self.assertEqual(
            "a=1&b=2&d=4&d=5", qs_remove_value(TEST_QS.copy(), "c")
        )
        self.assertEqual("a=1&b=2", qs_remove_value(TEST_QS.copy(), "d"))
