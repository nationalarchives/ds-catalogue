from datetime import date

from app.records.utils import (
    change_discovery_record_details_links,
    extract,
    format_link,
)
from django.test import SimpleTestCase

TODAY = date.today()


class TestExtract(SimpleTestCase):
    test_data = {
        "item": {
            "id": 2,
            "name": "foo",
            "date_created": TODAY,
            "parent": {
                "id": 1,
                "name": "parent",
                "date_created": TODAY,
            },
            "children": [
                {"id": 3, "name": "bar", "date_created": TODAY},
                {"id": 4, "name": "baz", "date_created": TODAY},
            ],
        }
    }

    def test_successes(self):
        """
        Show that we can extract values via:
        - dict keys
        - sequence indexes
        - object attribute names
        """
        for key, expected_value in (
            ("item", self.test_data["item"]),
            ("item.id", 2),
            ("item.date_created", TODAY),
            ("item.date_created.day", TODAY.day),
            ("item.parent.id", 1),
            ("item.parent.date_created.year", TODAY.year),
            ("item.children.0.id", 3),
            ("item.children.0.date_created.month", TODAY.month),
            ("item.children.1.id", 4),
            ("item.children.1.date_created.month", TODAY.month),
        ):
            with self.subTest(key):
                self.assertEqual(
                    extract(self.test_data, key),
                    expected_value,
                )

    def test_with_defaults(self):
        """
        Shows that wherever in the process the failure happens, no exception
        is raised, and the default value is returned.
        """
        for key, default_value in (
            ("item_2", "somestring"),
            ("item.invalid_key", 1),
            ("item.date_created.invalid_attr", None),
            ("item.children.invalid_index", TODAY),
            ("item.children.999", None),
            ("item.children.1.invalid_key", False),
            ("item.children.1.date_created.invalid_attr", True),
        ):
            with self.subTest(key):
                self.assertIs(
                    extract(self.test_data, key, default=default_value),
                    default_value,
                )


class TestFormatLink(SimpleTestCase):
    def test_format_link(self):
        test_data = (
            (
                "valid link",
                '<a href="C5789">DEFE 31</a>',
                {
                    "id": "C5789",
                    "href": "/catalogue/id/C5789/",
                    "text": "DEFE 31",
                },
            ),
        )

        for label, value, expected in test_data:
            with self.subTest(label):
                result = format_link(value)
                self.assertEqual(result, expected)

    def test_format_link_with_missing_id_data(self):
        """Tests handling of missing data received from API response."""

        test_data = (
            (
                "missing id",
                "some value",
                {"id": "", "href": "", "text": "some value"},
            ),
        )

        for label, value, expected in test_data:
            with self.subTest(label):
                result = format_link(value)
                self.assertEqual(result, expected)


class TestChangeDiscoveryRecordDetailsLinks(SimpleTestCase):
    def test_change_discovery_record_details_links(self):
        test_data = (
            (
                "valid link",
                '<a href="https://discovery.nationalarchives.gov.uk/details/r/C361/">C361</a>',
                '<a href="/catalogue/id/C361/">C361</a>',
            ),
            (
                "valid link without https",
                '<a href="http://discovery.nationalarchives.gov.uk/details/r/C361/">C361</a>',
                '<a href="/catalogue/id/C361/">C361</a>',
            ),
            (
                "valid link without trailing slash",
                '<a href="https://discovery.nationalarchives.gov.uk/details/r/C361">C361</a>',
                '<a href="/catalogue/id/C361/">C361</a>',
            ),
            (
                "invalid ID",
                '<a href="https://discovery.nationalarchives.gov.uk/details/r/notvalid/">C361</a>',
                '<a href="/catalogue/id/notvalid/">C361</a>',
            ),
            (
                "valid link with blank target",
                '<a href="https://discovery.nationalarchives.gov.uk/details/r/C361/" title="Opens in a new tab" target="_blank">C361</a>',
                '<a href="/catalogue/id/C361/">C361</a>',
            ),
            (
                "search UI link",
                '<a href="http://discovery.nationalarchives.gov.uk/SearchUI/details?Uri=C5224">(otherwise in CO 1035)</a>',
                '<a href="/catalogue/id/C5224/">(otherwise in CO 1035)</a>',
            ),
        )

        for label, value, expected in test_data:
            with self.subTest(label):
                result = change_discovery_record_details_links(value)
                self.assertEqual(result, expected)
