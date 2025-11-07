from http import HTTPStatus

import responses
from django.conf import settings
from django.test import TestCase


class CatalogueSearchViewSortParamTests(TestCase):
    """Mainly tests the context.
    Sort param is available for all groups."""

    @responses.activate
    def test_catalogue_search_context_with_sort_param(self):

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

        response = self.client.get("/catalogue/search/?sort=title:asc")
        sort_field = response.context_data.get("form").fields["sort"]

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(sort_field.id, "id_sort")
        self.assertEqual(sort_field.name, "sort")
        self.assertEqual(sort_field.value, "title:asc")
        self.assertEqual(sort_field.cleaned, "title:asc")
        self.assertEqual(
            sort_field.items,
            [
                {
                    "text": "Relevance",
                    "value": "",
                },
                {
                    "text": "Date (newest first)",
                    "value": "date:desc",
                },
                {"text": "Date (oldest first)", "value": "date:asc"},
                {"text": "Title (A–Z)", "value": "title:asc", "checked": True},
                {"text": "Title (Z–A)", "value": "title:desc"},
            ],
        )
        self.assertEqual(response.context_data.get("selected_filters"), [])
