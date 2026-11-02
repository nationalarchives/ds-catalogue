from http import HTTPStatus
from urllib.parse import parse_qs, urlparse

import responses
from django.conf import settings
from django.test import TestCase

from app.search.forms import FieldsConstant

MDR_SEARCH_URL = "/catalogue/manor-search/"
SEARCH_TEMPLATE = "search/mdr_search.html"
RESULTS_TEMPLATE = "search/mdr_results.html"


def rosetta_calls() -> list:
    """Returns the mocked calls to the Rosetta API, excluding other APIs
    called by the page e.g. Wagtail notifications."""

    return [
        call
        for call in responses.calls
        if call.request.url.startswith(settings.ROSETTA_API_URL)
    ]


def api_response(data: list, total: int | None = None) -> dict:
    """Returns a Rosetta /search response for MDR records, in the shape returned
    by the API. The group bucket counts are for all records, not the MDR search."""

    return {
        "data": [{"@template": {"details": details}} for details in data],
        "aggregations": [
            {
                "name": "country",
                "entries": [
                    {"value": "England", "doc_count": 2},
                    {"value": "South West", "doc_count": 1},
                    {"value": "Surrey", "doc_count": 1},
                    {"value": "Wales", "doc_count": 1},
                ],
                "other": 5,
            }
        ],
        "buckets": [
            {
                "name": "group",
                "entries": [
                    {"value": "tna", "count": 30382470},
                    {"value": "nonTna", "count": 17292431},
                ],
            }
        ],
        "stats": {"total": len(data) if total is None else total, "results": len(data)},
    }


MANOR_GROUP_ARRAY = [{"value": "manor"}, {"value": "creator"}, {"value": "nonTna"}]

MANORS = [
    # fields returned by the API, with provisional fields not yet returned
    {
        "id": "F238687",
        "summaryTitle": "RICHMOND MANOR",
        "groupArray": MANOR_GROUP_ARRAY,
        "place": "Richmond, Surrey",
        "startDate": "1189",
        "endDate": "1925",
        "collectionsCount": 61,
        "collectionsHeldByCount": 9,
    },
    {
        "id": "F273224",
        "summaryTitle": "HINTON COLUMBERS MANOR",
        "groupArray": MANOR_GROUP_ARRAY,
        "place": "Broad Hinton, Wiltshire",
        "collectionsCount": 0,
        "collectionsHeldByCount": 0,
    },
    # only the fields currently returned by the API
    {
        "id": "F240356",
        "summaryTitle": "PREBEND OF BUCKINGHAM WITH GAWCOTT MANOR",
        "groupArray": MANOR_GROUP_ARRAY,
        "startDate": "1611",
        "endDate": "1936",
    },
]


def result_html(response, record_id: str) -> str:
    """Returns the html for a result in the results list."""

    content = response.content.decode()
    start = content.index(f'id="record-{record_id}"')
    return content[start : content.index("</li>", start)]


