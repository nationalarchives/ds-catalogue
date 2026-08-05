from types import SimpleNamespace

from django.test import SimpleTestCase

from config.utils.records import normalise_record_field, override_tna_record_count


class OverrideTnaRecordCountTestCase(SimpleTestCase):
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


class SanitiseRecordFieldTestCase(SimpleTestCase):
    def test_collapses_whitespace_between_paragraphs(self):
        source = """  <p>Test</p> <p>Test</p>     <p>Test</p> """
        self.assertEqual(
            normalise_record_field(source),
            "<p>Test</p><p>Test</p><p>Test</p>",
        )
