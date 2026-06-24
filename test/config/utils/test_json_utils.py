from urllib.parse import quote

from django.test import SimpleTestCase

from config.utils.json_utils import dump_json, parse_json


class DumpJsonTestCase(SimpleTestCase):
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


class ParseJsonTestCase(SimpleTestCase):
    def test_parse_json_object(self):
        self.assertEqual(parse_json('{"a": 1}'), {"a": 1})

    def test_parse_json_url_encoded(self):
        self.assertEqual(
            parse_json(quote('{"a": 1, "b": [2, 3]}')),
            {"a": 1, "b": [2, 3]},
        )

    def test_parse_json_array(self):
        self.assertEqual(parse_json("[1, 2, 3]"), [1, 2, 3])

    def test_parse_json_invalid_returns_empty_dict(self):
        self.assertEqual(parse_json("not json"), {})
        self.assertEqual(parse_json(""), {})

    def test_parse_json_none_returns_empty_dict(self):
        self.assertEqual(parse_json(None), {})
