from http import HTTPStatus

import responses
from django.conf import settings
from django.test import TestCase
from django.utils.encoding import force_str


class CatalogueSearchViewAnalyticsTnaTests(TestCase):
    """Tests analytics metadata, data layer in CatalogueSearchView for TNA group"""

    @responses.activate
    def test_search_analytics_without_filters(
        self,
    ):
        """Tests analytics metadata, data layer without filters"""

        # data present for input
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [
                    {
                        "@template": {
                            "details": {
                                "id": "C123456",
                                "source": "CAT",
                            }
                        }
                    }
                ],
                "aggregations": [
                    {
                        "name": "collection",
                        "entries": [
                            {"value": "BT", "doc_count": 50},
                            {"value": "WO", "doc_count": 35},
                        ],
                        "total": 100,
                        "other": 50,
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
            status=HTTPStatus.OK,
        )

        query = "/catalogue/search/"
        response = self.client.get(query)

        context_data = response.context_data
        form = context_data.get("form")

        self.assertEqual(len(context_data.get("results")), 1)
        html = force_str(response.content)
        self.assertTrue(form.is_valid())

        # tests metadata in template
        self.assertIn(
            """<meta name="tna_root:content_group" content="Search the catalogue">""",
            html,
        )
        self.assertIn(
            """<meta name="tna_root:page_type" content="catalogue_search">""",
            html,
        )
        self.assertIn("""<meta name="tna_root:reader_type" content="">""", html)
        self.assertIn(
            """<meta name="tna_root:search_type" content="Records at The National Archives">""",
            html,
        )
        self.assertIn("""<meta name="tna_root:search_term" content="">""", html)
        self.assertIn(
            """<meta name="tna_root:search_total" content="26008838">""", html
        )
        self.assertIn(
            """<meta name="tna_root:search_filters" content="0">""", html
        )

        self.assertEqual(
            context_data.get("analytics_data"),
            {
                "content_group": "Search the catalogue",
                "page_type": "catalogue_search",
                "reader_type": None,
                "content_source": "TNA catalogue",
                "search_type": "Records at The National Archives",
                "search_term": "",
                "search_filters": 0,
                "search_total": 26008838,
            },
        )

    @responses.activate
    def test_search_analytics_with_filters(
        self,
    ):
        """Tests analytics metadata, data layer with filters"""

        # data present for input
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [
                    {
                        "@template": {
                            "details": {
                                "id": "C123456",
                                "source": "CAT",
                            }
                        }
                    }
                ],
                "aggregations": [
                    {
                        "name": "collection",
                        "entries": [
                            {"value": "BT", "doc_count": 50},
                            {"value": "WO", "doc_count": 35},
                        ],
                        "total": 100,
                        "other": 50,
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
            status=HTTPStatus.OK,
        )

        query = "/catalogue/search/?group=tna&q=ufo&collection=BT&collection=WO&covering_date_from-year=1900&covering_date_to-year=1950"
        response = self.client.get(query)

        context_data = response.context_data
        form = context_data.get("form")

        self.assertEqual(len(context_data.get("results")), 1)
        html = force_str(response.content)
        self.assertTrue(form.is_valid())

        # tests metadata in template
        self.assertIn(
            """<meta name="tna_root:content_group" content="Search the catalogue">""",
            html,
        )
        self.assertIn(
            """<meta name="tna_root:page_type" content="catalogue_search">""",
            html,
        )
        self.assertIn("""<meta name="tna_root:reader_type" content="">""", html)
        self.assertIn(
            """<meta name="tna_root:search_type" content="Records at The National Archives">""",
            html,
        )
        self.assertIn(
            """<meta name="tna_root:search_term" content="ufo">""", html
        )
        self.assertIn(
            """<meta name="tna_root:search_total" content="26008838">""", html
        )
        self.assertIn(
            """<meta name="tna_root:search_filters" content="4">""", html
        )

        self.assertEqual(
            context_data.get("analytics_data"),
            {
                "content_group": "Search the catalogue",
                "page_type": "catalogue_search",
                "reader_type": None,
                "content_source": "TNA catalogue",
                "search_type": "Records at The National Archives",
                "search_term": "ufo",
                "search_filters": 4,
                "search_total": 26008838,
            },
        )

    @responses.activate
    def test_search_analytics_with_no_results(
        self,
    ):
        """Tests analytics metadata, data layer when no results found"""

        query = "/catalogue/search/?group=tna&q=qwert"

        # no data for input
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/search",
            json={
                "data": [],
                "aggregations": [
                    {
                        "name": "collection",
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
                    "total": 0,
                    "results": 0,
                },
            },
            status=HTTPStatus.OK,
        )

        response = self.client.get(query)

        context_data = response.context_data
        form = context_data.get("form")

        self.assertEqual(context_data.get("results"), [])
        html = force_str(response.content)
        self.assertTrue(form.is_valid())

        # tests metadata in template
        self.assertIn(
            """<meta name="tna_root:content_group" content="Search the catalogue">""",
            html,
        )
        self.assertIn(
            """<meta name="tna_root:page_type" content="catalogue_search">""",
            html,
        )
        self.assertIn("""<meta name="tna_root:reader_type" content="">""", html)
        self.assertIn(
            """<meta name="tna_root:search_type" content="Records at The National Archives">""",
            html,
        )
        self.assertIn(
            """<meta name="tna_root:search_term" content="qwert">""", html
        )
        self.assertIn(
            """<meta name="tna_root:search_total" content="0">""", html
        )
        self.assertIn(
            """<meta name="tna_root:search_filters" content="0">""", html
        )

        self.assertEqual(
            context_data.get("analytics_data"),
            {
                "content_group": "Search the catalogue",
                "page_type": "catalogue_search",
                "reader_type": None,
                "content_source": "TNA catalogue",
                "search_type": "Records at The National Archives",
                "search_term": "qwert",
                "search_filters": 0,
                "search_total": 0,
            },
        )

    @responses.activate
    def test_search_analytics_with_errors(
        self,
    ):
        """Tests analytics metadata, data layer when form has errors"""

        query = "/catalogue/search/?group=tna&q=ufo&collection=BT&level=INVALID"
        response = self.client.get(query)

        context_data = response.context_data
        form = context_data.get("form")

        self.assertEqual(context_data.get("results"), None)
        html = force_str(response.content)
        self.assertFalse(form.is_valid())

        # tests metadata in template
        self.assertIn(
            """<meta name="tna_root:content_group" content="Search the catalogue">""",
            html,
        )
        self.assertIn(
            """<meta name="tna_root:page_type" content="catalogue_search">""",
            html,
        )
        self.assertIn("""<meta name="tna_root:reader_type" content="">""", html)
        self.assertIn(
            """<meta name="tna_root:search_type" content="Records at The National Archives">""",
            html,
        )
        self.assertIn(
            """<meta name="tna_root:search_term" content="ufo">""", html
        )
        self.assertIn(
            """<meta name="tna_root:search_total" content="0">""", html
        )
        self.assertIn(
            """<meta name="tna_root:search_filters" content="2">""", html
        )

        self.assertEqual(
            context_data.get("analytics_data"),
            {
                "content_group": "Search the catalogue",
                "page_type": "catalogue_search",
                "reader_type": None,
                "content_source": "TNA catalogue",
                "search_type": "Records at The National Archives",
                "search_term": "ufo",
                "search_filters": 2,
                "search_total": 0,
            },
        )
