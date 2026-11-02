from http import HTTPStatus

import responses
from django.conf import settings
from django.test import TestCase


class TestRecordViewForSuppressedErrorsLogged(TestCase):
    """Test errors in views that are logged which do not impact user experience."""

    # NB: There is no detail-view test for held_by_count error logging because
    # the new hierarchy panel no longer renders held_by_count (the old "Held by
    # X records" row was replaced by the archive root node). The held_by_count
    # missing-value behaviour is covered at model level in test_models.py.

    @responses.activate
    def test_record_detail_view_hierarchy_count_error_log(self):

        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C123456",
            json={
                "data": [
                    {
                        "@template": {
                            "details": {
                                "id": "C123456",
                                "title": "Test Title",
                                "source": "CAT",
                                "heldByCount": 100,
                                "groupArray": [{"value": "tna"}],
                                "@hierarchy": [
                                    {
                                        "@admin": {"id": "C236"},
                                        "identifier": [{"reference_numbers": "PROB"}],
                                        "level": {"code": 1},
                                    },
                                ],
                            }
                        }
                    }
                ]
            },
            status=HTTPStatus.OK,
        )

        with self.assertLogs("app.records.models", level="ERROR") as log:
            response = self.client.get("/catalogue/id/C123456/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "ERROR:app.records.models:hierarchy_count missing for hierarchy record",
            "".join(log.output),
        )
        self.assertEqual(
            response.context_data.get("record").hierarchy[0].hierarchy_count,
            "Unknown number of",
        )
