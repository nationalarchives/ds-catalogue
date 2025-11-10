from http import HTTPStatus

import responses
from django.conf import settings
from django.test import TestCase


class CatalogueSearchViewQueryParamTests(TestCase):
    """Mainly tests the context."""

    @responses.activate
    def test_catalogue_search_context_with_query_param(self):

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

        # get response
        response = self.client.get("/catalogue/search/?q=ufo")
        # get form and fields
        form = response.context_data.get("form")
        q_field = form.fields["q"]

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(q_field.id, "id_q")
        self.assertEqual(q_field.name, "q")
        self.assertEqual(q_field.value, "ufo")
        self.assertEqual(response.context_data.get("selected_filters"), [])

    @responses.activate
    def test_catalogue_search_context_with_unknown_query_returns_no_results(
        self,
    ):
        """Test that unknown filter values result in empty choices and no results,
        with filters having configured choices returning empty choices."""

        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [],
                "aggregations": [
                    {"name": "closure", "total": 0, "other": 0},
                    {"name": "collection", "total": 0, "other": 0},
                    {"name": "level", "total": 0, "other": 0},
                    {"name": "subject", "total": 0, "other": 0},
                ],
                "buckets": [{"name": "group", "total": 0, "other": 0}],
                "stats": {
                    "total": 0,
                    "results": 0,
                },
            },
            status=HTTPStatus.OK,
        )

        # get response
        response = self.client.get("/catalogue/search/?q=qwert")

        # get form and fields
        form = response.context_data.get("form")
        q_field = form.fields["q"]
        # get collection and level fields which have configured choices
        collection_field = form.fields["collection"]
        level_field = form.fields["level"]

        self.assertEqual(response.status_code, HTTPStatus.OK)

        self.assertEqual(response.context_data.get("results"), None)
        self.assertEqual(response.context_data.get("total"), None)

        # no errors, but no results
        self.assertEqual(form.is_valid(), True)
        self.assertEqual(form.errors, {})

        self.assertEqual(q_field.value, "qwert")

        # choices updated by items property from view context
        self.assertEqual(collection_field.choices_updated, True)
        # configured choices should be empty
        self.assertEqual(collection_field.items, [])

        # choices updated by items property from view context
        self.assertEqual(level_field.choices_updated, True)
        # configured choices should be empty
        self.assertEqual(level_field.items, [])

        # filtered selections should be empty
        self.assertEqual(response.context_data.get("selected_filters"), [])
