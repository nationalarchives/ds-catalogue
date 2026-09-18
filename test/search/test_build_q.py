from django.test import SimpleTestCase

from app.search.views import FieldsConstant, _build_q


class _F:
    def __init__(self, cleaned=None, value=None):
        self.cleaned = cleaned
        self.value = value or cleaned


class DummyForm:
    def __init__(self, all_words="", exact_words="", any_words="", ignore_words=""):
        self.fields = {
            FieldsConstant.ALL_WORDS: _F(cleaned=all_words),
            FieldsConstant.EXACT_WORDS: _F(cleaned=exact_words),
            FieldsConstant.ANY_WORDS: _F(cleaned=any_words),
            FieldsConstant.IGNORE_WORDS: _F(cleaned=ignore_words),
        }


class BuildQTests(SimpleTestCase):
    def test_all_words_only(self):
        form = DummyForm(all_words="search term")
        self.assertEqual(_build_q(form), "search term")

    def test_exact_words_multiple(self):
        form = DummyForm(exact_words="one\ntwo")
        self.assertEqual(_build_q(form), '"one" AND "two"')

    def test_any_words_with_spaces_and_grouping(self):
        form = DummyForm(all_words="start", any_words="foo\nbar baz")
        # 'bar baz' should be quoted by _quote_if_needed and grouped
        self.assertEqual(_build_q(form), 'start AND (foo OR "bar baz")')

    def test_ignore_words_multiple(self):
        form = DummyForm(ignore_words="bad\nworse")
        self.assertEqual(_build_q(form), 'NOT "bad" NOT "worse"')

    def test_complex_combination_ordering(self):
        form = DummyForm(
            all_words="all",
            exact_words="first\nsecond",
            any_words="one\ntwo three",
            ignore_words="skip",
        )
        # Construct expected according to _build_q ordering and quoting rules
        expected = 'all AND "first" AND "second" AND (one OR "two three") NOT "skip"'
        self.assertEqual(_build_q(form), expected)
