import responses
from app.records.models import Record
from django.conf import settings
from django.test import TestCase


class TestRecordView(TestCase):

    @responses.activate
    def test_record_detail_view_for_catalogue_record(self):

        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C123456",
            json={
                "data": [
                    {
                        "@template": {
                            "details": {
                                "iaid": "C123456",
                                "title": "Test Title",
                                "source": "CAT",
                                "heldByCount": 100,
                            }
                        }
                    }
                ]
            },
            status=200,
        )

        response = self.client.get("/catalogue/id/C123456/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.view_name, "records:details")
        self.assertTemplateUsed("records/record_detail.html")

        self.assertIsInstance(response.context_data.get("record"), Record)

    @responses.activate
    def test_record_detail_view_for_archive_record(self):

        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=A13530600",
            json={
                "data": [
                    {
                        "@template": {
                            "details": {
                                "iaid": "A13530600",
                                "title": "Test Title",
                                "source": "ARCHON",
                            }
                        }
                    }
                ]
            },
            status=200,
        )

        response = self.client.get("/catalogue/id/A13530600/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.view_name, "records:details")
        self.assertTemplateUsed("records/archon_detail.html")

        self.assertIsInstance(response.context_data.get("record"), Record)
