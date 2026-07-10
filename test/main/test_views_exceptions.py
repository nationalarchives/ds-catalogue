from http import HTTPStatus
from unittest.mock import patch

import responses
from django.conf import settings
from django.core.cache import cache
from django.test import TestCase


class CatalogueViewExceptionsTests(TestCase):
    """Tests error logging for the catalogue view"""

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    @responses.activate
    @patch("app.main.views.fetch_global_notifications", return_value=None)
    @patch("app.main.views.get_explore_the_collection", return_value={})
    def test_catalogue_view_subjects_error(
        self,
        mock_get_explore_the_collection,
        mock_fetch_global_notifications,
    ):
        """Test that the catalogue view handles errors in fetching subjects gracefully
        and logs the error.
        Patch the fetch_global_notifications and get_explore_the_collection functions to
        return empty values to isolate the test to the subjects fetching logic."""

        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            status=HTTPStatus.OK,
            body="TEST",  # non-JSON response
        )

        with self.assertLogs("app.main.cache", level="ERROR") as lc:
            response = self.client.get("/catalogue/")
            # The page does not raise an exception
            self.assertEqual(response.status_code, HTTPStatus.OK)
            context_data = response.context_data

        # test error logging
        self.assertIn(
            "ERROR:app.main.cache:Failed to fetch all Subjects: Non-JSON response provided",
            lc.output,
        )
        # test that the context contains the expected data
        expected_disabled_letters = [
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
            "I",
            "J",
            "K",
            "L",
            "M",
            "N",
            "O",
            "P",
            "Q",
            "R",
            "S",
            "T",
            "U",
            "V",
            "W",
            "X",
            "Y",
            "Z",
        ]
        expected_subjects_grouped_by_letter = {
            "A": [],
            "B": [],
            "C": [],
            "D": [],
            "E": [],
            "F": [],
            "G": [],
            "H": [],
            "I": [],
            "J": [],
            "K": [],
            "L": [],
            "M": [],
            "N": [],
            "O": [],
            "P": [],
            "Q": [],
            "R": [],
            "S": [],
            "T": [],
            "U": [],
            "V": [],
            "W": [],
            "X": [],
            "Y": [],
            "Z": [],
        }
        self.assertEqual(
            context_data.get("subjects_grouped_by_letter"),
            expected_subjects_grouped_by_letter,
        )
        self.assertEqual(
            context_data.get("disabled_letters"), expected_disabled_letters
        )

        # test other error logging for the catalogue view
        with self.assertLogs("app.lib.api", level="ERROR") as lc:
            _ = self.client.get("/catalogue/")
        self.assertIn(
            "ERROR:app.lib.api:JSON API provided non-JSON response", lc.output
        )
        self.assertIn("ERROR:app.lib.api:Non-JSON response: TEST", lc.output)
