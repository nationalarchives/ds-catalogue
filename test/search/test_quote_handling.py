from app.search.views import _quote_if_needed


def test_quote_with_spaces():
    assert _quote_if_needed("hello world") == '"hello world"'


def test_escape_and_quote_with_internal_quotes_and_spaces():
    value = 'He said "hello"'
    # Expect internal quotes escaped and whole string quoted
    assert _quote_if_needed(value) == '"He said \\"hello\\""'


def test_escape_without_spaces_for_internal_quote():
    value = 'contains"quote'
    # No spaces, so return escaped content without surrounding quotes
    assert _quote_if_needed(value) == 'contains\\"quote'


def test_escape_backslash_and_quote_with_space():
    value = 'back\\slash here'
    # backslash doubled in the escaped output and whole string quoted
    assert _quote_if_needed(value) == '"back\\\\slash here"'


def test_no_change_for_simple_token():
    assert _quote_if_needed("simple") == "simple"
