import json
from copy import deepcopy

from app.records.models import APIResponse
from django.conf import settings
from django.test import SimpleTestCase


class CatalogueRecordResponseTests(SimpleTestCase):
    """
    Tests for typical responses for differrent id formats
    """

    maxDiff = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_response_C15836(self):
        fixture_path = (
            f"{settings.BASE_DIR}/test/records/fixtures/response_C15836.json"
        )
        with open(fixture_path, "r") as f:
            fixture_contents = json.loads(f.read())

        self.response = APIResponse(deepcopy(fixture_contents["data"][0]))
        self.record = self.response.record

        self.assertEqual(self.record.iaid, "C15836")
        self.assertEqual(self.record.source, "CAT")
        self.assertEqual(self.record.custom_record_type, "CAT")
        self.assertEqual(self.record.reference_number, "DEFE 65")
        self.assertEqual(self.record.date_covering, "1959 - 1975")
        self.assertEqual(self.record.creator, ["Ministry of Defence, 1947"])
        self.assertEqual(self.record.dimensions, "")
        self.assertEqual(self.record.former_department_reference, "EWP, DI")
        self.assertEqual(self.record.former_pro_reference, "")
        self.assertEqual(self.record.language, "English")
        self.assertEqual(self.record.legal_status, "Public Record(s)")
        self.assertEqual(self.record.level, "Series")
        self.assertEqual(self.record.level_code, 3)
        self.assertEqual(self.record.map_designation, "")
        self.assertEqual(self.record.map_scale, "")
        self.assertEqual(self.record.note, "")
        self.assertEqual(self.record.physical_condition, "")
        self.assertEqual(self.record.physical_description, "7 file(s)")
        self.assertEqual(self.record.held_by, "The National Archives, Kew")
        self.assertEqual(self.record.held_by_id, "A13530124")
        self.assertEqual(self.record.held_by_url, "/catalogue/id/A13530124/")
        self.assertEqual(
            self.record.access_condition, "Subject to 30 year closure"
        )
        self.assertEqual(self.record.closure_status, "")
        self.assertEqual(self.record.record_opening, "")
        self.assertEqual(self.record.accruals, "Series is accruing")
        self.assertEqual(self.record.accumulation_dates, "")
        self.assertEqual(self.record.appraisal_information, "")
        self.assertEqual(self.record.copies_information, "")
        self.assertEqual(self.record.custodial_history, "")
        self.assertEqual(
            self.record.immediate_source_of_acquisition,
            ["From 2003  Ministry of Defence"],
        )
        self.assertEqual(self.record.location_of_originals, [])
        self.assertEqual(self.record.restrictions_on_use, "")
        self.assertEqual(
            self.record.administrative_background,
            (
                "The series consists of a collection of reports and papers "
                "produced by some ofthe many intelligence conferences or "
                "working parties in which the JointIntelligence Bureau "
                "and Defence Intelligence Staff participated, often "
                "incollaboration with the United Kingdom's intelligence "
                "allies and partners, andby a wide range of intelligence "
                "committees, sub-committees or other workinggroups "
                "established over the years as necessary to address "
                "numerousinter-departmental, cross-directorate or "
                "multi-disciplinary intelligenceproblems and issues."
            ),
        )
        self.assertEqual(self.record.arrangement, "")
        self.assertEqual(self.record.publication_note, [])
        self.assertEqual(
            self.record.related_materials,
            (
                {
                    "description": (
                        "Papers and reports of the pre-1964 single-service"
                        " intelligence directorates can be found in:"
                    ),
                    "links": [
                        {
                            "id": "C1931",
                            "href": "/catalogue/id/C1931/",
                            "text": "ADM 223",
                        },
                        {
                            "id": "C2095",
                            "href": "/catalogue/id/C2095/",
                            "text": "AIR 40",
                        },
                        {
                            "id": "C14314",
                            "href": "/catalogue/id/C14314/",
                            "text": "WO 106",
                        },
                        {
                            "id": "C14414",
                            "href": "/catalogue/id/C14414/",
                            "text": "WO 208",
                        },
                    ],
                },
            ),
        )
        self.assertEqual(
            self.record.description,
            (
                """<span class="scopecontent"><p>The series consists of a """
                "collection of reports and papers produced by some of "
                "the many intelligence conferences or working parties "
                "in which the Joint Intelligence Bureau and Defence "
                "Intelligence Staff participated, often in "
                "collaboration with the United Kingdom's "
                "intelligence allies and partners, and by a wide "
                "range of intelligence committees, sub-committees or "
                "other working groups established over the years as "
                "necessary to address numerous inter-departmental, "
                "cross-directorate or multi-disciplinary intelligence "
                "problems and issues.</p></span>"
            ),
        )
        self.assertEqual(self.record.separated_materials, ())
        self.assertEqual(self.record.unpublished_finding_aids, [])
        self.assertEqual(len(self.record.hierarchy), 2)
        self.assertEqual(self.record.next, None)
        self.assertEqual(self.record.previous, None)
        self.assertEqual(self.record.parent, None)
        self.assertEqual(self.record.is_tna, True)
        self.assertEqual(self.record.is_digitised, False)

    def test_response_00149557ca64456a8a41e44f14621801_1(self):

        fixture_path = (
            f"{settings.BASE_DIR}"
            "/test/records/fixtures/response_00149557ca64456a8a41e44f14621801_1.json"
        )
        with open(fixture_path, "r") as f:
            fixture_contents = json.loads(f.read())
        self.response = APIResponse(deepcopy(fixture_contents["data"][0]))
        self.record = self.response.record
        self.assertEqual(self.record.iaid, "00149557ca64456a8a41e44f14621801_1")
        self.assertEqual(self.record.source, "CAT")
        self.assertEqual(self.record.custom_record_type, "CAT")
        self.assertEqual(self.record.reference_number, "LITV 2/D63/Z/1")
        self.assertEqual(self.record.date_covering, "2015-07-31")
        self.assertEqual(self.record.creator, [])
        self.assertEqual(self.record.dimensions, "")
        self.assertEqual(self.record.former_department_reference, "")
        self.assertEqual(self.record.former_pro_reference, "")
        self.assertEqual(self.record.language, "")
        self.assertEqual(self.record.legal_status, "Public Record")
        self.assertEqual(self.record.level, "Piece")
        self.assertEqual(self.record.level_code, 6)
        self.assertEqual(self.record.map_designation, "")
        self.assertEqual(self.record.map_scale, "")
        self.assertEqual(self.record.note, "")
        self.assertEqual(self.record.physical_condition, "")
        self.assertEqual(self.record.physical_description, "1 digital record")
        self.assertEqual(self.record.held_by, "The National Archives, Kew")
        self.assertEqual(self.record.held_by_id, "A13530124")
        self.assertEqual(self.record.held_by_url, "/catalogue/id/A13530124/")
        self.assertEqual(self.record.access_condition, "Open on Transfer")
        self.assertEqual(
            self.record.closure_status, "Open Document, Open Description"
        )
        self.assertEqual(self.record.record_opening, "17 July 2018")
        self.assertEqual(self.record.accruals, "")
        self.assertEqual(self.record.accumulation_dates, "")
        self.assertEqual(self.record.appraisal_information, "")
        self.assertEqual(self.record.copies_information, "")
        self.assertEqual(self.record.custodial_history, "")
        self.assertEqual(self.record.immediate_source_of_acquisition, [])
        self.assertEqual(self.record.location_of_originals, [])
        self.assertEqual(self.record.restrictions_on_use, "")
        self.assertEqual(self.record.administrative_background, "")
        self.assertEqual(
            self.record.arrangement,
            (
                """<span class=\"wrapper\">This born digital """
                """record was arranged under the following file structure: """
                """<span class=\"ref\" """
                """target=\"1ec57aac-e02e-497e-bba8-150d6f392edb\">LITV 2"""
                """</span>&gt;&gt; <span class=\"ref\" """
                """href=\"1ec57aac-e02e-497e-bba8-150d6f392edb\""""
                """ target=\"986a6839-6ffd-463a-9c91-876c6037d41d\">"""
                """Evidence_Records</span></span>"""
            ),
        )
        self.assertEqual(self.record.publication_note, [])
        self.assertEqual(
            self.record.related_materials,
            (
                {
                    "description": "This is a redacted record. To make a Freedom of Information request for the full record go to",
                    "links": [
                        {
                            "id": "00149557ca64456a8a41e44f14621801",
                            "href": "/catalogue/id/00149557ca64456a8a41e44f14621801/",
                            "text": "LITV 2/D63/Z",
                        },
                    ],
                },
            ),
        )
        self.assertEqual(
            self.record.description,
            "Witness statement of Clive Timmons dated 11 February 2015",
        )
        self.assertEqual(self.record.separated_materials, ())
        self.assertEqual(self.record.unpublished_finding_aids, [])
        self.assertEqual(len(self.record.hierarchy), 3)
        self.assertEqual(self.record.next, None)
        self.assertEqual(self.record.previous, None)
        self.assertEqual(self.record.parent, None)
        self.assertEqual(self.record.is_tna, True)
        self.assertEqual(self.record.is_digitised, True)
