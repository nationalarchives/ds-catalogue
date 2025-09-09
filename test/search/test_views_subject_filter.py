from http import HTTPStatus

import responses
from django.conf import settings
from django.test import TestCase


class CatalogueSearchViewSubjectsFilterTests(TestCase):
    """Tests the subjects filter functionality in the catalogue search view."""

    @responses.activate
    def test_catalogue_search_context_with_valid_subjects_params(self):
        """Test that valid subjects parameters are processed correctly."""

        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [
                    {
                        "@template": {
                            "details": {
                                "iaid": "C123456",
                                "source": "CAT",
                            }
                        }
                    }
                ],
                "aggregations": [
                    {
                        "name": "subjects",
                        "entries": [
                            {"value": "2", "doc_count": 150},
                            {"value": "18", "doc_count": 75},
                        ],
                    }
                ],
                "buckets": [
                    {
                        "name": "group",
                        "entries": [
                            {"value": "tna", "count": 1},
                        ],
                    }
                ],
                "stats": {
                    "total": 26008838,
                    "results": 20,
                },
            },
            status=HTTPStatus.OK,
        )

        # Test with multiple valid subjects parameters
        response = self.client.get(
            "/catalogue/search/?q=military&subjects=2&subjects=18"
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Check form field values
        self.assertEqual(
            response.context_data.get("form").fields["subjects"].value,
            ["2", "18"],
        )
        self.assertEqual(
            response.context_data.get("form").fields["subjects"].cleaned,
            ["2", "18"],
        )

        # Check form field items with API counts
        self.assertEqual(
            response.context_data.get("form").fields["subjects"].items,
            [
                {
                    "text": "Army (150)",
                    "value": "2",
                    "checked": True,
                },
                {
                    "text": "Air Force (75)",
                    "value": "18",
                    "checked": True,
                },
            ],
        )

        # Check selected filters
        self.assertEqual(
            response.context_data.get("selected_filters"),
            [
                {
                    "label": "Subject: Army",
                    "href": "?q=military&subjects=18",
                    "title": "Remove Army subject",
                },
                {
                    "label": "Subject: Air Force",
                    "href": "?q=military&subjects=2",
                    "title": "Remove Air Force subject",
                },
            ],
        )

    @responses.activate
    def test_catalogue_search_context_with_subjects_no_api_results(self):
        """Test subjects parameters when API returns no matching results."""

        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [
                    {
                        "@template": {
                            "details": {
                                "iaid": "C123456",
                                "source": "CAT",
                            }
                        }
                    }
                ],
                "aggregations": [
                    {
                        "name": "subjects",
                        "entries": [
                            {"value": "6", "doc_count": 50},
                        ],
                    }
                ],
                "buckets": [
                    {
                        "name": "group",
                        "entries": [
                            {"value": "tna", "count": 1},
                        ],
                    }
                ],
                "stats": {
                    "total": 26008838,
                    "results": 20,
                },
            },
            status=HTTPStatus.OK,
        )

        # Test with subjects where some have results and some don't
        response = self.client.get(
            "/catalogue/search/?q=navy&subjects=2&subjects=6&subjects=99"
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Check form field values include all selected subjects
        self.assertEqual(
            response.context_data.get("form").fields["subjects"].value,
            ["2", "6", "99"],
        )
        self.assertEqual(
            response.context_data.get("form").fields["subjects"].cleaned,
            ["2", "6", "99"],
        )

        # Check items show counts from API and 0 for missing ones
        self.assertEqual(
            response.context_data.get("form").fields["subjects"].items,
            [
                {
                    "text": "Navy (50)",
                    "value": "6",
                    "checked": True,
                },
                {
                    "text": "Army (0)",
                    "value": "2",
                    "checked": True,
                },
                {
                    "text": "Sewerage (0)",
                    "value": "99",
                    "checked": True,
                },
            ],
        )

        # Check selected filters show correct labels
        self.assertEqual(
            response.context_data.get("selected_filters"),
            [
                {
                    "label": "Subject: Army",
                    "href": "?q=navy&subjects=6&subjects=99",
                    "title": "Remove Army subject",
                },
                {
                    "label": "Subject: Navy",
                    "href": "?q=navy&subjects=2&subjects=99",
                    "title": "Remove Navy subject",
                },
                {
                    "label": "Subject: Sewerage",
                    "href": "?q=navy&subjects=2&subjects=6",
                    "title": "Remove Sewerage subject",
                },
            ],
        )

    @responses.activate
    def test_catalogue_search_context_with_invalid_subjects_params(self):
        """Test behavior with invalid subject IDs."""

        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [
                    {
                        "@template": {
                            "details": {
                                "iaid": "C123456",
                                "source": "CAT",
                            }
                        }
                    }
                ],
                "aggregations": [
                    {
                        "name": "subjects",
                        "entries": [
                            {"value": "2", "doc_count": 100},
                        ],
                    }
                ],
                "buckets": [
                    {
                        "name": "group",
                        "entries": [
                            {"value": "tna", "count": 1},
                        ],
                    }
                ],
                "stats": {
                    "total": 26008838,
                    "results": 20,
                },
            },
            status=HTTPStatus.OK,
        )

        # Test with valid and invalid subject IDs
        response = self.client.get(
            "/catalogue/search/?q=test&subjects=2&subjects=invalid&subjects=999"
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Form should include all values (valid and invalid)
        self.assertEqual(
            response.context_data.get("form").fields["subjects"].value,
            ["2", "invalid", "999"],
        )

        # Should still be cleaned since validate_input=False for subjects
        self.assertEqual(
            response.context_data.get("form").fields["subjects"].cleaned,
            ["2", "invalid", "999"],
        )

        # Items should show what's available
        self.assertEqual(
            response.context_data.get("form").fields["subjects"].items,
            [
                {
                    "text": "Army (100)",
                    "value": "2",
                    "checked": True,
                },
                {
                    "text": "invalid (0)",
                    "value": "invalid",
                    "checked": True,
                },
                {
                    "text": "999 (0)",
                    "value": "999",
                    "checked": True,
                },
            ],
        )

        # Selected filters should handle invalid IDs gracefully
        self.assertEqual(
            response.context_data.get("selected_filters"),
            [
                {
                    "label": "Subject: Army",
                    "href": "?q=test&subjects=invalid&subjects=999",
                    "title": "Remove Army subject",
                },
                {
                    "label": "Subject: invalid",
                    "href": "?q=test&subjects=2&subjects=999",
                    "title": "Remove invalid subject",
                },
                {
                    "label": "Subject: 999",
                    "href": "?q=test&subjects=2&subjects=invalid",
                    "title": "Remove 999 subject",
                },
            ],
        )

    @responses.activate
    def test_catalogue_search_context_without_subjects_params(self):
        """Test that subjects field works correctly when no subjects are selected."""

        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [
                    {
                        "@template": {
                            "details": {
                                "iaid": "C123456",
                                "source": "CAT",
                            }
                        }
                    }
                ],
                "aggregations": [
                    {
                        "name": "subjects",
                        "entries": [
                            {"value": "2", "doc_count": 100},
                            {"value": "6", "doc_count": 50},
                        ],
                    }
                ],
                "buckets": [
                    {
                        "name": "group",
                        "entries": [
                            {"value": "tna", "count": 1},
                        ],
                    }
                ],
                "stats": {
                    "total": 26008838,
                    "results": 20,
                },
            },
            status=HTTPStatus.OK,
        )

        response = self.client.get("/catalogue/search/?q=test")

        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Check subjects field is empty
        self.assertEqual(
            response.context_data.get("form").fields["subjects"].value,
            [],
        )
        self.assertEqual(
            response.context_data.get("form").fields["subjects"].cleaned,
            [],
        )

        # Should show available subjects from API without any checked
        self.assertEqual(
            response.context_data.get("form").fields["subjects"].items,
            [
                {
                    "text": "Army (100)",
                    "value": "2",
                },
                {
                    "text": "Navy (50)",
                    "value": "6",
                },
            ],
        )

        # No subject filters should be in selected filters
        self.assertEqual(response.context_data.get("selected_filters"), [])

    @responses.activate
    def test_subjects_filter_field_properties(self):
        """Test the subjects field has correct properties."""

        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [],
                "aggregations": [],
                "buckets": [
                    {
                        "name": "group",
                        "entries": [
                            {"value": "tna", "count": 0},
                        ],
                    }
                ],
                "stats": {
                    "total": 0,
                    "results": 0,
                },
            },
            status=HTTPStatus.OK,
        )

        response = self.client.get("/catalogue/search/")

        subjects_field = response.context_data.get("form").fields["subjects"]

        # Check field properties
        self.assertEqual(subjects_field.name, "subjects")
        self.assertEqual(subjects_field.label, "Subjects")
        self.assertFalse(
            subjects_field.validate_input
        )  # Should be False for subjects
        self.assertIn(
            "1", [choice[0] for choice in subjects_field.configured_choices]
        )
        self.assertIn(
            "Armed Forces (General Administration)",
            [choice[1] for choice in subjects_field.configured_choices],
        )
