from http import HTTPStatus

import responses
from app.records.models import Record
from app.search.buckets import BucketKeys
from app.search.forms import (
    CatalogueSearchTnaForm,
    FieldsConstant,
)
from django.conf import settings
from django.test import TestCase


class CatalogueSearchViewDefaultTests(TestCase):
    """Mainly tests the context.
    Default is tna group."""

    @responses.activate
    def test_catalogue_search_context_without_params(self):

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
                "aggregations": [
                    {
                        "name": "level",
                        "entries": [
                            {"value": "Item", "doc_count": 100},
                            {"value": "Division", "doc_count": 5},
                        ],
                    },
                    {
                        "name": "collection",
                        "entries": [
                            {"value": "BT", "doc_count": 50},
                            {"value": "WO", "doc_count": 35},
                        ],
                    },
                    {
                        "name": "closure",
                        "entries": [
                            {
                                "value": "Open Document, Open Description",
                                "doc_count": 150,
                            },
                        ],
                    },
                    {
                        "name": "subject",
                        "entries": [
                            {"value": "Army", "doc_count": 25},
                            {"value": "Navy", "doc_count": 15},
                        ],
                    },
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

        response = self.client.get("/catalogue/search/")
        context_data = response.context_data
        form = context_data.get("form")
        group_field = form.fields[FieldsConstant.GROUP]
        q_field = form.fields[FieldsConstant.Q]
        sort_field = form.fields[FieldsConstant.SORT]
        level_field = form.fields[FieldsConstant.LEVEL]
        collection_field = form.fields[FieldsConstant.COLLECTION]
        closure_field = form.fields[FieldsConstant.CLOSURE]
        subject_field = form.fields[FieldsConstant.SUBJECT]
        covering_date_from_field = form.fields[
            FieldsConstant.COVERING_DATE_FROM
        ]
        covering_date_to_field = form.fields[FieldsConstant.COVERING_DATE_TO]

        self.assertEqual(response.status_code, HTTPStatus.OK)

        self.assertIsInstance(context_data.get("results"), list)
        self.assertEqual(len(context_data.get("results")), 1)
        self.assertIsInstance(context_data.get("results")[0], Record)
        self.assertEqual(
            context_data.get("stats"),
            {"total": 26008838, "results": 20},
        )

        self.assertEqual(
            context_data.get("results_range"),
            {"from": 1, "to": 20},
        )

        self.assertEqual(context_data.get("selected_filters"), [])

        self.assertEqual(
            context_data.get("pagination"),
            {
                "items": [
                    {"number": "1", "href": "?page=1", "current": True},
                    {"number": "2", "href": "?page=2", "current": False},
                    {"ellipsis": True},
                    {"number": "500", "href": "?page=500", "current": False},
                ],
                "next": {"href": "?page=2", "title": "Next page of results"},
            },
        )

        self.assertEqual(
            context_data.get("bucket_list").items,
            [
                {
                    "name": "Records at the National Archives (1)",
                    "href": "?group=tna",
                    "current": True,
                },
                {
                    "name": "Records at other UK archives (0)",
                    "href": "?group=nonTna",
                    "current": False,
                },
            ],
        )
        self.assertEqual(context_data.get("bucket_keys"), BucketKeys)

        # ### form ###
        self.assertIsInstance(form, CatalogueSearchTnaForm)
        self.assertEqual(form.errors, {})
        self.assertEqual(len(form.fields), 13)
        tna_field_names = [
            FieldsConstant.GROUP,
            FieldsConstant.SORT,
            FieldsConstant.Q,
            FieldsConstant.LEVEL,
            FieldsConstant.COLLECTION,
            FieldsConstant.SUBJECT,
            FieldsConstant.ONLINE,
            FieldsConstant.CLOSURE,
            FieldsConstant.FILTER_LIST,
            FieldsConstant.COVERING_DATE_FROM,
            FieldsConstant.COVERING_DATE_TO,
            FieldsConstant.OPENING_DATE_FROM,
            FieldsConstant.OPENING_DATE_TO,
        ]
        tna_form_field_names = set(form.fields.keys())
        self.assertTrue(set(tna_field_names) == set(tna_form_field_names))

        # ### form fields ###

        self.assertEqual(q_field.id, "id_q")
        self.assertEqual(q_field.name, "q")
        self.assertEqual(q_field.value, "")
        self.assertEqual(q_field.cleaned, "")

        self.assertEqual(group_field.id, "id_group")
        self.assertEqual(group_field.name, "group")
        self.assertEqual(group_field.value, "tna")
        self.assertEqual(
            group_field.cleaned,
            "tna",
        )
        self.assertEqual(
            group_field.items,
            [
                {
                    "text": "Records at the National Archives",
                    "value": "tna",
                    "checked": True,
                },
                {"text": "Records at other UK archives", "value": "nonTna"},
            ],
        )

        self.assertEqual(sort_field.id, "id_sort")
        self.assertEqual(sort_field.name, "sort")
        self.assertEqual(sort_field.value, "")
        self.assertEqual(sort_field.cleaned, "")
        self.assertEqual(
            sort_field.items,
            [
                {"text": "Relevance", "value": "", "checked": True},
                {"text": "Date (newest first)", "value": "date:desc"},
                {"text": "Date (oldest first)", "value": "date:asc"},
                {"text": "Title (A–Z)", "value": "title:asc"},
                {"text": "Title (Z–A)", "value": "title:desc"},
            ],
        )

        self.assertEqual(level_field.id, "id_level")
        self.assertEqual(level_field.name, "level")
        self.assertEqual(
            level_field.label,
            "Filter by levels",
        )
        self.assertEqual(
            level_field.active_filter_label,
            "Level",
        )
        self.assertEqual(level_field.value, [])
        self.assertEqual(level_field.cleaned, [])
        self.assertEqual(
            level_field.items,
            [
                {"text": "Item (100)", "value": "Item"},
                {"text": "Division (5)", "value": "Division"},
            ],
        )
        self.assertEqual(
            collection_field.id,
            "id_collection",
        )
        self.assertEqual(
            collection_field.name,
            "collection",
        )
        self.assertEqual(
            collection_field.label,
            "Collections",
        )
        self.assertEqual(
            form.fields["collection"].active_filter_label,
            "Collection",
        )
        self.assertEqual(
            collection_field.value,
            [],
        )
        self.assertEqual(
            collection_field.cleaned,
            [],
        )
        self.assertEqual(
            collection_field.items,
            [
                {
                    "text": "BT - Board of Trade and successors (50)",
                    "value": "BT",
                },
                {
                    "text": "WO - War Office, Armed Forces, Judge Advocate General, and related bodies (35)",
                    "value": "WO",
                },
            ],
        )

        self.assertEqual(
            closure_field.id,
            "id_closure",
        )
        self.assertEqual(
            closure_field.name,
            "closure",
        )
        self.assertEqual(
            closure_field.label,
            "Closure status",
        )
        self.assertEqual(
            closure_field.active_filter_label,
            "Closure status",
        )
        self.assertEqual(
            closure_field.value,
            [],
        )
        self.assertEqual(
            closure_field.cleaned,
            [],
        )
        self.assertEqual(
            closure_field.items,
            [
                {
                    "text": "Open Document, Open Description (150)",
                    "value": "Open Document, Open Description",
                },
            ],
        )

        # Test subjects field
        self.assertEqual(
            subject_field.name,
            "subject",
        )
        self.assertEqual(
            subject_field.label,
            "Subjects",
        )
        self.assertEqual(subject_field.value, [])
        self.assertEqual(
            subject_field.cleaned,
            [],
        )
        self.assertEqual(
            subject_field.items,
            [
                {"text": "Army (25)", "value": "Army"},
                {"text": "Navy (15)", "value": "Navy"},
            ],
        )

        # test covering date from fields
        self.assertEqual(
            covering_date_from_field.id,
            "id_covering_date_from",
        )
        self.assertEqual(
            covering_date_from_field.name,
            "covering_date_from",
        )
        self.assertEqual(
            covering_date_from_field.label,
            "From",
        )
        self.assertEqual(
            covering_date_from_field.active_filter_label,
            "Record date from",
        )
        self.assertEqual(
            covering_date_from_field.value,
            {"year": "", "month": "", "day": ""},
        )
        self.assertEqual(
            covering_date_from_field.cleaned,
            None,
        )

        # test covering date to fields
        self.assertEqual(
            covering_date_to_field.id,
            "id_covering_date_to",
        )
        self.assertEqual(
            covering_date_to_field.name,
            "covering_date_to",
        )
        self.assertEqual(
            covering_date_to_field.label,
            "To",
        )
        self.assertEqual(
            covering_date_to_field.active_filter_label,
            "Record date to",
        )
        self.assertEqual(
            covering_date_to_field.value,
            {"year": "", "month": "", "day": ""},
        )
        self.assertEqual(
            covering_date_to_field.cleaned,
            None,
        )
