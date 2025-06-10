import responses
from app.records.models import Record
from app.search.buckets import BucketKeys
from django.conf import settings
from django.test import TestCase
from django.utils.encoding import force_str


class CatalogueSearchViewTests(TestCase):

    @responses.activate
    def test_catalogue_search_view(self):

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
            status=200,
        )

        response = self.client.get("/catalogue/search/")

        self.assertEqual(response.status_code, 200)

        self.assertIsInstance(response.context_data.get("results"), list)
        self.assertEqual(len(response.context_data.get("results")), 1)
        self.assertIsInstance(response.context_data.get("results")[0], Record)
        self.assertEqual(
            response.context_data.get("stats"),
            {"total": 26008838, "results": 20},
        )
        self.assertEqual(
            response.context_data.get("results_range"), {"from": 1, "to": 20}
        )
        self.assertEqual(response.context_data.get("selected_filters"), [])
        self.assertEqual(
            response.context_data.get("pagination"),
            {
                "items": [
                    {"number": "1", "href": "?page=1", "current": True},
                    {"number": "2", "href": "?page=2", "current": False},
                    {"ellipsis": True},
                    {"number": "500", "href": "?page=500", "current": False},
                ],
                "next": {"href": "?page=2", "title": "Next page of results"},
            },
        )
        self.assertEqual(
            response.context_data.get("bucket_list").items,
            [
                {
                    "name": "Records at the National Archives (1)",
                    "href": "?group=tna",
                    "current": True,
                },
                {
                    "name": "Records at other UK archives (0)",
                    "href": "?group=nonTna",
                    "current": False,
                },
            ],
        )
        self.assertEqual(response.context_data.get("bucket_keys"), BucketKeys)

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
        response_group_tna_online = self.client.get("/catalogue/search/?group=tna&online=true")
        html_checked = force_str(response_group_tna_online.content)
        self.assertIn('name="online" checked', html_checked)

        # Assert the online checkbox is not included if group is set to 'nonTna'
        non_tna_response = self.client.get("/catalogue/search/?group=nonTna")
        self.assertNotIn('name="online"', force_str(non_tna_response.content))
