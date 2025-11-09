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
        response = self.client.get("/catalogue/search/?group=nonTna")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        mock_logger.debug.assert_called_with(
            "https://rosetta.test/data/search?"
            "filter=group%3AnonTna"
            "&filter=datatype%3Arecord"
            "&aggs=heldBy"
            "&q=%2A"
            "&size=20"
            "&from=0"
        )

        # with search term, non tna records
        response = self.client.get("/catalogue/search/?group=nonTna&q=ufo")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        mock_logger.debug.assert_called_with(
            "https://rosetta.test/data/search?"
            "filter=group%3AnonTna"
            "&filter=datatype%3Arecord"
            "&aggs=heldBy"
            "&q=ufo"
            "&size=20"
            "&from=0"
        )

        # with filter not belonging to nontna group (should be ignored)
        response = self.client.get(
            "/catalogue/search/?"
            "group=nonTna"
            "&q=ufo"
            "&collection=somecollection"
            "&online=true"
            "&level=somelevel"
            "&subject=Army"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        mock_logger.debug.assert_called_with(
            "https://rosetta.test/data/search?"
            "filter=group%3AnonTna"
            "&filter=datatype%3Arecord"
            "&aggs=heldBy"
            "&q=ufo"
            "&size=20"
            "&from=0"
        )

        # Test covering date filters
        response = self.client.get(
            "/catalogue/search/?"
            "group=nonTna"
            "&covering_date_from-year=2000"
            "&covering_date_from-month=12"
            "&covering_date_from-day=1"
            "&covering_date_to-year=2000"
            "&covering_date_to-month=12"
            "&covering_date_to-day=31"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        mock_logger.debug.assert_called_with(
            "https://rosetta.test/data/search?"
            "filter=group%3AnonTna"
            "&filter=datatype%3Arecord"
            "&filter=coveringFromDate%3A%28%3E%3D2000-12-1%29"
            "&filter=coveringToDate%3A%28%3C%3D2000-12-31%29"
            "&aggs=heldBy"
            "&q=%2A"
            "&size=20"
            "&from=0"
        )

        # Test longHeldBy filter
        response = self.client.get(
            "/catalogue/search/?group=nonTna&filter_list=longHeldBy"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        mock_logger.debug.assert_called_with(
            "https://rosetta.test/data/search?"
            "filter=group%3AnonTna"
            "&filter=datatype%3Arecord"
            "&aggs=longHeldBy"
            "&q=%2A"
            "&size=0"
        )
