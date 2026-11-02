from http import HTTPStatus
from urllib.parse import parse_qs, urlparse

import responses
from django.conf import settings
from django.test import SimpleTestCase, TestCase

from app.records.api import record_creator_collections
from app.records.constants import RecordTypes
from app.records.models import Record

CREATOR_TEMPLATE = "records/creator_detail.html"

MANOR_GROUP_ARRAY = [{"value": "manor"}, {"value": "creator"}, {"value": "nonTna"}]

# fields returned by the API for a manor
RICHMOND_MANOR = {
    "id": "F238687",
    "primaryIdentifier": "F238687",
    "summaryTitle": "RICHMOND MANOR",
    "title": "RICHMOND MANOR",
    "group": "creator",
    "groupArray": MANOR_GROUP_ARRAY,
    "type": "agent",
    "startDate": "1189",
    "endDate": "1925",
}

HINTON_COLUMBERS_MANOR = {
    "id": "F273224",
    "summaryTitle": "HINTON COLUMBERS MANOR",
    "title": "HINTON COLUMBERS MANOR",
    "group": "creator",
    "groupArray": MANOR_GROUP_ARRAY,
    "type": "agent",
}

# record creator details returned by the API for a manor
RICHMOND_MANOR_DETAILS = {
    "name": [{"value": "Sheen, West"}, {"value": "West Sheen"}],
    "place": "Richmond, Surrey",
    "authorityReference": "GB/NNAF/M170870",
    "formerAuthorityReference": "GB/NNAF/M108906",
}

# fields returned by the API for the manor's collections (records)
COLLECTIONS = [
    {
        "id": "N14261699",
        "summaryTitle": "serjeant's account",
        "dateCovering": "1313-1315",
        "heldBy": "The National Archives",
        "reference": "SC 6/1014/2",
        "group": "nonTna",
        "groupArray": [{"value": "record"}, {"value": "nonTna"}],
    },
    {
        "id": "N14261700",
        "summaryTitle": "bailiff's accounts",
        "heldBy": "The National Archives",
        "group": "nonTna",
        "groupArray": [{"value": "record"}, {"value": "nonTna"}],
    },
    {
        "id": "N14261701",
        "dateCovering": "1400",
        "group": "nonTna",
        "groupArray": [{"value": "record"}, {"value": "nonTna"}],
    },
]


def get_response(details: dict) -> dict:
    """Returns a Rosetta /get response for a record."""

    return {"data": [{"@template": {"details": details}}]}


def search_response(data: list, total: int | None = None, bucket_count=100) -> dict:
    """Returns a Rosetta /search response. The group bucket counts are for all
    records, not the search."""

    return {
        "data": [{"@template": {"details": details}} for details in data],
        "buckets": [
            {
                "name": "group",
                "entries": [
                    {"value": "tna", "count": bucket_count},
                    {"value": "nonTna", "count": bucket_count},
                ],
            }
        ],
        "stats": {
            "total": len(data) if total is None else total,
            "results": len(data),
        },
    }


def add_creator_responses(details: dict, collections: dict):
    """Adds the mocked Rosetta responses for a record creator page."""

    responses.add(
        responses.GET,
        f"{settings.ROSETTA_API_URL}/get?id={details['id']}",
        json=get_response(details),
    )
    responses.add(
        responses.GET,
        f"{settings.ROSETTA_API_URL}/search",
        json=collections,
    )


def collections_api_params() -> dict:
    """Returns the params of the mocked Rosetta /search call for collections."""

    calls = [
        call
        for call in responses.calls
        if call.request.url.startswith(f"{settings.ROSETTA_API_URL}/search")
    ]
    return parse_qs(urlparse(calls[0].request.url).query)


