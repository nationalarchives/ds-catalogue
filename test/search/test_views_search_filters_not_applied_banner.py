from http import HTTPStatus

import responses
from django.conf import settings
from django.test import TestCase
from django.utils.encoding import force_str


class CatalogueSearchFiltersNotAppliedTests(TestCase):
    """"""

    @responses.activate
    def test_filters_not_applied_banner_for_tna(
        self,
    ):
        """Tests banner for TNA search - filters not applicable to tna"""

        # data present for input
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [
                    {
                        "@template": {
                            "details": {
                                "id": "C123456",
                                "source": "CAT",
                            }
                        }
                    }
                ],
                "aggregations": [
                    {
                        "name": "collection",
                        "entries": [
                            {"value": "BT", "doc_count": 50},
                            {"value": "WO", "doc_count": 35},
                        ],
                        "total": 100,
                        "other": 50,
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

        query = (
            "/catalogue/search/"
            "?group=tna"
            "&display=list"
            "&held_by=Lancashire+Archives"  # non tna filter not applicable to tna
        )
        response = self.client.get(query)
        html = force_str(response.content)
        form = response.context_data.get("form")
        self.assertTrue(form.is_valid())

        # tests spefific banner text in template
        self.assertIn("Some filters have not been applied", html)

    @responses.activate
    def test_filters_not_applied_banner_for_nontna_grid_view(
        self,
    ):
        """Tests banner for NON TNA search - filters not applicable to non tna with Grid view"""

        # data present for input
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [
                    {
                        "@template": {
                            "details": {
                                "id": "C123456",
                                "source": "CAT",
                            }
                        }
                    }
                ],
                "aggregations": [
                    {
                        "name": "heldBy",
                        "entries": [
                            {"value": "Lancashire Archives", "doc_count": 1},
                        ],
                        "total": 1,
                        "other": 0,
                    }
                ],
                "buckets": [
                    {
                        "name": "group",
                        "entries": [
                            {"value": "nonTna", "count": 1},
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

        query = (
            "/catalogue/search/"
            "?group=nonTna"
            "&display=grid"
            "&online=true"  # tna filter not applicable to non tna
            "&collection=BT"  # tna filter not applicable to non tna
            "&subject=Military"  # tna filter not applicable to non tna
            "&level=Item"  # tna filter not applicable to non tna
            "&opening_date_from-year=1900"  # tna filter not applicable to non tna
            "&closure=Open+Document%2C+Open+Description"  # tna filter not applicable to non tna
        )
        response = self.client.get(query)
        html = force_str(response.content)
        form = response.context_data.get("form")
        self.assertTrue(form.is_valid())

        # tests spefific banner text in template
        self.assertIn("Some filters have not been applied", html)
