from unittest.mock import Mock, patch

import responses
from app.deliveryoptions.constants import AvailabilityCondition
from app.records.mixins import DeliveryOptionsMixin
from django.conf import settings
from django.test import TestCase


class TestAnalyticsDataInRecordDetailsView(TestCase):

    def setUp(self):
        self.mixin = DeliveryOptionsMixin()

    @responses.activate
    def test_analytics_record_details(self):

        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C1731303",
            json={
                "data": [
                    {
                        "@template": {
                            "details": {
                                "iaid": "C1731303",
                                "referenceNumber": "CO 166/2",
                                "source": "CAT",
                                "groupArray": [
                                    {"value": "record"},
                                    {"value": "tna"},
                                ],
                                "heldBy": "The National Archives, Kew",
                                "level": {"code": 6, "value": "Piece"},
                                "summaryTitle": "Military and Naval",
                                "subjects": [
                                    "Caribbean",
                                    "Navy",
                                    "Operations, battles and campaigns",
                                ],
                                "@hierarchy": [
                                    {
                                        "@admin": {"id": "C57"},
                                        "identifier": [
                                            {"reference_number": "CO"}
                                        ],
                                        "level": {"code": 1},
                                        "source": {"value": "CAT"},
                                        "summary": {
                                            "title": "Records of the Colonial Office, Commonwealth and Foreign and Commonwealth Offices,..."
                                        },
                                        "count": 370148,
                                    },
                                    {
                                        "@admin": {"id": "C433"},
                                        "level": {"code": 2},
                                        "source": {"value": "CAT"},
                                        "summary": {
                                            "title": "Correspondence with the colonies, entry books and registers of correspondence"
                                        },
                                        "count": 252104,
                                    },
                                    {
                                        "@admin": {"id": "C4357"},
                                        "identifier": [
                                            {"reference_number": "CO 166"}
                                        ],
                                        "level": {"code": 3},
                                        "source": {"value": "CAT"},
                                        "summary": {
                                            "title": "Secretary of State for the Colonies and War and Colonial Department: Martinique,..."
                                        },
                                        "count": 172,
                                    },
                                    {
                                        "@admin": {"id": "C38371"},
                                        "level": {"code": 4},
                                        "source": {"value": "CAT"},
                                        "summary": {
                                            "title": "Correspondence, Original - Secretary of State"
                                        },
                                        "count": 164,
                                    },
                                    {
                                        "@admin": {"id": "C1731303"},
                                        "identifier": [
                                            {"reference_number": "CO 166/2"}
                                        ],
                                        "level": {"code": 6},
                                        "source": {"value": "CAT"},
                                        "summary": {
                                            "title": "Military and Naval"
                                        },
                                        "count": 69,
                                    },
                                ],
                            }
                        }
                    }
                ]
            },
            status=200,
        )

        mock_delivery_response = [
            {
                "options": AvailabilityCondition.OrderOriginal.value,
                "surrogateLinks": [],
                "advancedOrderUrlParameters": "",
            }
        ]

        mock_availability_group = Mock()
        mock_availability_group.name = "AVAILABLE_IN_PERSON_WITH_COPYING"

        with (
            patch(
                "app.records.mixins.delivery_options_request_handler",
                return_value=mock_delivery_response,
            ),
            patch(
                "app.records.mixins.get_availability_group",
                return_value=mock_availability_group,
            ),
        ):

            _ = self.mixin.get_delivery_options_context("C1731303")
            response = self.client.get("/catalogue/id/C1731303/")

            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.resolver_match.view_name, "records:details"
            )
            self.assertTemplateUsed("records/record_detail.html")

            self.assertEqual(
                response.context_data.get("analytics_data"),
                {
                    "content_group": "TNA catalogue",
                    "page_type": "RecordDetailView[TNA catalogue record description]",
                    "reader_type": "",
                    "user_type": "",
                    "taxonomy_topic": "Caribbean;Navy;Operations, battles and campaigns",
                    "taxonomy_term": "not in use",
                    "time_period": "not in use",
                    "catalogue_repository": "66-The National Archives",
                    "catalogue_level": "6-Piece",
                    "catalogue_series": "CO 166-Secretary of State for the Colonies and War and Colonial Department: Martinique,...",
                    "catalogue_reference": "CO 166/2-Military and Naval",
                    "catalogue_datasource": "CAT",
                    "delivery_option_category": "AVAILABLE_IN_PERSON_WITH_COPYING",
                    "delivery_option": "OrderOriginal",
                },
            )
