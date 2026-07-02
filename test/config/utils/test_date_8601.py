from datetime import UTC, datetime
from unittest.mock import patch

from django.test import SimpleTestCase

from config.utils.date_iso8601 import now_iso_8601, now_iso_8601_date


class NowIso8601TestCase(SimpleTestCase):
    @patch("config.utils.date_iso8601.datetime")
    def test_now_iso_8601_formats_utc_with_zulu(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2026, 6, 23, 17, 25, 56, tzinfo=UTC)
        self.assertEqual(now_iso_8601(), "2026-06-23T17:25:56Z")
        # The trailing 'Z' is only honest if the time was taken in UTC.
        mock_datetime.now.assert_called_once_with(UTC)

    @patch("config.utils.date_iso8601.datetime")
    def test_now_iso_8601_date_formats_utc(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2026, 6, 23, 17, 25, 56, tzinfo=UTC)
        self.assertEqual(now_iso_8601_date(), "2026-06-23")
        mock_datetime.now.assert_called_once_with(UTC)

    def test_now_iso_8601_real_value_matches_zulu_format(self):
        value = now_iso_8601()
        self.assertRegex(value, r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
        # Parses cleanly back to a datetime.
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
