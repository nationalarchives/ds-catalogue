from django.http import QueryDict
from django.test import SimpleTestCase

from app.search.constants import (
    ADV_SEARCH_TEXTAREA_MAX_CHARS,
    ADV_SEARCH_TEXTAREA_MAX_LINES,
    FieldsConstant,
)
from app.search.forms import AdvancedSearchForm


class AdvancedSearchInputLimitsTests(SimpleTestCase):
    def test_textarea_char_limit_exceeded(self):
        long_value = "a" * (ADV_SEARCH_TEXTAREA_MAX_CHARS + 1)
        qd = QueryDict("", mutable=True)
        qd[FieldsConstant.EXACT_WORDS] = long_value

        form = AdvancedSearchForm(data=qd)
        self.assertFalse(form.is_valid())
        errors = form.errors
        self.assertIn(FieldsConstant.EXACT_WORDS, errors)

    def test_textarea_line_limit_exceeded(self):
        many_lines = "\n".join(["line"] * (ADV_SEARCH_TEXTAREA_MAX_LINES + 1))
        qd = QueryDict("", mutable=True)
        qd[FieldsConstant.REFERENCES] = many_lines

        form = AdvancedSearchForm(data=qd)
        self.assertFalse(form.is_valid())
        errors = form.errors
        self.assertIn(FieldsConstant.REFERENCES, errors)
