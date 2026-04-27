from http import HTTPStatus

import responses
from django.conf import settings
from django.test import TestCase
from django.utils.encoding import force_str


class NonTnaArchonPageInfoBoxTests(TestCase):
    """Tests conditional rendering of info box on non-TNA Archon record pages based on
    presence of place description field in API response."""

    @responses.activate
    def test_info_box_render_with_place_description(self):
        """Tests that the info box renders when place description is present,
        and that the content takes half width of the page to accommodate the info box.
        """

        # data with place description field
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=A13531661",
            json={
                "data": [
                    {
                        "@template": {
                            "details": {
                                "id": "A13531661",
                                "referenceNumber": "179",
                                "title": "Test Title",
                                "source": "ARCHON",
                                "description": {
                                    "raw": "<contacts><addressline1><![CDATA[England]]></addressline1></contacts>"
                                },
                                "placeDescription": {
                                    "raw": '<span class="accessconditions"><span class="openinghours">Monday to Friday 9am to 5pm</span></span>'
                                },
                            }
                        }
                    }
                ]
            },
            status=200,
        )

        response = self.client.get("/catalogue/id/A13531661/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        html = force_str(response.content)
        # Check info box content is rendered
        self.assertIn("Information about this archive", html)
        self.assertIn("Monday to Friday 9am to 5pm", html)

        # Check class values to confirm content takes half width of the page
        # 1> check template `contact_class` value is used
        self.assertContains(
            response,
            "tna-column tna-column--full-tiny tna-column--full-small tna-column--width-1-2 tna-!--margin-top-m",
            count=1,
        )
        # 2> number of times template `full_width_class` value is used on the page
        self.assertContains(
            response, "tna-column tna-column--full tna-!--margin-top-l", count=1
        )

    @responses.activate
    def test_info_box_does_not_render_without_place_description(self):
        """Tests that the info box does not render when place description is absent,
        and that the content takes full width of the page."""

        # data without place description field
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=A13531666",
            json={
                "data": [
                    {
                        "@template": {
                            "details": {
                                "id": "A13531666",
                                "referenceNumber": "703",
                                "title": "Test Title",
                                "source": "ARCHON",
                                "description": {
                                    "raw": "<contacts><addressline1><![CDATA[USA]]></addressline1></contacts>"
                                },
                            }
                        }
                    }
                ]
            },
            status=200,
        )

        response = self.client.get("/catalogue/id/A13531666/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        html = force_str(response.content)
        # Check info box content is not rendered
        self.assertNotIn("Information about this archive", html)

        # Check class values to confirm content takes full width of the page
        # 1> check template `contact_class` value is not used
        self.assertNotContains(
            response,
            "tna-column tna-column--full-tiny tna-column--full-small tna-column--width-1-2 tna-!--margin-top-m",
        )
        # 2> number of times template `full_width_class` value is used on the page
        self.assertContains(
            response, "tna-column tna-column--full tna-!--margin-top-l", count=2
        )
