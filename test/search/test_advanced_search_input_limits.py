from django.http import QueryDict

from app.search.constants import (
    ADV_SEARCH_TEXTAREA_MAX_CHARS,
    ADV_SEARCH_TEXTAREA_MAX_LINES,
    FieldsConstant,
)
from app.search.forms import AdvancedSearchForm


def test_textarea_char_limit_exceeded():
    long_value = "a" * (ADV_SEARCH_TEXTAREA_MAX_CHARS + 1)
    qd = QueryDict("", mutable=True)
    qd[FieldsConstant.EXACT_WORDS] = long_value

    form = AdvancedSearchForm(data=qd)
    assert not form.is_valid()
    errors = form.errors
    assert FieldsConstant.EXACT_WORDS in errors


def test_textarea_line_limit_exceeded():
    many_lines = "\n".join(["line"] * (ADV_SEARCH_TEXTAREA_MAX_LINES + 1))
    qd = QueryDict("", mutable=True)
    qd[FieldsConstant.REFERENCES] = many_lines

    form = AdvancedSearchForm(data=qd)
    assert not form.is_valid()
    errors = form.errors
    assert FieldsConstant.REFERENCES in errors
