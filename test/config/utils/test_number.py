from django.test import SimpleTestCase

from config.utils.number import format_number


class FormatNumberTestCase(SimpleTestCase):
    def test_format_number(self):
        self.assertEqual(format_number(1), "1")
        self.assertEqual(format_number("1"), "1")
        self.assertEqual(format_number("a"), "a")
        self.assertEqual(format_number(999), "999")
        self.assertEqual(format_number(1000), "1,000")
        self.assertEqual(format_number(1234567890), "1,234,567,890")
