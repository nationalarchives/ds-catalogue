from http import HTTPStatus

import responses
from django.conf import settings
from django.test import TestCase
from django.utils.encoding import force_str


class CatalogueSearchViewIntegrationTests(TestCase):

    @responses.activate
    def test_catalogue_search_online_checkbox(self):

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

        response = self.client.get("/catalogue/search/")

        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Assert for presence of the unchecked online checkbox where no group is set in request
        response_no_group = self.client.get("/catalogue/search/")
        html = force_str(response_no_group.content)
        self.assertIn('name="online"', html)
        self.assertNotIn('name="online" checked', html)

        # Assert for checked state where there is no group and online is set to true in request
        response_checked = self.client.get("/catalogue/search/?online=true")
        html_checked = force_str(response_checked.content)
        self.assertIn('name="online" checked', html_checked)

        # Assert for presence of the unchecked online checkbox where group is set to 'tna'
        response_group_tna = self.client.get("/catalogue/search/?group=tna")
        html = force_str(response_group_tna.content)
        self.assertIn('name="online"', html)
        self.assertNotIn('name="online" checked', html)

        # Assert for checked state where group is set to 'tna' and online is set to true in request
        response_group_tna_online = self.client.get(
            "/catalogue/search/?group=tna&online=true"
        )
        html_checked = force_str(response_group_tna_online.content)
        self.assertIn('name="online" checked', html_checked)

        # Assert the online checkbox is not included if group is set to 'nonTna'
        non_tna_response = self.client.get("/catalogue/search/?group=nonTna")
        self.assertNotIn('name="online"', force_str(non_tna_response.content))


class CatalogueSearchViewSubjectsIntegrationTests(TestCase):
    """Integration tests for subjects functionality in the catalogue search view."""

    @responses.activate
    def test_subjects_in_dynamic_choice_fields(self):
        """Test that subjects is included in dynamic_choice_fields for API processing."""

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
                        "name": "level",
                        "entries": [
                            {"value": "Item", "doc_count": 100},
                        ],
                    },
                    {
                        "name": "collection",
                        "entries": [
                            {"value": "BT", "doc_count": 50},
                        ],
                    },
                    {
                        "name": "subjects",
                        "entries": [
                            {"value": "2", "doc_count": 75},
                            {"value": "6", "doc_count": 25},
                        ],
                    },
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
                    "total": 1,
                    "results": 1,
                },
            },
            status=HTTPStatus.OK,
        )

        response = self.client.get("/catalogue/search/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Check that subjects field is processed from API aggregations
        subjects_field = response.context_data.get("form").fields["subjects"]

        # Should have items from API aggregation
        self.assertEqual(len(subjects_field.items), 2)
        self.assertEqual(subjects_field.items[0]["text"], "Army (75)")
        self.assertEqual(subjects_field.items[0]["value"], "2")
        self.assertEqual(subjects_field.items[1]["text"], "Navy (25)")
        self.assertEqual(subjects_field.items[1]["value"], "6")

    @responses.activate
    def test_subjects_filter_combination_with_other_filters(self):
        """Test subjects filter working in combination with other filters."""

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
                        "name": "level",
                        "entries": [
                            {"value": "Item", "doc_count": 50},
                        ],
                    },
                    {
                        "name": "subjects",
                        "entries": [
                            {"value": "2", "doc_count": 30},
                        ],
                    },
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
                    "total": 1,
                    "results": 1,
                },
            },
            status=HTTPStatus.OK,
        )

        # Test with multiple filter types including subjects
        response = self.client.get(
            "/catalogue/search/?q=military&level=Item&subjects=2&online=true"
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Check that all filters appear in selected_filters
        selected_filters = response.context_data.get("selected_filters")
        filter_labels = [f["label"] for f in selected_filters]

        self.assertIn("Online only", filter_labels)
        self.assertIn("Level: Item", filter_labels)
        self.assertIn("Subject: Army", filter_labels)

    @responses.activate
    def test_subjects_filter_with_nonTna_group(self):
        """Test that subjects filter is not processed for nonTna group."""

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
                "aggregations": [],
                "buckets": [
                    {
                        "name": "group",
                        "entries": [
                            {"value": "nonTna", "count": 1},
                        ],
                    }
                ],
                "stats": {
                    "total": 1,
                    "results": 1,
                },
            },
            status=HTTPStatus.OK,
        )

        # Test with nonTna group - subjects should not be processed from API
        response = self.client.get("/catalogue/search/?group=nonTna&subjects=2")

        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Subjects field should exist but without API updates
        subjects_field = response.context_data.get("form").fields["subjects"]
        self.assertEqual(subjects_field.value, ["2"])

        # Should still show in selected filters even for nonTna
        selected_filters = response.context_data.get("selected_filters")
        subject_filters = [
            f for f in selected_filters if f["label"].startswith("Subject:")
        ]
        self.assertEqual(len(subject_filters), 1)
        self.assertEqual(subject_filters[0]["label"], "Subject: Army")

    @responses.activate
    def test_subjects_field_error_handling(self):
        """Test error handling for subjects field when API fails."""

        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [],
                "aggregations": [
                    {
                        "name": "subjects",
                        "entries": [],
                    }
                ],
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

        # Test with subjects that have no results
        response = self.client.get("/catalogue/search/?subjects=2&subjects=6")

        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Should handle empty aggregation gracefully
        subjects_field = response.context_data.get("form").fields["subjects"]
        self.assertEqual(subjects_field.value, ["2", "6"])

        # Should show selected filters even with no results
        selected_filters = response.context_data.get("selected_filters")
        subject_filters = [
            f for f in selected_filters if f["label"].startswith("Subject:")
        ]
        self.assertEqual(len(subject_filters), 2)

        @responses.activate
        def test_subjects_template_rendering(self):
            """Test that subjects are properly rendered in the template."""

            responses.add(
                responses.GET,
                f"{settings.ROSETTA_API_URL}/search",
                json={
                    "data": [],
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

            response = self.client.get("/catalogue/search/?subjects=Army")

            self.assertEqual(response.status_code, HTTPStatus.OK)

            # Check that subjects appear in the rendered HTML
            html = force_str(response.content)

            # Should have subjects checkboxes
            self.assertIn('name="subjects"', html)
            self.assertIn('value="Army"', html)
            self.assertIn('value="Navy"', html)

            # Should show subject labels with counts
            self.assertIn("Army (100)", html)
            self.assertIn("Navy (50)", html)

            # Check that subjects section is rendered for TNA group
            self.assertIn("Subjects", html)

    def test_subjects_constant_value(self):
        """Test that SUBJECTS constant has correct value."""
        from app.search.forms import FieldsConstant

        self.assertEqual(FieldsConstant.SUBJECTS, "subjects")

        # Make sure it's different from other constants
        self.assertNotEqual(FieldsConstant.SUBJECTS, FieldsConstant.COLLECTION)
        self.assertNotEqual(FieldsConstant.SUBJECTS, FieldsConstant.LEVEL)
