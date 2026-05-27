from types import SimpleNamespace
from unittest.mock import patch

from django.http import QueryDict
from django.test import SimpleTestCase

from config.jinja_filters import (
    base64_decode,
    base64_encode,
    dump_json,
    format_number,
    none_to_empty_string,
    now_iso_8601,
    now_iso_8601_date,
    override_tna_record_count,
    parse_json,
    qs_append_value,
    qs_is_value_active,
    qs_remove_value,
    qs_replace_value,
    qs_toggle_value,
    remove_string_case_insensitive,
    sanitise_record_field,
    sanitize_search_qs,
    slugify,
    tna_html,
    truncate_preserve_mark_tags,
)


class Jinja2TestCase(SimpleTestCase):
    # -----------------------------------------------------------------------
    # sanitise_record_field
    # -----------------------------------------------------------------------

    def test_sanitise_record_field_collapses_whitespace_between_p_tags(self):
        source = """  <p>Test</p> <p>Test</p>     <p>Test</p> """
        self.assertEqual(
            sanitise_record_field(source),
            "<p>Test</p><p>Test</p><p>Test</p>",
        )

    # -----------------------------------------------------------------------
    # dump_json
    # -----------------------------------------------------------------------

    def test_dump_json_round_trips_via_json_loads(self):
        """Round-trip test: more robust than asserting against a literal."""
        import json as _json

        source = {
            "foo1": "bar",
            "foo2": True,
            "foo3": 123,
            "foo4": ["a", "b", "c"],
            "foo5": {"a": 1, "b": 2},
            "foo6": None,
        }
        self.assertEqual(_json.loads(dump_json(source)), source)

    def test_dump_json_uses_two_space_indent(self):
        """Specifically pin the indent format that templates depend on."""
        result = dump_json({"a": 1})
        self.assertIn('\n  "a"', result)

    # -----------------------------------------------------------------------
    # format_number
    # -----------------------------------------------------------------------

    def test_format_number(self):
        self.assertEqual(format_number(1), "1")
        self.assertEqual(format_number("1"), "1")
        self.assertEqual(format_number("a"), "a")
        self.assertEqual(format_number(999), "999")
        self.assertEqual(format_number(1000), "1,000")
        self.assertEqual(format_number(1234567890), "1,234,567,890")

    # -----------------------------------------------------------------------
    # slugify
    # -----------------------------------------------------------------------

    def test_slugify(self):
        self.assertEqual(slugify(""), "")
        self.assertEqual(slugify("test"), "test")
        self.assertEqual(slugify("  test TEST"), "test-test")
        self.assertEqual(slugify("test 12 3 -4 "), "test-12-3-4")
        self.assertEqual(slugify("test---test"), "test-test")
        self.assertEqual(slugify("test---"), "test")
        self.assertEqual(slugify("test---$"), "test")
        self.assertEqual(slugify("test---$---"), "test")

    # -----------------------------------------------------------------------
    # tna_html
    # -----------------------------------------------------------------------

    def test_tna_html_empty_input(self):
        self.assertEqual(tna_html(""), "")
        self.assertIsNone(tna_html(None))

    def test_tna_html_adds_tna_ul_class(self):
        self.assertEqual(
            tna_html("<ul><li>foo</li></ul>"),
            '<ul class="tna-ul"><li>foo</li></ul>',
        )

    def test_tna_html_adds_tna_ol_class(self):
        self.assertEqual(
            tna_html("<ol><li>foo</li></ol>"),
            '<ol class="tna-ol"><li>foo</li></ol>',
        )

    def test_tna_html_converts_b_to_strong(self):
        self.assertEqual(
            tna_html("<b>bold</b>"),
            "<strong>bold</strong>",
        )

    def test_tna_html_converts_b_with_attributes_to_strong(self):
        self.assertEqual(
            tna_html('<b class="x">bold</b>'),
            '<strong class="x">bold</strong>',
        )

    def test_tna_html_strips_wagtail_data_block_key(self):
        self.assertEqual(
            tna_html('<p data-block-key="abc123">foo</p>'),
            "<p>foo</p>",
        )

    def test_tna_html_replaces_crlf_with_br(self):
        self.assertEqual(
            tna_html("line one\r\nline two"),
            "line one<br>line two",
        )

    def test_tna_html_internal_link_www_no_rel_added(self):
        source = '<a href="https://www.nationalarchives.gov.uk/foo">link</a>'
        self.assertEqual(tna_html(source), source)

    def test_tna_html_internal_link_discovery_no_rel_added(self):
        source = '<a href="https://discovery.nationalarchives.gov.uk/x">link</a>'
        self.assertEqual(tna_html(source), source)

    def test_tna_html_internal_link_webarchive_no_rel_added(self):
        source = '<a href="https://webarchive.nationalarchives.gov.uk/y">x</a>'
        self.assertEqual(tna_html(source), source)

    def test_tna_html_external_link_adds_rel(self):
        self.assertEqual(
            tna_html('<a href="https://example.com/">link</a>'),
            '<a rel="noreferrer nofollow noopener" href="https://example.com/">link</a>',
        )

    def test_tna_html_http_internal_link_treated_as_external(self):
        """
        Documents current behaviour: the regex only matches https:// for
        internal-link detection, so http:// versions of TNA URLs get the
        external rel attribute. Change this test if the behaviour changes.
        """
        result = tna_html('<a href="http://www.nationalarchives.gov.uk/foo">link</a>')
        self.assertIn('rel="noreferrer nofollow noopener"', result)

    def test_tna_html_unrecognised_internal_subdomain_treated_as_external(
        self,
    ):
        """
        Documents current behaviour: only www/discovery/webarchive subdomains
        are considered internal. Other TNA subdomains get the external rel.
        """
        result = tna_html(
            '<a href="https://media.nationalarchives.gov.uk/foo">link</a>'
        )
        self.assertIn('rel="noreferrer nofollow noopener"', result)

    # -----------------------------------------------------------------------
    # qs_is_value_active
    # -----------------------------------------------------------------------

    def test_qs_is_value_active(self):
        test_qs = QueryDict("", mutable=True)
        test_qs.update({"a": "1", "b": "1"})
        test_qs.update({"b": "2"})
        self.assertTrue(qs_is_value_active(test_qs, "a", "1"))
        self.assertTrue(qs_is_value_active(test_qs, "b", "1"))
        self.assertTrue(qs_is_value_active(test_qs, "b", "2"))
        self.assertFalse(qs_is_value_active(test_qs, "a", "2"))
        self.assertFalse(qs_is_value_active(test_qs, "c", "3"))
        self.assertFalse(qs_is_value_active(test_qs, "c", ""))
        self.assertFalse(qs_is_value_active(test_qs, "a", ""))
        self.assertFalse(qs_is_value_active(test_qs, "", ""))
        self.assertFalse(qs_is_value_active(QueryDict(""), "a", "1"))
        self.assertFalse(qs_is_value_active(QueryDict(""), "", ""))

    # -----------------------------------------------------------------------
    # qs_toggle_value
    # -----------------------------------------------------------------------

    def test_qs_toggle_value(self):
        test_qs = QueryDict("", mutable=True)
        test_qs.update({"a": "1", "b": "1"})
        test_qs.update({"b": "2"})
        self.assertEqual("a=1&b=1&b=2&b=3", qs_toggle_value(test_qs.copy(), "b", "3"))
        self.assertEqual("a=1&b=1&b=2&c=3", qs_toggle_value(test_qs.copy(), "c", "3"))
        self.assertEqual("b=1&b=2", qs_toggle_value(test_qs.copy(), "a", "1"))
        self.assertEqual("a=1", qs_toggle_value(QueryDict(""), "a", "1"))
        self.assertEqual("a=", qs_toggle_value(QueryDict(""), "a", ""))

    # -----------------------------------------------------------------------
    # qs_replace_value
    # -----------------------------------------------------------------------

    def test_qs_replace_value(self):
        test_qs = QueryDict("", mutable=True)
        test_qs.update({"a": "1", "b": "1"})
        test_qs.update({"b": "2"})
        self.assertEqual("a=1&b=1&b=2", qs_replace_value(test_qs.copy(), "a", "1"))
        self.assertEqual("a=2&b=1&b=2", qs_replace_value(test_qs.copy(), "a", "2"))
        self.assertEqual("a=1&b=1", qs_replace_value(test_qs.copy(), "b", "1"))
        self.assertEqual("a=1&b=3", qs_replace_value(test_qs.copy(), "b", "3"))
        self.assertEqual("a=1&b=1&b=2&c=3", qs_replace_value(test_qs.copy(), "c", "3"))
        self.assertEqual("a=&b=1&b=2", qs_replace_value(test_qs.copy(), "a", ""))
        self.assertEqual("a=1&b=", qs_replace_value(test_qs.copy(), "b", ""))
        self.assertEqual("a=1&b=1&b=2&c=", qs_replace_value(test_qs.copy(), "c", ""))

    # -----------------------------------------------------------------------
    # qs_append_value
    # -----------------------------------------------------------------------

    def test_qs_append_value(self):
        test_qs = QueryDict("", mutable=True)
        test_qs.update({"a": "1", "b": "1"})
        test_qs.update({"b": "2"})
        self.assertEqual("a=1&b=1&b=2", qs_append_value(test_qs.copy(), "a", "1"))
        self.assertEqual("a=1&a=2&b=1&b=2", qs_append_value(test_qs.copy(), "a", "2"))
        self.assertEqual("a=1&b=1&b=2&c=3", qs_append_value(test_qs.copy(), "c", "3"))
        self.assertEqual("a=1&b=1&b=2", qs_append_value(test_qs.copy(), "", "1"))
        self.assertEqual("a=1&a=&b=1&b=2", qs_append_value(test_qs.copy(), "a", ""))
        self.assertEqual("a=1&b=1&b=2&b=", qs_append_value(test_qs.copy(), "b", ""))
        self.assertEqual("a=1&b=1&b=2&c=", qs_append_value(test_qs.copy(), "c", ""))

    # -----------------------------------------------------------------------
    # qs_remove_value
    # -----------------------------------------------------------------------

    def test_qs_remove_value(self):
        test_qs = QueryDict("", mutable=True)
        test_qs.update({"a": "1", "b": "1"})
        test_qs.update({"b": "2"})
        self.assertEqual("b=1&b=2", qs_remove_value(test_qs.copy(), "a"))
        self.assertEqual("a=1", qs_remove_value(test_qs.copy(), "b"))
        self.assertEqual("a=1&b=1&b=2", qs_remove_value(test_qs.copy(), "c"))
        self.assertEqual("a=1&b=1&b=2", qs_remove_value(test_qs.copy(), ""))

    # -----------------------------------------------------------------------
    # remove_string_case_insensitive
    # -----------------------------------------------------------------------

    def test_remove_string_case_insensitive_single(self):
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
        self.assertEqual(
            remove_string_case_insensitive("fooffo", "foo"),
            "ffo",
        )

    # -----------------------------------------------------------------------
    # truncate_preserve_mark_tags
    # -----------------------------------------------------------------------

    def test_truncate_preserve_mark_tags_no_truncation(self):
        self.assertEqual(
            truncate_preserve_mark_tags("Hello world", 50),
            "Hello world",
        )

    def test_truncate_preserve_mark_tags_simple_truncation(self):
        self.assertEqual(
            truncate_preserve_mark_tags("Hello world", 5),
            "Hello…",
        )

    def test_truncate_preserve_mark_tags_with_mark_no_truncation(self):
        self.assertEqual(
            truncate_preserve_mark_tags("Hello <mark>world</mark>", 20),
            "Hello <mark>world</mark>",
        )

    def test_truncate_preserve_mark_tags_truncate_after_mark(self):
        self.assertEqual(
            truncate_preserve_mark_tags("Hi <mark>there</mark> friend", 9),
            "Hi <mark>there</mark> …",
        )

    def test_truncate_preserve_mark_tags_truncate_inside_mark_content(self):
        self.assertEqual(
            truncate_preserve_mark_tags("<mark>abcdefghij</mark>", 5),
            "<mark>abcde</mark>…",
        )

    def test_truncate_preserve_mark_tags_multiple_marks(self):
        self.assertEqual(
            truncate_preserve_mark_tags(
                "A <mark>quick</mark> brown <mark>fox</mark> jumps", 17
            ),
            "A <mark>quick</mark> brown <mark>fox</mark>…",
        )

    def test_truncate_preserve_mark_tags_adjacent_marks(self):
        self.assertEqual(
            truncate_preserve_mark_tags(
                "<mark>alpha</mark><mark>beta</mark><mark>gamma</mark>", 12
            ),
            "<mark>alpha</mark><mark>beta</mark><mark>gam</mark>…",
        )

    def test_truncate_preserve_mark_tags_empty_string(self):
        self.assertEqual(
            truncate_preserve_mark_tags("", 10),
            "",
        )

    def test_truncate_preserve_mark_tags_zero_length(self):
        self.assertEqual(
            truncate_preserve_mark_tags("Content", 0),
            "",
        )

    def test_truncate_preserve_mark_tags_only_mark_tag(self):
        """Content fits exactly within the mark — no truncation, no ellipsis."""
        self.assertEqual(
            truncate_preserve_mark_tags("<mark>content</mark>", 7),
            "<mark>content</mark>",
        )

    def test_truncate_preserve_mark_tags_uses_default_max_length_when_omitted(
        self,
    ):
        long_text = "a" * 300
        self.assertEqual(
            truncate_preserve_mark_tags(long_text),
            "a" * 250 + "…",
        )

    def test_truncate_preserve_mark_tags_none_input_returns_empty_string(self):
        """Pin down the contract: None input becomes empty string."""
        self.assertEqual(truncate_preserve_mark_tags(None, 10), "")

    def test_truncate_preserve_mark_tags_non_coercible_max_length(self):
        """
        Documents current behaviour: an uncoercible max_length returns the
        input unchanged. Flagged in code review as questionable — this test
        pins the behaviour so any future change is deliberate.
        """
        self.assertEqual(
            truncate_preserve_mark_tags("hello", "oops"),
            "hello",
        )

    def test_truncate_preserve_mark_tags_strips_non_mark_html(self):
        """Non-mark HTML should be stripped; only <mark> tags survive."""
        self.assertEqual(
            truncate_preserve_mark_tags("<p>Hello <mark>world</mark></p>", 50),
            "Hello <mark>world</mark>",
        )

    def test_truncate_preserve_mark_tags_exact_length_no_ellipsis(self):
        """
        When visible length equals max_length exactly, no truncation has
        occurred and no ellipsis should be appended.
        """
        self.assertEqual(
            truncate_preserve_mark_tags("hello", 5),
            "hello",
        )

    def test_truncate_preserve_mark_tags_exact_length_with_mark_no_ellipsis(
        self,
    ):
        """Same boundary, wrapped in a <mark> tag."""
        self.assertEqual(
            truncate_preserve_mark_tags("<mark>hello</mark>", 5),
            "<mark>hello</mark>",
        )

    def test_truncate_preserve_mark_tags_one_over_length_appends_ellipsis(
        self,
    ):
        """One character over the limit must still produce an ellipsis."""
        self.assertEqual(
            truncate_preserve_mark_tags("hello!", 5),
            "hello…",
        )

    # -----------------------------------------------------------------------
    # parse_json
    # -----------------------------------------------------------------------

    def test_parse_json_valid_input(self):
        self.assertEqual(parse_json('{"a": 1}'), {"a": 1})

    def test_parse_json_url_encoded_input(self):
        """parse_json calls unquote before json.loads."""
        self.assertEqual(parse_json("%7B%22a%22%3A%201%7D"), {"a": 1})

    def test_parse_json_invalid_input_returns_empty_dict(self):
        self.assertEqual(parse_json("not json"), {})

    def test_parse_json_empty_string_returns_empty_dict(self):
        self.assertEqual(parse_json(""), {})

    def test_parse_json_none_returns_empty_dict(self):
        """None input is swallowed by the broad except clause."""
        self.assertEqual(parse_json(None), {})

    # -----------------------------------------------------------------------
    # base64_encode / base64_decode
    # -----------------------------------------------------------------------

    def test_base64_encode_decode_round_trip(self):
        original = "hello world"
        self.assertEqual(base64_decode(base64_encode(original)), original)

    def test_base64_encode_unicode(self):
        original = "café naïve"
        self.assertEqual(base64_decode(base64_encode(original)), original)

    def test_base64_decode_empty_string(self):
        self.assertEqual(base64_decode(""), "")

    def test_base64_decode_none(self):
        self.assertEqual(base64_decode(None), "")

    def test_base64_decode_invalid_returns_empty_string(self):
        """Invalid base64 is swallowed by the broad except clause."""
        self.assertEqual(base64_decode("!!!not-base64!!!"), "")

    def test_base64_decode_handles_missing_padding(self):
        """The decode function adds padding before decoding."""
        # 'hello' base64-encoded is 'aGVsbG8=' — strip the padding
        self.assertEqual(base64_decode("aGVsbG8"), "hello")

    # -----------------------------------------------------------------------
    # sanitize_search_qs
    # -----------------------------------------------------------------------

    def test_sanitize_search_qs_allowed_keys_survive(self):
        """Common allowlisted keys round-trip through the sanitiser."""
        original_qs = "q=test&group=tna&sort=relevance"
        encoded = base64_encode(original_qs)
        result = sanitize_search_qs(encoded)

        # Parse both sides for order-independent comparison.
        result_qs = QueryDict(result)
        self.assertEqual(result_qs.get("q"), "test")
        self.assertEqual(result_qs.get("group"), "tna")
        self.assertEqual(result_qs.get("sort"), "relevance")

    def test_sanitize_search_qs_disallowed_keys_stripped(self):
        """Keys not in the allowlist are silently dropped."""
        original_qs = "q=test&evil=injection&__internal=secret"
        encoded = base64_encode(original_qs)
        result = sanitize_search_qs(encoded)

        result_qs = QueryDict(result)
        self.assertEqual(result_qs.get("q"), "test")
        self.assertIsNone(result_qs.get("evil"))
        self.assertIsNone(result_qs.get("__internal"))

    def test_sanitize_search_qs_empty_values_stripped(self):
        """Empty values for allowed keys are dropped."""
        original_qs = "q=test&sort="
        encoded = base64_encode(original_qs)
        result = sanitize_search_qs(encoded)

        result_qs = QueryDict(result)
        self.assertEqual(result_qs.get("q"), "test")
        self.assertIsNone(result_qs.get("sort"))

    def test_sanitize_search_qs_invalid_base64_returns_empty(self):
        self.assertEqual(sanitize_search_qs("!!!not-base64!!!"), "")

    def test_sanitize_search_qs_empty_input_returns_empty(self):
        self.assertEqual(sanitize_search_qs(""), "")

    def test_sanitize_search_qs_empty_decoded_returns_empty(self):
        """Valid base64 decoding to an empty string returns empty."""
        self.assertEqual(sanitize_search_qs(base64_encode("")), "")

    def test_sanitize_search_qs_page_param_preserved(self):
        """The 'page' key is explicitly in the allowlist."""
        encoded = base64_encode("q=test&page=3")
        result = sanitize_search_qs(encoded)
        result_qs = QueryDict(result)
        self.assertEqual(result_qs.get("page"), "3")

    def test_sanitize_search_qs_multi_value_keys_preserved(self):
        """Allowed keys with multiple values keep all of them."""
        encoded = base64_encode("level=Item&level=Series")
        result = sanitize_search_qs(encoded)
        result_qs = QueryDict(result)
        self.assertEqual(sorted(result_qs.getlist("level")), ["Item", "Series"])

    # -----------------------------------------------------------------------
    # now_iso_8601 / now_iso_8601_date
    # -----------------------------------------------------------------------

    def test_now_iso_8601_format(self):
        """Output should match the ISO 8601 'Z'-suffixed format."""
        result = now_iso_8601()
        self.assertRegex(result, r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

    def test_now_iso_8601_date_format(self):
        """Output should be a YYYY-MM-DD date."""
        result = now_iso_8601_date()
        self.assertRegex(result, r"^\d{4}-\d{2}-\d{2}$")

    @patch("config.jinja_filters.datetime")
    def test_now_iso_8601_uses_current_time(self, mock_datetime):
        from datetime import datetime as real_datetime
        from datetime import timezone

        fixed = real_datetime(2025, 6, 15, 12, 30, 45, tzinfo=timezone.utc)
        mock_datetime.now.return_value = fixed

        self.assertEqual(now_iso_8601(), "2025-06-15T12:30:45Z")

    @patch("config.jinja_filters.datetime")
    def test_now_iso_8601_date_uses_current_time(self, mock_datetime):
        from datetime import datetime as real_datetime

        fixed = real_datetime(2025, 6, 15, 12, 30, 45)
        mock_datetime.now.return_value = fixed

        self.assertEqual(now_iso_8601_date(), "2025-06-15")

    # -----------------------------------------------------------------------
    # override_tna_record_count
    # -----------------------------------------------------------------------

    def test_override_tna_record_count_parametrized(self):
        cases = [
            ("12345678", True, "Over 27 million"),
            ("12,345,678", False, "12,345,678"),
            ("321", None, "321"),
            ("654", "", "654"),
        ]
        for value, is_tna, expected in cases:
            with self.subTest(value=value, is_tna=is_tna):
                record = SimpleNamespace(is_tna=is_tna)
                self.assertEqual(override_tna_record_count(value, record), expected)

    # -----------------------------------------------------------------------
    # none_to_empty_string
    # -----------------------------------------------------------------------

    def test_none_to_empty_string_none(self):
        self.assertEqual(none_to_empty_string(None), "")

    def test_none_to_empty_string_passes_through_non_none(self):
        self.assertEqual(none_to_empty_string("some value"), "some value")
        self.assertEqual(none_to_empty_string(""), "")
        # Documents current behaviour: only None is converted; 0/False survive.
        self.assertEqual(none_to_empty_string(0), 0)
        self.assertEqual(none_to_empty_string(False), False)

    def test_now_iso_8601_returns_utc_not_local_time(self):
        """
        TDD: prove that now_iso_8601 returns UTC, not local time.

        The 'Z' suffix in the output means UTC. If the function uses a naive
        datetime.now() and the server runs in a non-UTC timezone, the output
        will claim to be UTC but actually be local time — silently wrong.

        This test simulates a server in UTC+1 and asserts that calling the
        function at 14:00 local (= 13:00 UTC) returns the UTC value.
        """
        from datetime import datetime as real_datetime
        from datetime import timedelta, timezone

        fake_tz = timezone(timedelta(hours=1))
        # Same instant in time, expressed two ways:
        local_now = real_datetime(2025, 7, 15, 14, 0, 0, tzinfo=fake_tz)
        utc_equivalent = local_now.astimezone(timezone.utc)
        # utc_equivalent is 2025-07-15 13:00:00+00:00

        with patch("config.jinja_filters.datetime") as mock_datetime:
            # datetime.now() with no args returns naive local time on a real
            # server; we simulate that by stripping tzinfo from local_now.
            # datetime.now(timezone.utc) returns the UTC-aware equivalent.
            def fake_now(tz=None):
                if tz is None:
                    return local_now.replace(tzinfo=None)
                return utc_equivalent

            mock_datetime.now.side_effect = fake_now

            result = now_iso_8601()

        # If the function is correct (uses UTC), result is 09:00:00Z.
        # If the function is buggy (uses naive local), result is 14:00:00Z
        # — which is wrong, because the 'Z' claims UTC but the value is local.
        self.assertEqual(result, "2025-07-15T13:00:00Z")
