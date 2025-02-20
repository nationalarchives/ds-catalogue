import responses
from app.lib.api import JSONAPIClient, rosetta_request_handler
from django.conf import settings
from django.test import SimpleTestCase


class TestJSONAPIClientGetRequest(SimpleTestCase):
    def setUp(self):
        self.records_client = JSONAPIClient

    @responses.activate
    def test_response_with_ok_200(self):

        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C123456",
            status=200,
            json={"data": [{"@template": {"details": {"iaid": "C198022"}}}]},
        )

        reponse_dict = rosetta_request_handler(
            uri="get", params={"id": "C123456"}
        )
        self.assertDictEqual(
            reponse_dict,
            {"data": [{"@template": {"details": {"iaid": "C198022"}}}]},
        )