class MDRSearchFormStateTests(TestCase):
    """Tests the search form is rendered when no search has been submitted
    or the search terms are invalid, without calling the API."""

    @responses.activate
    def test_no_search_renders_search_form(self):
        response = self.client.get(MDR_SEARCH_URL)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.template_name, [SEARCH_TEMPLATE])
        self.assertEqual(response.context_data["form"].errors, {})
        self.assertEqual(len(rosetta_calls()), 0)
        self.assertContains(response, "Search by manor")
        self.assertNotContains(response, "There is a problem")

    @responses.activate
    def test_empty_search_renders_search_form_with_errors(self):
        response = self.client.get(f"{MDR_SEARCH_URL}?q=&parish=&county=")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.template_name, [SEARCH_TEMPLATE])
        self.assertEqual(len(rosetta_calls()), 0)
        self.assertContains(response, "<title>Error: Manorial Documents Register")
        self.assertContains(response, "There is a problem")
        self.assertContains(
            response,
            'href="#id_q" class="tna-error-summary__link">Enter a manor name, parish name or historic county',
        )

    @responses.activate
    def test_invalid_county_renders_search_form_with_errors(self):
        response = self.client.get(f"{MDR_SEARCH_URL}?q=richmond&county=Nowhere")

        self.assertEqual(response.template_name, [SEARCH_TEMPLATE])
        self.assertIn(FieldsConstant.COUNTY, response.context_data["form"].errors)
        self.assertEqual(len(rosetta_calls()), 0)

    def test_invalid_page_without_search(self):
        response = self.client.get(f"{MDR_SEARCH_URL}?page=abc")

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class MDRSearchResultsTests(TestCase):
    """Tests the MDR search results, API params and links."""

    @responses.activate
    def test_search_api_params(self):
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json=api_response(MANORS),
        )

        response = self.client.get(
            f"{MDR_SEARCH_URL}?q=richmond&parish=Richmond&county=Surrey"
            "&covering_date_from-year=1300"
            "&covering_date_to-year=1900&sort=title:asc"
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.template_name, [RESULTS_TEMPLATE])
        self.assertEqual(len(rosetta_calls()), 1)

        api_params = parse_qs(urlparse(rosetta_calls()[0].request.url).query)
        self.assertEqual(
            api_params,
            {
                "q": ["richmond"],
                "filter": [
                    "group:nonTna",
                    "schema:manor",
                    "parish:Richmond",
                    "country:Surrey",
                    "startDate:(>=1300-1-1)",
                    "endDate:(<=1900-12-31)",
                ],
                "aggs": ["country"],
                "size": ["20"],
                "sort": ["title:asc"],
                "from": ["0"],
            },
        )

    @responses.activate
    def test_search_api_params_tna_bucket(self):
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json=api_response([]),
        )

        self.client.get(f"{MDR_SEARCH_URL}?county=Surrey&group=tna")

        api_params = parse_qs(urlparse(rosetta_calls()[0].request.url).query)
        self.assertEqual(api_params["q"], ["*"])
        self.assertEqual(
            api_params["filter"],
            ["group:tna", "schema:manor", "country:Surrey"],
        )

    @responses.activate
    def test_country_filter(self):
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json=api_response(MANORS),
        )

        response = self.client.get(
            f"{MDR_SEARCH_URL}?q=richmond&country=England&country=Wales"
        )

        api_params = parse_qs(urlparse(rosetta_calls()[0].request.url).query)
        self.assertEqual(
            api_params["filter"],
            ["group:nonTna", "schema:manor", "country:England", "country:Wales"],
        )
        self.assertTrue(
            response.context_data["form"].fields[FieldsConstant.COUNTRY].is_visible
        )
        self.assertEqual(
            [item["label"] for item in response.context_data["selected_filters"]],
            ["Manor", "Country: England", "Country: Wales"],
        )

    @responses.activate
    def test_country_filter_not_applied_with_county(self):
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json=api_response(MANORS),
        )

        response = self.client.get(f"{MDR_SEARCH_URL}?county=Glamorgan&country=Wales")

        api_params = parse_qs(urlparse(rosetta_calls()[0].request.url).query)
        self.assertEqual(
            api_params["filter"],
            ["group:nonTna", "schema:manor", "country:Glamorgan"],
        )
        self.assertFalse(
            response.context_data["form"].fields[FieldsConstant.COUNTRY].is_visible
        )
        self.assertEqual(
            [item["label"] for item in response.context_data["selected_filters"]],
            ["Manor"],
        )

    @responses.activate
    def test_search_results(self):
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json=api_response(MANORS, total=30),
        )

        response = self.client.get(f"{MDR_SEARCH_URL}?q=manor")

        self.assertEqual(response.context_data["stats"], {"total": 30, "results": 3})
        self.assertEqual(response.context_data["results_range"], {"from": 1, "to": 3})
        self.assertContains(response, "1–3 (of 30) results")

        # manor with collections
        html = result_html(response, "F238687")
        self.assertIn('href="/catalogue/id/F238687/"', html)
        self.assertIn("RICHMOND MANOR", html)
        self.assertIn("Manor", html)
        self.assertIn("61 collection(s) held by 9 archive(s)", html)
        self.assertIn("Richmond; Surrey", html)
        self.assertIn("1189-1925", html)

        # manor without collections or dates
        html = result_html(response, "F273224")
        self.assertIn("No records known to survive", html)
        self.assertIn("Dates unknown", html)

        # manor with only the fields currently returned by the API
        html = result_html(response, "F240356")
        self.assertIn("PREBEND OF BUCKINGHAM WITH GAWCOTT MANOR", html)
        self.assertIn("Manor", html)
        self.assertIn("1611-1936", html)
        self.assertNotIn("collection(s)", html)
        self.assertNotIn("No records known to survive", html)
        self.assertNotIn("Place", html)

        # record date filter without the catalogue date hint
        self.assertContains(response, "Filter by record date")
        self.assertNotContains(response, "For example: 1997")

        # country filter only includes countries from the country aggregation
        self.assertEqual(
            response.context_data["form"].fields[FieldsConstant.COUNTRY].items,
            [
                {"text": "England (2)", "value": "England"},
                {"text": "Wales (1)", "value": "Wales"},
            ],
        )

    @responses.activate
    def test_defaults_to_non_tna_bucket_with_results_count(self):
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json=api_response(MANORS, total=30),
        )

        response = self.client.get(f"{MDR_SEARCH_URL}?q=manor")

        # bucket counts from the API are not scoped to the MDR search
        self.assertEqual(
            response.context_data["bucket_list"].items,
            [
                {
                    "name": "Records at the National Archives",
                    "href": "?group=tna&q=manor",
                    "current": False,
                },
                {
                    "name": "Records at other UK archives (30)",
                    "href": "?group=nonTna&q=manor",
                    "current": True,
                },
            ],
        )
        self.assertContains(
            response, '<input type="hidden" name="group" value="nonTna">'
        )

    @responses.activate
    def test_no_results(self):
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json=api_response([]),
        )

        response = self.client.get(f"{MDR_SEARCH_URL}?q=noresults")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.template_name, [RESULTS_TEMPLATE])
        self.assertEqual(response.context_data["results"], [])
        self.assertContains(response, "No results found")

    @responses.activate
    def test_links_keep_search_terms(self):
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json=api_response(MANORS),
        )

        response = self.client.get(
            f"{MDR_SEARCH_URL}?q=richmond+manor&parish=Richmond&county=Surrey&country=England"
        )
        context = response.context_data

        self.assertEqual(
            [bucket.href for bucket in context["bucket_list"]],
            [
                "?group=tna&q=richmond+manor&parish=Richmond&county=Surrey",
                "?group=nonTna&q=richmond+manor&parish=Richmond&county=Surrey",
            ],
        )
        self.assertEqual(
            context["reset_filters_href"],
            "?group=nonTna&display=list&q=richmond+manor&parish=Richmond&county=Surrey",
        )
        self.assertEqual(
            context["selected_filters"][0],
            {
                "label": "Manor",
                "href": "/catalogue/search/?q=richmond+manor",
                "title": "Remove manor filter",
            },
        )
        # the country filter is not applied with a county
        self.assertEqual(len(context["selected_filters"]), 1)

        # search terms not in the search field are kept as hidden inputs
        self.assertContains(
            response, '<input type="hidden" name="parish" value="Richmond">'
        )
        self.assertContains(
            response, '<input type="hidden" name="county" value="Surrey">'
        )

    @responses.activate
    def test_invalid_date_range_renders_results_with_errors(self):
        response = self.client.get(
            f"{MDR_SEARCH_URL}?q=richmond&covering_date_from-year=1900&covering_date_to-year=1800"
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.template_name, [RESULTS_TEMPLATE])
        self.assertEqual(len(rosetta_calls()), 0)
        self.assertContains(
            response,
            "Record date from: This date must be earlier than or equal to the &#39;to&#39; date.",
        )

    def test_invalid_page_with_search(self):
        response = self.client.get(f"{MDR_SEARCH_URL}?q=richmond&page=abc")

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
