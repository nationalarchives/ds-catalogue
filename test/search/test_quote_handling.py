from django.test import SimpleTestCase

from app.search.views import _quote_if_needed


class QuoteHandlingTests(SimpleTestCase):
    def test_quote_with_spaces(self):
        self.assertEqual(_quote_if_needed("hello world"), '"hello world"')

    def test_escape_and_quote_with_internal_quotes_and_spaces(self):
        value = 'He said "hello"'
        # Expect internal quotes escaped and whole string quoted
        self.assertEqual(_quote_if_needed(value), '"He said \\"hello\\""')

    def test_escape_without_spaces_for_internal_quote(self):
        value = 'contains"quote'
        # No spaces, so return escaped content without surrounding quotes
        self.assertEqual(_quote_if_needed(value), 'contains\\"quote')

    def test_escape_backslash_and_quote_with_space(self):
        value = "back\\slash here"
        # backslash doubled in the escaped output and whole string quoted
        self.assertEqual(_quote_if_needed(value), '"back\\\\slash here"')

    def test_no_change_for_simple_token(self):
        self.assertEqual(_quote_if_needed("simple"), "simple")
