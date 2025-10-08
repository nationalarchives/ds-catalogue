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
