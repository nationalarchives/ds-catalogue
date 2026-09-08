from django.test import SimpleTestCase

from config.utils.encoding import base64_decode, base64_encode


class Base64TestCase(SimpleTestCase):
    def test_base64_encode_known_value(self):
        self.assertEqual(base64_encode("foo"), "Zm9v")

    def test_base64_encode_uses_url_safe_alphabet(self):
        encoded = base64_encode("favicon?size=64&q=>>>")
        self.assertNotIn("+", encoded)
        self.assertNotIn("/", encoded)

    def test_base64_decode_known_value(self):
        self.assertEqual(base64_decode("Zm9v"), "foo")

    def test_base64_decode_tolerates_missing_padding(self):
        # 'Zm8=' decodes to 'fo'; the decoder re-adds the stripped '=' padding.
        self.assertEqual(base64_decode("Zm8"), "fo")

    def test_base64_decode_empty_or_none_returns_empty(self):
        self.assertEqual(base64_decode(""), "")
        self.assertEqual(base64_decode(None), "")

    def test_base64_decode_garbage_returns_empty(self):
        self.assertEqual(base64_decode("!!!"), "")

    def test_base64_round_trip(self):
        for original in ["", "foo", "hello world", "café ☕", "a=b&c=d"]:
            with self.subTest(original=original):
                self.assertEqual(base64_decode(base64_encode(original)), original)
