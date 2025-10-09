from http import HTTPStatus

import responses
from django.conf import settings
from django.test import TestCase


class CatalogueSearchViewSubjectsFilterTests(TestCase):
    """Tests the subjects filter context in the catalogue search view."""

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
                            {"value": "Army", "doc_count": 150},
                            {"value": "Air Force", "doc_count": 75},
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
            "/catalogue/search/?q=military&subjects=Army&subjects=Air Force"
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Check form field values
        self.assertEqual(
            response.context_data.get("form").fields["subjects"].value,
            ["Army", "Air Force"],
        )
        self.assertEqual(
            response.context_data.get("form").fields["subjects"].cleaned,
            ["Army", "Air Force"],
        )

        # Check form field items with API counts
        self.assertEqual(
            response.context_data.get("form").fields["subjects"].items,
            [
                {
                    "text": "Army (150)",
                    "value": "Army",
                    "checked": True,
                },
                {
                    "text": "Air Force (75)",
                    "value": "Air Force",
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
                    "href": "?q=military&subjects=Air+Force",
                    "title": "Remove Army subject",
                },
                {
                    "label": "Subject: Air Force",
                    "href": "?q=military&subjects=Army",
                    "title": "Remove Air Force subject",
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
                            {"value": "Army", "doc_count": 100},
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
            "/catalogue/search/?q=test&subjects=Army&subjects=invalid&subjects=999"
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Form should include all values (valid and invalid)
        self.assertEqual(
            response.context_data.get("form").fields["subjects"].value,
            ["Army", "invalid", "999"],
        )

        # Should still be cleaned since validate_input=False for subjects
        self.assertEqual(
            response.context_data.get("form").fields["subjects"].cleaned,
            ["Army", "invalid", "999"],
        )

        # Items should show what's available
        self.assertEqual(
            response.context_data.get("form").fields["subjects"].items,
            [
                {
                    "text": "Army (100)",
                    "value": "Army",
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
                    "href": "?q=test&subjects=Army&subjects=999",
                    "title": "Remove invalid subject",
                },
                {
                    "label": "Subject: 999",
                    "href": "?q=test&subjects=Army&subjects=invalid",
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
                            {"value": "Army", "doc_count": 100},
                            {"value": "Navy", "doc_count": 50},
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
                    "value": "Army",
                },
                {
                    "text": "Navy (50)",
                    "value": "Navy",
                },
            ],
        )

        # No subject filters should be in selected filters
        self.assertEqual(response.context_data.get("selected_filters"), [])

    @responses.activate
    def test_catalogue_search_context_with_subjects_param(self):
        """Test that subjects parameters are processed correctly."""

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
                            {"value": "Army", "doc_count": 150},
                            {"value": "Navy", "doc_count": 75},
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

        self.response = self.client.get(
            "/catalogue/search/?subjects=Army&subjects=Navy"
        )
        self.assertEqual(self.response.status_code, HTTPStatus.OK)

        filter_labels = [
            f["label"]
            for f in self.response.context_data.get("selected_filters")
        ]
        self.assertIn("Subject: Army", filter_labels)
        self.assertIn("Subject: Navy", filter_labels)