class RecordCreatorTypeTests(SimpleTestCase):
    """Tests record creators are identified by the API group value."""

    def test_custom_record_type_for_creator(self):
        record = Record(RICHMOND_MANOR)

        self.assertEqual(record.custom_record_type, RecordTypes.CREATORS)

    def test_custom_record_type_for_creator_collection_record(self):
        record = Record(COLLECTIONS[0] | {"source": "NRA"})

        self.assertEqual(record.custom_record_type, "NRA")

    def test_empty_for_optional_creator_details(self):
        record = Record(RICHMOND_MANOR)

        self.assertEqual(record.alternative_names, [])
        self.assertEqual(record.place, "")
        self.assertEqual(record.name_authority_reference, "")
        self.assertEqual(record.former_name_authority_reference, "")

    def test_creator_details(self):
        record = Record(RICHMOND_MANOR | RICHMOND_MANOR_DETAILS)

        self.assertEqual(record.alternative_names, ["Sheen, West", "West Sheen"])
        self.assertEqual(record.place, "Richmond, Surrey")
        self.assertEqual(record.name_authority_reference, "GB/NNAF/M170870")
        self.assertEqual(record.former_name_authority_reference, "GB/NNAF/M108906")

    def test_alternative_names_ignores_unexpected_values(self):
        record = Record(
            RICHMOND_MANOR
            | {"name": [{"value": "West Sheen"}, "Sheen, West", {"value": ""}]}
        )

        self.assertEqual(record.alternative_names, ["West Sheen"])

    def test_alternative_names_for_one_name(self):
        # the api value is a dict, rather than a list, for one name
        record = Record(RICHMOND_MANOR | {"name": {"value": "Prebend End"}})

        self.assertEqual(record.alternative_names, ["Prebend End"])


class RecordCreatorCollectionsApiTests(SimpleTestCase):
    """Tests fetching the collections created by a record creator."""

    @responses.activate
    def test_collections_api_params(self):
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json=search_response(COLLECTIONS, total=61),
        )

        api_result = record_creator_collections(creator_id="F238687", page=2)

        self.assertEqual(api_result.stats_total, 61)
        self.assertEqual(
            collections_api_params(),
            {
                "filter": ["creator:F238687"],
                "q": ["*"],
                "size": ["20"],
                "sort": ["dateCovering:asc"],
                "from": ["20"],
            },
        )

    @responses.activate
    def test_no_collections(self):
        # no data and no bucket counts raises NoResultsFound in the search api
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json=search_response([], bucket_count=0),
        )

        self.assertIsNone(record_creator_collections(creator_id="F273224"))


