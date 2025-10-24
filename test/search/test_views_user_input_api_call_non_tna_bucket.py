from http import HTTPStatus
from unittest.mock import patch

import responses
from django.conf import settings
from django.test import TestCase


class CatalogueSearchViewDebugAPINonTnaBucketTests(TestCase):
    """Tests API calls (url) made by the catalogue search view for for nonTna bucket/group."""

    @patch("app.lib.api.logger")
    @responses.activate
    def test_catalogue_debug_api_non_tna(self, mock_logger):

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
                # Note: api response is not checked for these values
                "aggregations": [
                    {
                        "name": "heldBy",
                        "entries": [
                            {"value": "somevalue", "doc_count": 100},
                        ],
                    },
                ],
                "buckets": [
                    {
                        "name": "group",
                        "entries": [
                            # Note: api response is not checked for these values
                            {"value": "somevalue", "count": 1},
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

        # with nonTna group param
        self.response = self.client.get("/catalogue/search/?group=nonTna")
        self.assertEqual(self.response.status_code, HTTPStatus.OK)
        mock_logger.debug.assert_called_with(
            "https://rosetta.test/data/search?aggs=heldBy&filter=group%3AnonTna&filter=datatype%3Arecord&q=%2A&size=20"
        )

        # with search term, non tna records
        self.response = self.client.get("/catalogue/search/?group=nonTna&q=ufo")
        self.assertEqual(self.response.status_code, HTTPStatus.OK)
        mock_logger.debug.assert_called_with(
            "https://rosetta.test/data/search?aggs=heldBy&filter=group%3AnonTna&filter=datatype%3Arecord&q=ufo&size=20"
        )

        # with filter not belonging to nontna group (should be ignored)
        self.response = self.client.get(
            "/catalogue/search/?group=nonTna&q=ufo&collection=somecollection&online=true&level=somelevel&subject=Army"
        )
        self.assertEqual(self.response.status_code, HTTPStatus.OK)
        mock_logger.debug.assert_called_with(
            "https://rosetta.test/data/search?aggs=heldBy&filter=group%3AnonTna&filter=datatype%3Arecord&q=ufo&size=20"
        )
