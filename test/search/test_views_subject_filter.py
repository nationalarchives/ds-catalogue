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
                        "name": "subject",
                        "entries": [
                            {"value": "Army", "doc_count": 150},
                            {"value": "Air Force", "doc_count": 75},
                        ],
                        "total": 100,
                        "other": 0,
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
            "/catalogue/search/?q=military&subject=Army&subject=Air Force"
        )
        context_data = response.context_data
        subject_field = context_data.get("form").fields["subject"]

        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Check form field values
        self.assertEqual(
            subject_field.value,
            ["Army", "Air Force"],
        )
        self.assertEqual(
            subject_field.cleaned,
            ["Army", "Air Force"],
        )

        # Check form field items with API counts
        self.assertEqual(
            subject_field.items,
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
            context_data.get("selected_filters"),
            [
                {
                    "label": "Subject: Army",
                    "href": "?q=military&subject=Air+Force",
                    "title": "Remove Army subject",
                },
                {
                    "label": "Subject: Air Force",
                    "href": "?q=military&subject=Army",
                    "title": "Remove Air Force subject",
                },
            ],
        )
        self.assertEqual(
            subject_field.more_filter_choices_available,
            False,
        )
        self.assertEqual(
            subject_field.more_filter_choices_url,
            "",
        )
        self.assertEqual(
            subject_field.more_filter_choices_text,
            "",
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
                        "name": "subject",
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
            "/catalogue/search/?q=test&subject=Army&subject=invalid&subject=999"
        )
        context_data = response.context_data
        subject_field = context_data.get("form").fields["subject"]

        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Form should include all values (valid and invalid)
        self.assertEqual(
            subject_field.value,
            ["Army", "invalid", "999"],
        )

        # Should still be cleaned since validate_input=False for subjects
        self.assertEqual(
            subject_field.cleaned,
            ["Army", "invalid", "999"],
        )

        # Items should show what's available
        self.assertEqual(
            subject_field.items,
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
            context_data.get("selected_filters"),
            [
                {
                    "label": "Subject: Army",
                    "href": "?q=test&subject=invalid&subject=999",
                    "title": "Remove Army subject",
                },
                {
                    "label": "Subject: invalid",
                    "href": "?q=test&subject=Army&subject=999",
                    "title": "Remove invalid subject",
                },
                {
                    "label": "Subject: 999",
                    "href": "?q=test&subject=Army&subject=invalid",
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
                        "name": "subject",
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
        context_data = response.context_data
        subject_field = context_data.get("form").fields["subject"]

        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Check subjects field is empty
        self.assertEqual(
            subject_field.value,
            [],
        )
        self.assertEqual(
            subject_field.cleaned,
            [],
        )

        # Should show available subjects from API without any checked
        self.assertEqual(
            subject_field.items,
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
        self.assertEqual(context_data.get("selected_filters"), [])

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

        response = self.client.get(
            "/catalogue/search/?subject=Army&subject=Navy"
        )
        context_data = response.context_data

        self.assertEqual(response.status_code, HTTPStatus.OK)

        filter_labels = [
            f["label"] for f in context_data.get("selected_filters")
        ]
        self.assertIn("Subject: Army", filter_labels)
        self.assertIn("Subject: Navy", filter_labels)
