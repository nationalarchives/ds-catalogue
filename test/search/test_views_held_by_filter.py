import responses
from app.records.models import Record
from app.search.forms import FieldsConstant
from django.conf import settings
from django.test import TestCase


class CatalogueSearchViewHeldByFilterTests(TestCase):
    """Mainly tests the context.
    Held by filter is only available for nonTna group."""

    def setUp(self):
        self.maxDiff = None

    @responses.activate
    def test_catalogue_search_context_for_held_by(
        self,
    ):

        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [
                    {
                        "@template": {
                            "details": {
                                "iaid": "89d4c544-3d43-43a7-ae95-79e3bba0c25b",
                                "heldBy": "Devon Archives and Local Studies Service (South West Heritage Trust)",
                                "referenceNumber": "4420M/Z 13",
                            }
                        }
                    },
                    {
                        "@template": {
                            "details": {
                                "iaid": "C3828406",
                                "heldBy": "National Library of Wales: Department of Collection Services",
                                "referenceNumber": "WALE 20/160",
                            }
                        }
                    },
                ],
                "aggregations": [
                    {
                        "name": "heldBy",
                        "entries": [
                            {
                                "value": "Devon Archives and Local Studies Service (South West Heritage Trust)",
                                "doc_count": 1,
                            },
                            {
                                "value": "National Library of Wales: Department of Collection Services",
                                "doc_count": 1,
                            },
                        ],
                    }
                ],
                "buckets": [
                    {
                        "name": "group",
                        "entries": [
                            {"value": "nonTna", "count": 25},
                        ],
                        "total": 100,
                        "other": 0,
                    }
                ],
                "stats": {
                    "total": 2,
                    "results": 20,
                },
            },
        )

        response = self.client.get(
            "/catalogue/search/?group=nonTna&held_by=Devon Archives and Local Studies Service (South West Heritage Trust)&held_by=National Library of Wales: Department of Collection Services"
        )
        context_data = response.context_data
        form = context_data.get("form")
        held_by_field = form.fields[FieldsConstant.HELD_BY]

        self.assertEqual(form.is_valid(), True)

        self.assertIsInstance(context_data.get("results"), list)
        self.assertEqual(len(context_data.get("results")), 2)
        self.assertIsInstance(context_data.get("results")[0], Record)
        self.assertEqual(
            context_data.get("stats"),
            {"total": 2, "results": 20},
        )

        self.assertEqual(
            context_data.get("results_range"),
            {"from": 1, "to": 20},
        )

        self.assertEqual(held_by_field.choices_updated, True)

        self.assertEqual(
            held_by_field.value,
            [
                "Devon Archives and Local Studies Service (South West Heritage Trust)",
                "National Library of Wales: Department of Collection Services",
            ],
        )
        self.assertEqual(
            held_by_field.cleaned,
            [
                "Devon Archives and Local Studies Service (South West Heritage Trust)",
                "National Library of Wales: Department of Collection Services",
            ],
        )
        self.assertEqual(
            held_by_field.items,
            [
                {
                    "text": "Devon Archives and Local Studies Service (South West Heritage Trust) (1)",
                    "value": "Devon Archives and Local Studies Service (South West Heritage Trust)",
                    "checked": True,
                },
                {
                    "text": "National Library of Wales: Department of Collection Services (1)",
                    "value": "National Library of Wales: Department of Collection Services",
                    "checked": True,
                },
            ],
        )
        self.assertEqual(
            context_data.get("selected_filters"),
            [
                {
                    "label": "Held by: Devon Archives and Local Studies Service (South West Heritage Trust)",
                    "href": "?group=nonTna&held_by=National+Library+of+Wales%3A+Department+of+Collection+Services",
                    "title": "Remove Devon Archives and Local Studies Service (South West Heritage Trust) held by",
                },
                {
                    "label": "Held by: National Library of Wales: Department of Collection Services",
                    "href": "?group=nonTna&held_by=Devon+Archives+and+Local+Studies+Service+%28South+West+Heritage+Trust%29",
                    "title": "Remove National Library of Wales: Department of Collection Services held by",
                },
            ],
        )
        self.assertEqual(
            held_by_field.more_filter_choices_available,
            False,
        )
        self.assertEqual(held_by_field.more_filter_choices_url, "")
        self.assertEqual(held_by_field.more_filter_choices_text, "")

    @responses.activate
    def test_catalogue_search_context_for_held_by_does_not_exist(
        self,
    ):

        # data is empty, but bucket has count for nonTna group
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [],
                "aggregations": [{"name": "heldBy", "total": 0, "other": 0}],
                "buckets": [
                    {
                        "name": "group",
                        "entries": [
                            {"value": "nonTna", "count": 25},
                        ],
                        "total": 100,
                        "other": 0,
                    }
                ],
                "stats": {
                    "total": 0,
                    "results": 0,
                },
            },
        )

        response = self.client.get(
            "/catalogue/search/?group=nonTna&held_by=DOESNOTEXIST"
        )

        context_data = response.context_data
        form = context_data.get("form")
        held_by_field = form.fields["held_by"]

        self.assertEqual(form.is_valid(), True)

        self.assertEqual(context_data.get("results"), [])
        self.assertEqual(context_data.get("results_range"), None)
        self.assertEqual(context_data.get("pagination"), None)

        self.assertEqual(held_by_field.choices_updated, True)

        self.assertEqual(held_by_field.value, ["DOESNOTEXIST"])
        self.assertEqual(
            held_by_field.cleaned,
            ["DOESNOTEXIST"],
        )
        self.assertEqual(held_by_field.choices_updated, True)
        self.assertEqual(
            held_by_field.items,
            [
                {
                    "checked": True,
                    "text": "DOESNOTEXIST (0)",
                    "value": "DOESNOTEXIST",
                }
            ],
        )
        self.assertEqual(
            context_data.get("selected_filters"),
            [
                {
                    "label": "Held by: DOESNOTEXIST",
                    "href": "?group=nonTna",
                    "title": "Remove DOESNOTEXIST held by",
                },
            ],
        )
        self.assertEqual(
            held_by_field.more_filter_choices_available,
            False,
        )