class RecordCreatorDetailViewTests(TestCase):
    """Tests the record creator (e.g. manor) details page."""

    @responses.activate
    def test_creator_page(self):
        add_creator_responses(RICHMOND_MANOR, search_response(COLLECTIONS, total=61))

        response = self.client.get("/catalogue/id/F238687/")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.template_name, [CREATOR_TEMPLATE])
        self.assertContains(
            response, '<p class="tna-hgroup__supertitle">Manor</p>', html=True
        )
        self.assertContains(
            response, '<h1 class="tna-hgroup__title">RICHMOND MANOR</h1>', html=True
        )
        self.assertContains(
            response,
            "This page is about the record creator <strong>RICHMOND MANOR</strong>",
        )

        # record creator details
        self.assertContains(response, "Record creator details")
        self.assertContains(response, "1189-1925")
        self.assertContains(response, "/catalogue/id/F238687/</span>")

        # optional fields not returned by the API are not displayed
        self.assertNotContains(response, "Alternative name(s)")
        self.assertNotContains(response, "Places")
        self.assertNotContains(response, "Name authority reference")

        # catalogue record content is not displayed
        self.assertNotContains(response, "Catalogue reference:</p>")
        self.assertNotContains(response, "View options")

        # catalogue record analytics are not output, as for ARCHON records
        self.assertNotContains(response, "tna_root:")

    @responses.activate
    def test_creator_details_when_provided(self):
        add_creator_responses(
            RICHMOND_MANOR | RICHMOND_MANOR_DETAILS,
            search_response(COLLECTIONS, total=61),
        )

        response = self.client.get("/catalogue/id/F238687/")

        self.assertContains(response, "Alternative name(s)")
        self.assertContains(response, '<ul class="tna-ul tna-ul--plain">')
        self.assertContains(response, "<li>Sheen, West (Manor)</li>", html=True)
        self.assertContains(response, "<li>West Sheen (Manor)</li>", html=True)
        self.assertContains(response, "Places")
        self.assertContains(response, "Richmond, Surrey")
        self.assertContains(response, "Name authority reference")
        self.assertContains(
            response, "GB/NNAF/M170870 (Former ISAAR ref: GB/NNAF/M108906)"
        )

    @responses.activate
    def test_one_alternative_name(self):
        add_creator_responses(
            RICHMOND_MANOR | {"name": {"value": "Prebend End"}},
            search_response(COLLECTIONS, total=61),
        )

        response = self.client.get("/catalogue/id/F238687/")

        self.assertContains(response, "Prebend End (Manor)")
        self.assertNotContains(response, '<ul class="tna-ul tna-ul--plain">')

    @responses.activate
    def test_creator_details_without_former_reference(self):
        add_creator_responses(
            HINTON_COLUMBERS_MANOR
            | {
                "place": "Broad Hinton, Wiltshire",
                "authorityReference": "GB/NNAF/M291286",
            },
            search_response([], bucket_count=0),
        )

        response = self.client.get("/catalogue/id/F273224/")

        self.assertNotContains(response, "Alternative name(s)")
        self.assertContains(response, "Broad Hinton, Wiltshire")
        self.assertContains(response, "GB/NNAF/M291286")
        self.assertNotContains(response, "Former ISAAR ref")

    @responses.activate
    def test_collections(self):
        add_creator_responses(RICHMOND_MANOR, search_response(COLLECTIONS, total=61))

        response = self.client.get("/catalogue/id/F238687/")
        context = response.context_data

        self.assertEqual(collections_api_params()["filter"], ["creator:F238687"])
        self.assertEqual(context["collections_total"], 61)
        self.assertEqual(context["collections_range"], {"from": 1, "to": 3})
        self.assertContains(response, "Collections (61)")
        self.assertContains(response, "Showing 1–3 of 61")
        self.assertNotContains(response, "No records known to survive")

        # collection with all fields, title prefixed with the date
        self.assertContains(response, 'href="/catalogue/id/N14261699/"')
        self.assertContains(response, "1313-1315: serjeant&#39;s account")
        html = response.content.decode()
        start = html.index('<li id="record-N14261699">')
        collection_html = html[start : html.index("</li>", start) + len("</li>")]
        self.assertInHTML("<dt>Date</dt><dd>1313-1315</dd>", collection_html)
        self.assertInHTML(
            "<dt>Held by</dt><dd>The National Archives</dd>", collection_html
        )
        self.assertInHTML(
            "<dt>Catalogue reference</dt><dd>SC 6/1014/2</dd>", collection_html
        )

        # collection without a date or reference
        self.assertContains(response, 'href="/catalogue/id/N14261700/"')
        self.assertContains(response, "bailiff&#39;s accounts")
        self.assertNotContains(response, ": bailiff&#39;s accounts")

        # collection without a title
        self.assertContains(
            response, 'href="/catalogue/id/N14261701/">1400: [No title]</a>'
        )

        # pagination for 61 collections, 20 per page
        self.assertEqual(
            [item.get("href") for item in context["collections_pagination"]["items"]],
            ["?page=1", "?page=2", "?page=3", "?page=4"],
        )

    @responses.activate
    def test_collections_pagination_keeps_search(self):
        add_creator_responses(RICHMOND_MANOR, search_response(COLLECTIONS, total=61))

        response = self.client.get("/catalogue/id/F238687/?page=2&search=abc")

        self.assertEqual(collections_api_params()["from"], ["20"])
        self.assertEqual(
            response.context_data["collections_range"], {"from": 21, "to": 23}
        )
        self.assertEqual(
            response.context_data["collections_pagination"]["previous"]["href"],
            "?page=1&search=abc",
        )

    @responses.activate
    def test_no_collections(self):
        add_creator_responses(
            HINTON_COLUMBERS_MANOR, search_response([], bucket_count=0)
        )

        response = self.client.get("/catalogue/id/F273224/")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.template_name, [CREATOR_TEMPLATE])
        self.assertEqual(response.context_data["collections"], [])
        self.assertEqual(response.context_data["collections_total"], 0)
        self.assertIsNone(response.context_data["collections_pagination"])
        self.assertContains(response, "Collections (0)")
        self.assertContains(response, "No records known to survive")
        self.assertNotContains(response, "Showing")

        # no dates for the record creator
        self.assertNotContains(response, "The date covered by the record")

    @responses.activate
    def test_invalid_page(self):
        add_creator_responses(RICHMOND_MANOR, search_response(COLLECTIONS, total=61))

        for page in ("abc", "0", "5"):
            with self.subTest(page=page):
                response = self.client.get(f"/catalogue/id/F238687/?page={page}")

                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    @responses.activate
    def test_catalogue_record_does_not_fetch_collections(self):
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=N14261699",
            json=get_response(COLLECTIONS[0] | {"source": "NRA"}),
        )

        response = self.client.get("/catalogue/id/N14261699/")

        self.assertEqual(response.template_name, ["records/record_detail.html"])
        self.assertNotIn("collections", response.context_data)
