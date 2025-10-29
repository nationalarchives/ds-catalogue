from unittest.mock import patch

from app.records.models import Record
from django.test import SimpleTestCase


class RecordModelTests(SimpleTestCase):
    maxDiff = None

    def setUp(self):

        self.template_details = {"some value": "some value"}

    def test_empty_for_optional_attributes(self):
        self.record = Record(self.template_details)

        self.assertEqual(self.record.iaid, "")
        self.assertEqual(self.record.source, "")
        self.assertEqual(self.record.custom_record_type, "")
        self.assertEqual(self.record.reference_number, "")
        self.assertEqual(self.record.title, "")
        self.assertEqual(self.record.summary_title, "")
        self.assertEqual(self.record.clean_summary_title, "")
        self.assertEqual(self.record.date_covering, "")
        self.assertEqual(self.record.creator, [])
        self.assertEqual(self.record.dimensions, "")
        self.assertEqual(self.record.former_department_reference, "")
        self.assertEqual(self.record.former_pro_reference, "")
        self.assertEqual(self.record.language, "")
        self.assertEqual(self.record.legal_status, "")
        self.assertEqual(self.record.level, "")
        self.assertEqual(self.record.level_code, None)
        self.assertEqual(self.record.map_designation, "")
        self.assertEqual(self.record.map_scale, "")
        self.assertEqual(self.record.note, "")
        self.assertEqual(self.record.physical_condition, "")
        self.assertEqual(self.record.physical_description, "")
        self.assertEqual(self.record.held_by, "")
        self.assertEqual(self.record.held_by_id, "")
        self.assertEqual(self.record.held_by_url, "")
        self.assertEqual(self.record.held_by_count, "Unknown number of")
        self.assertEqual(self.record.access_condition, "")
        self.assertEqual(self.record.closure_status, "")
        self.assertEqual(self.record.record_opening, "")
        self.assertEqual(self.record.accruals, "")
        self.assertEqual(self.record.accumulation_dates, "")
        self.assertEqual(self.record.appraisal_information, "")
        self.assertEqual(self.record.copies_information, "")
        self.assertEqual(self.record.custodial_history, "")
        self.assertEqual(self.record.immediate_source_of_acquisition, "")
        self.assertEqual(self.record.location_of_originals, [])
        self.assertEqual(self.record.restrictions_on_use, "")
        self.assertEqual(self.record.administrative_background, "")
        self.assertEqual(self.record.arrangement, "")
        self.assertEqual(self.record.publication_note, [])
        self.assertEqual(self.record.related_materials, ())
        self.assertEqual(self.record.description, "")
        self.assertEqual(self.record.clean_description, None)
        self.assertEqual(self.record.short_description, "")
        self.assertEqual(self.record.separated_materials, ())
        self.assertEqual(self.record.unpublished_finding_aids, [])
        self.assertEqual(self.record.hierarchy, ())
        self.assertEqual(self.record.next, None)
        self.assertEqual(self.record.previous, None)
        self.assertEqual(self.record.parent, None)
        self.assertEqual(self.record.is_tna, False)
        self.assertEqual(self.record.is_digitised, False)
        self.assertEqual(self.record.subjects, [])
        self.assertEqual(self.record.subjects_enrichment, {})
        self.assertEqual(self.record.has_subjects_enrichment, False)

    def test_iaid(self):

        self.record = Record(self.template_details)

        # patch raw data
        self.record._raw["iaid"] = "C123456"

        self.assertEqual(self.record.iaid, "C123456")

    def test_iaid_other_places(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["@previous"] = {
            "@admin": {"id": "C11827824"},
        }
        self.record._raw["@next"] = {
            "@admin": {"id": "C11827826"},
        }
        self.record._raw["parent"] = {"@admin": {"id": "C199"}}

        self.assertEqual(self.record.previous.iaid, "C11827824")
        self.assertEqual(self.record.next.iaid, "C11827826")
        self.assertEqual(self.record.parent.iaid, "C199")

    def test_source(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["source"] = "CAT"
        self.assertEqual(self.record.source, "CAT")

    def test_custom_record_type(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["source"] = "CAT"
        self.assertEqual(self.record.custom_record_type, "CAT")

    def test_reference_number(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["referenceNumber"] = "LO 2"
        self.assertEqual(self.record.reference_number, "LO 2")

    def test_reference_number_other_places(self):
        self.record = Record(self.template_details)
        # patch raw
        self.record._raw["@previous"] = {
            "identifier": [
                {
                    "reference_number": "LO 3",
                },
            ],
        }
        self.record._raw["@next"] = {
            "identifier": [
                {
                    "reference_number": "LO 1",
                },
            ],
        }
        self.record._raw["parent"] = {
            "identifier": [
                {
                    "reference_number": "LO",
                },
            ],
        }

        self.assertEqual(self.record.previous.reference_number, "LO 3")
        self.assertEqual(self.record.next.reference_number, "LO 1")
        self.assertEqual(self.record.parent.reference_number, "LO")

    def test_title(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["title"] = (
            "Ministry of Defence: Joint Intelligence Bureau and Defence Intelligence Staff: "
            "Intelligence Conferences, Committees and Working Parties: Reports and Papers."
        )
        self.assertEqual(
            self.record.title,
            (
                "Ministry of Defence: Joint Intelligence Bureau and Defence Intelligence Staff: "
                "Intelligence Conferences, Committees and Working Parties: Reports and Papers."
            ),
        )

    def test_summary_title(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["summaryTitle"] = "This record has no title"
        self.assertEqual(self.record.summary_title, "This record has no title")

    def test_summary_title_other_places(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["iaid"] = "C11827825"
        self.record._raw["groupArray"] = [
            {"value": "record"},
            {"value": "tna"},
        ]
        self.record._raw["@previous"] = {
            "summary": {
                "title": "Law Officers' Department: Patents for Inventions"
            },
        }
        self.record._raw["@next"] = {
            "summary": {
                "title": "Law Officers' Department: Law Officers' Opinions"
            },
        }
        self.record._raw["parent"] = {
            "summary": {
                "title": "Records created or inherited by the Law Officers' Department"
            },
        }

        self.record._raw["@hierarchy"] = [
            {
                "identifier": [
                    {
                        "reference_number": "AIR",
                    }
                ],
                "summary": {
                    "title": "Records created or inherited by the Air Ministry, the Royal Air Force, and related..."
                },
            },
        ]
        self.assertEqual(
            self.record.hierarchy[0].summary_title,
            "Records created or inherited by the Air Ministry, the Royal Air Force, and related...",
        )

        self.assertEqual(
            self.record.previous.summary_title,
            "Law Officers' Department: Patents for Inventions",
        )
        self.assertEqual(
            self.record.next.summary_title,
            "Law Officers' Department: Law Officers' Opinions",
        )
        self.assertEqual(
            self.record.parent.summary_title,
            "Records created or inherited by the Law Officers' Department",
        )

    def test_clean_summary_title(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["cleanSummaryTitle"] = (
            "PART I - ITEMS DISCUSSED AT THE MEETING1."
        )
        self.assertEqual(
            self.record.clean_summary_title,
            "PART I - ITEMS DISCUSSED AT THE MEETING1.",
        )

    def test_clean_summary_title_fallback(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["summaryTitle"] = "FALLBACK summaryTitle"
        self.assertEqual(
            self.record.clean_summary_title,
            "FALLBACK summaryTitle",
        )

    def test_date_covering(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["dateCovering"] = "2015-07-31"
        self.assertEqual(self.record.date_covering, "2015-07-31")

    def test_creator(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["creator"] = [
            "Donop, Stanley Brenton, 1860-1941",
            "Lambart, Frederick Rudolph, 1865-1946",
            "Thomson, William Montgomerie, 1877-1963",
        ]
        self.assertEqual(
            self.record.creator,
            [
                "Donop, Stanley Brenton, 1860-1941",
                "Lambart, Frederick Rudolph, 1865-1946",
                "Thomson, William Montgomerie, 1877-1963",
            ],
        )

    def test_dimensions(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["dimensions"] = "63.5 cm x 68.5 cm"
        self.assertEqual(self.record.dimensions, "63.5 cm x 68.5 cm")

    def test_former_department_reference(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["formerDepartmentReference"] = "African No. 355"
        self.assertEqual(
            self.record.former_department_reference, "African No. 355"
        )

    def test_former_pro_reference(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["formerProReference"] = "ASSI 35"
        self.assertEqual(self.record.former_pro_reference, "ASSI 35")

    def test_language(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["language"] = "Chinese, English, Malay and Tamil"
        self.assertEqual(
            self.record.language, "Chinese, English, Malay and Tamil"
        )

    def test_legal_status(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["legalStatus"] = "Public Record(s)"
        self.assertEqual(self.record.legal_status, "Public Record(s)")

    def test_level_tna(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["groupArray"] = [
            {"value": "record"},
            {"value": "tna"},
        ]
        self.record._raw["level"] = {
            "code": 7,
        }
        self.assertEqual(self.record.level, "Item")

    def test_level_non_tna(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["level"] = {
            "code": 7,
        }
        self.assertEqual(self.record.level, "Sub-sub-series")

    def test_level_code(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["level"] = {
            "code": 7,
        }
        self.assertEqual(self.record.level_code, 7)

    def test_level_code_other_places(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["iaid"] = "C11827825"
        self.record._raw["groupArray"] = [
            {"value": "record"},
            {"value": "tna"},
        ]
        self.record._raw["@hierarchy"] = [
            {
                "identifier": [
                    {
                        "reference_number": "AIR",
                    }
                ],
                "level": {"code": 1},
            },
        ]
        self.assertEqual(self.record.hierarchy[0].level_code, 1)

    def test_map_designation(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["mapDesignation"] = "OS 1:2500 County Series"
        self.assertEqual(self.record.map_designation, "OS 1:2500 County Series")

    def test_map_scale(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["mapScale"] = "1:2500"
        self.assertEqual(self.record.map_scale, "1:2500")

    def test_note(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["note"] = (
            "Details have been added from C 32/18, which also gives "
            "information about further process."
        )
        self.assertEqual(
            self.record.note,
            "Details have been added from C 32/18,"
            " which also gives information about further process.",
        )

    def test_physical_condition(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["physicalCondition"] = "In ink, on tracing linen"
        self.assertEqual(
            self.record.physical_condition, "In ink, on tracing linen"
        )

    def test_physical_description(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["physicalDescription"] = "file(s)"
        self.assertEqual(self.record.physical_description, "file(s)")

    def test_held_by(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["heldBy"] = "National Maritime Museum"
        self.assertEqual(self.record.held_by, "National Maritime Museum")

    def test_held_by_id(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["heldById"] = "A13530841"
        self.assertEqual(self.record.held_by_id, "A13530841")

    def test_valid_held_by_url(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["heldById"] = "A13530841"
        # TODO: Temporary link to Discovery until archon template is ready
        # self.assertEqual(self.record.held_by_url, "/catalogue/id/A13530841/")
        self.assertEqual(
            self.record.held_by_url,
            "https://discovery.nationalarchives.gov.uk/details/a/A13530841",
        )

    # TODO: Re-enable this test when archon template is ready
    # def test_invalid_data_for_held_by_url(self):
    #     self.record = Record(self.template_details)
    #     # patch raw data
    #     self.record._raw["iaid"] = "C12345"
    #     self.record._raw["heldById"] = "INVALID"

    #     with self.assertLogs("app.records.models", level="WARNING") as lc:
    #         result = self.record.held_by_url
    #     self.assertEqual(self.record.held_by_url, result)
    #     self.assertIn(
    #         "WARNING:app.records.models:held_by_url:Record(C12345):No reverse match for record_details with held_by_id=INVALID",
    #         lc.output,
    #     )

    def test_held_by_count(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["heldByCount"] = 12345
        self.assertEqual(self.record.held_by_count, "12,345")

    def test_access_condition(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["accessCondition"] = "Subject to 30 year closure"
        self.assertEqual(
            self.record.access_condition, "Subject to 30 year closure"
        )

    def test_closure_status(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["closureStatus"] = "Open Document, Open Description"
        self.assertEqual(
            self.record.closure_status, "Open Document, Open Description"
        )

    def test_record_opening(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["recordOpening"] = "01 September 2007"
        self.assertEqual(self.record.record_opening, "01 September 2007")

    def test_accruals(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["accruals"] = "Series is accruing"
        self.assertEqual(self.record.accruals, "Series is accruing")

    def test_accumulation_dates(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["accumulationDates"] = "File series began in 1971"
        self.assertEqual(
            self.record.accumulation_dates, "File series began in 1971"
        )

    def test_appraisal_information(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["appraisalInformation"] = (
            "Policy and contractual records have been preserved."
        )
        self.assertEqual(
            self.record.appraisal_information,
            "Policy and contractual records have been preserved.",
        )

    def test_copies_information(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["copiesInformation"] = (
            "Microform copies are available on open access in Microfilm "
            "Reading Room (MRR) as FO 605. They must be ordered by this reference"
        )
        self.assertEqual(
            self.record.copies_information,
            (
                "Microform copies are available on open access in Microfilm "
                "Reading Room (MRR) as FO 605. They must be ordered by this reference"
            ),
        )

    def test_custodial_history(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["custodialHistory"] = (
            "Transferred to the Employment Department in 1988 and the Department for Education and Employment in 1995."
        )
        self.assertEqual(
            self.record.custodial_history,
            "Transferred to the Employment Department in 1988 and the Department for Education and Employment in 1995.",
        )

    def test_immediate_source_of_acquisition(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["immediateSourceOfAcquisition"] = (
            "<p>since 1947 Essex Record Office</p>"
            "<p>Charles Cornwallis, 5th Baron Braybrooke, 1823-1902</p>"
            "<p>Henry Seymour Neville, 9th Baron Braybrooke, 1897-1990</p>"
        )
        self.assertEqual(
            self.record.immediate_source_of_acquisition,
            (
                "<p>since 1947 Essex Record Office</p>"
                "<p>Charles Cornwallis, 5th Baron Braybrooke, 1823-1902</p>"
                "<p>Henry Seymour Neville, 9th Baron Braybrooke, 1897-1990</p>"
            ),
        )

    def test_location_of_originals(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["locationOfOriginals"] = [
            "Museum of London Library",
            "Victoria & Albert Museum, Archive of Art and Design",
        ]
        self.assertEqual(
            self.record.location_of_originals,
            [
                "Museum of London Library",
                "Victoria & Albert Museum, Archive of Art and Design",
            ],
        )

    def test_restrictions_on_use(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["restrictionsOnUse"] = (
            "3 working days notice to produce"
        )
        self.assertEqual(
            self.record.restrictions_on_use, "3 working days notice to produce"
        )

    def test_administrative_background(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["administrativeBackground"] = (
            "The Industrial Relations Department was set up as soon as the "
            "British Transport Commission began functioning and continued in "
            "existence until the end of the British Railway Board. In 1983 it "
            "was renamed Employee Relations Department."
        )
        self.assertEqual(
            self.record.administrative_background,
            (
                "The Industrial Relations Department was set up as soon as the "
                "British Transport Commission began functioning and continued in "
                "existence until the end of the British Railway Board. In 1983 it "
                "was renamed Employee Relations Department."
            ),
        )

    def test_arrangement(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["arrangement"] = (
            "Former reference order within two accessions (AN 171/1-648 and AN 171/649-970)."
        )
        self.assertEqual(
            self.record.arrangement,
            "Former reference order within two accessions (AN 171/1-648 and AN 171/649-970).",
        )

    def test_publication_note(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["publicationNote"] = [
            "Printed in Rymer's Foedera (1709 edition), viii 90-91.",
        ]
        self.assertEqual(
            self.record.publication_note,
            [
                "Printed in Rymer's Foedera (1709 edition), viii 90-91.",
            ],
        )

    def test_related_materials(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["relatedMaterials"] = [
            {
                "description": "Post December 1946 minutes in",
                "links": ['<a href="C5762">DEFE 4</a>'],
            }
        ]

        self.assertEqual(
            self.record.related_materials,
            (
                {
                    "description": "Post December 1946 minutes in",
                    "links": [
                        {
                            "id": "C5762",
                            "href": "/catalogue/id/C5762/",
                            "text": "DEFE 4",
                        }
                    ],
                },
            ),
        )

    def test_description(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["description"] = {
            "value": (
                """C16248: Online descriptions of individual records can be viewed """
                """on Discovery, see <a class=\"extref\" """
                """href=\"f41eb-1496-446c-8bf8-21dc681223da\">RM 2</a>."""
                """"C16248: Also see the Royal Botanic Gardens, Kew """
                """<a class=\"extref\" href=\"https://www2.calmview.co.uk/kew/calmview"""
                """/Record.aspx?src=CalmView.Catalog&amp;id=MN&amp;pos=1\">online catalogue</a>"""
                """C244: <span class=\"emph-italic\">Censuses of Population</span>"""
                """C244: <span class=\"list\"><span class=\"item\">Correspondence and """
                """papers</span></span>"""
            ),
            "schema": "",
            "raw": "",
        }
        self.assertEqual(
            self.record.description,
            (
                """C16248: Online descriptions of individual records can be viewed """
                """on Discovery, see <a class=\"extref\" """
                """href=\"f41eb-1496-446c-8bf8-21dc681223da\">RM 2</a>."""
                """"C16248: Also see the Royal Botanic Gardens, Kew """
                """<a class=\"extref\" href=\"https://www2.calmview.co.uk/kew/calmview"""
                """/Record.aspx?src=CalmView.Catalog&amp;id=MN&amp;pos=1\">online catalogue</a>"""
                """C244: <span class=\"emph-italic\">Censuses of Population</span>"""
                """C244: <span class=\"list\"><span class=\"item\">Correspondence and """
                """papers</span></span>"""
            ),
        )

    def test_short_description(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["description"] = {
            "value": "",
            "short": (
                """This series contains the vast majority of registered wills """
                """proved before the Prerogative Court of Canterbury and other """
                """jurisdictions that exercised probate jurisdiction in the place """
                """of the Court, the most important of which was the Court for Probate ..."""
            ),
        }
        self.assertEqual(
            self.record.short_description,
            (
                """This series contains the vast majority of registered wills """
                """proved before the Prerogative Court of Canterbury and other """
                """jurisdictions that exercised probate jurisdiction in the place """
                """of the Court, the most important of which was the Court for Probate ..."""
            ),
        )
        self.assertTrue(self.record.short_description.endswith("..."))

    def test_raw_description(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["description"] = {
            "value": "",
            "schema": "",
            "raw": (
                """C16248: Online descriptions of individual records can be viewed """
                """on Discovery, see <a class=\"extref\" """
                """href=\"f41eb-1496-446c-8bf8-21dc681223da\">RM 2</a>."""
                """"C16248: Also see the Royal Botanic Gardens, Kew """
                """<a class=\"extref\" href=\"https://www2.calmview.co.uk/kew/calmview"""
                """/Record.aspx?src=CalmView.Catalog&amp;id=MN&amp;pos=1\">online catalogue</a>"""
                """C244: <span class=\"emph-italic\">Censuses of Population</span>"""
                """C244: <span class=\"list\"><span class=\"item\">Correspondence and """
                """papers</span></span>"""
            ),
        }
        self.assertEqual(
            self.record.raw_description,
            (
                """C16248: Online descriptions of individual records can be viewed """
                """on Discovery, see <a class=\"extref\" """
                """href=\"f41eb-1496-446c-8bf8-21dc681223da\">RM 2</a>."""
                """"C16248: Also see the Royal Botanic Gardens, Kew """
                """<a class=\"extref\" href=\"https://www2.calmview.co.uk/kew/calmview"""
                """/Record.aspx?src=CalmView.Catalog&amp;id=MN&amp;pos=1\">online catalogue</a>"""
                """C244: <span class=\"emph-italic\">Censuses of Population</span>"""
                """C244: <span class=\"list\"><span class=\"item\">Correspondence and """
                """papers</span></span>"""
            ),
        )

    def test_clean_description(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["cleanDescription"] = (
            "Appellant: <mark>Florence</mark> Emily <mark>Fenn</mark>. Respondent: Ernest William <mark>Fenn</mark>. Type: Wife's petition for divorce [wd]. "
        )
        self.assertEqual(
            self.record.clean_description,
            (
                "Appellant: <mark>Florence</mark> Emily <mark>Fenn</mark>. Respondent: Ernest William <mark>Fenn</mark>. Type: Wife's petition for divorce [wd]. "
            ),
        )

    def test_separated_materials(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["separatedMaterials"] = [
            {
                "description": "for 4 maps extracted from this item see",
                "links": [
                    '<a href="C8956177">MFQ 1/761/7</a>',
                    '<a href="C8956176">MFQ 1/761/6</a>',
                    '<a href="C8956175">MFQ 1/761/5</a>',
                    '<a href="C8956174">MFQ 1/761/4</a>',
                ],
            }
        ]

        self.assertEqual(
            self.record.separated_materials,
            (
                {
                    "description": "for 4 maps extracted from this item see",
                    "links": [
                        {
                            "id": "C8956177",
                            "href": "/catalogue/id/C8956177/",
                            "text": "MFQ 1/761/7",
                        },
                        {
                            "id": "C8956176",
                            "href": "/catalogue/id/C8956176/",
                            "text": "MFQ 1/761/6",
                        },
                        {
                            "id": "C8956175",
                            "href": "/catalogue/id/C8956175/",
                            "text": "MFQ 1/761/5",
                        },
                        {
                            "id": "C8956174",
                            "href": "/catalogue/id/C8956174/",
                            "text": "MFQ 1/761/4",
                        },
                    ],
                },
            ),
        )

    def test_unpublished_finding_aids(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["unpublishedFindingAids"] = [
            "There is a general index in BT 4 . There is a subject index in BT 19.",
        ]
        self.assertEqual(
            self.record.unpublished_finding_aids,
            [
                "There is a general index in BT 4 . There is a subject index in BT 19.",
            ],
        )

    def test_hierarchy(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["iaid"] = "C11827825"
        self.record._raw["groupArray"] = [
            {"value": "record"},
            {"value": "tna"},
        ]
        self.record._raw["@hierarchy"] = [
            {
                "@admin": {"id": "C8"},
                "identifier": [
                    {
                        "reference_number": "AIR",
                    }
                ],
                "level": {"code": 1},
                "summary": {
                    "title": "Records created or inherited by the Air Ministry, the Royal Air Force, and related..."
                },
                "count": 723850,
            },
            {
                "@admin": {"id": "C955"},
                "level": {"code": 2},
                "summary": {
                    "title": "Records of the Department of the Master General of Personnel and the Air Member for..."
                },
                "count": 478127,
            },
            {
                "@admin": {"id": "C2133"},
                "identifier": [
                    {
                        "reference_number": "AIR 79",
                    }
                ],
                "level": {"code": 3},
                "summary": {
                    "title": "Air Ministry: Air Member for Personnel and predecessors: Airmen's Records"
                },
                "count": 319338,
            },
            {
                "@admin": {"id": "C3872067"},
                "identifier": [
                    {
                        "reference_number": "AIR 79/962",
                    }
                ],
                "level": {"code": 6},
                "summary": {
                    "title": "107079 - 107200 (Described at item level)."
                },
                "count": 123,
            },
            {
                "@admin": {"id": "C11827825"},
                "identifier": [
                    {
                        "reference_number": "AIR 79/962/107133",
                    }
                ],
                "level": {"code": 7},
                "summary": {"title": "Name: Percy Augustus Cecil Gadd."},
                "count": 1,
            },
        ]

        self.assertEqual(len(self.record.hierarchy), 3)

        for i, r in enumerate(
            zip(
                self.record.hierarchy,
                [
                    (
                        True,
                        "C8",
                        "/catalogue/id/C8/",
                        1,
                        "Department",
                        "AIR",
                        "Records created or inherited by the Air Ministry, the Royal Air Force, and related...",
                        "723,850",
                    ),
                    (
                        True,
                        "C2133",
                        "/catalogue/id/C2133/",
                        3,
                        "Series",
                        "AIR 79",
                        "Air Ministry: Air Member for Personnel and predecessors: Airmen's Records",
                        "319,338",
                    ),
                    (
                        True,
                        "C3872067",
                        "/catalogue/id/C3872067/",
                        6,
                        "Piece",
                        "AIR 79/962",
                        "107079 - 107200 (Described at item level).",
                        "123",
                    ),
                    (
                        True,
                        "C11827825",
                        "/catalogue/id/C11827825/",
                        7,
                        "Item",
                        "AIR 79/962/107133",
                        "Name: Percy Augustus Cecil Gadd.",
                        "1",
                    ),
                ],
            )
        ):
            with self.subTest(i):
                hierarchy_record, expected = r[0], r[1]
                self.assertIsInstance(hierarchy_record, Record)
                self.assertEqual(
                    (
                        hierarchy_record.is_tna,
                        hierarchy_record.iaid,
                        hierarchy_record.url,
                        hierarchy_record.level_code,
                        hierarchy_record.level,
                        hierarchy_record.reference_number,
                        hierarchy_record.summary_title,
                        hierarchy_record.hierarchy_count,
                    ),
                    expected,
                )

    def test_next(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["iaid"] = "C11827825"
        self.record._raw["groupArray"] = [
            {"value": "record"},
            {"value": "tna"},
        ]
        self.record._raw["@next"] = {
            "@admin": {"id": "C11827826"},
            "summary": {"title": "Name: William Wilson."},
            "level": {"code": 7},
            "identifier": [{"reference_number": "AIR 79/962/107134"}],
        }

        self.assertIsInstance(self.record.next, Record)
        self.assertEqual(
            (
                self.record.next.iaid,
                self.record.next.url,
                self.record.next.level_code,
                self.record.next.level,
                self.record.next.reference_number,
                self.record.next.summary_title,
            ),
            (
                "C11827826",
                "/catalogue/id/C11827826/",
                7,
                "Item",
                "AIR 79/962/107134",
                "Name: William Wilson.",
            ),
        )

    def test_previous(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["iaid"] = "C11827825"
        self.record._raw["groupArray"] = [
            {"value": "record"},
            {"value": "tna"},
        ]
        self.record._raw["@previous"] = {
            "@admin": {"id": "C11827824"},
            "summary": {"title": "Name: George Forster."},
            "level": {"code": 7},
            "identifier": [{"reference_number": "AIR 79/962/107132"}],
        }

        self.assertIsInstance(self.record.previous, Record)

        self.assertEqual(
            (
                self.record.previous.iaid,
                self.record.previous.url,
                self.record.previous.level_code,
                self.record.previous.level,
                self.record.previous.reference_number,
                self.record.previous.summary_title,
            ),
            (
                "C11827824",
                "/catalogue/id/C11827824/",
                7,
                "Item",
                "AIR 79/962/107132",
                "Name: George Forster.",
            ),
        )

    def test_parent(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["parent"] = {
            "@admin": {"id": "C199"},
            "identifier": [
                {
                    "reference_number": "LO",
                },
            ],
            "summary": {
                "title": "Records created or inherited by the Law Officers' Department"
            },
        }

        self.assertIsInstance(self.record.parent, Record)
        self.assertEqual(
            (
                self.record.parent.iaid,
                self.record.parent.reference_number,
                self.record.parent.summary_title,
            ),
            (
                "C199",
                "LO",
                "Records created or inherited by the Law Officers' Department",
            ),
        )

    def test_is_tna_true(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["groupArray"] = [
            {"value": "record"},
            {"value": "tna"},
        ]
        self.assertEqual(self.record.is_tna, True)

    def test_is_tna_false(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["groupArray"] = [
            {"value": "record"},
            {"value": "nonTna"},
        ]
        self.assertEqual(self.record.is_tna, False)

    def test_is_digitised_true(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["digitised"] = True
        self.assertEqual(self.record.is_digitised, True)

    def test_is_digitised_false(self):
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["digitised"] = False
        self.assertEqual(self.record.is_digitised, False)

    def test_url(self):
        self.record = Record(self.template_details)

        # patch raw data
        self.record._raw["iaid"] = "C11827825"

        self.assertEqual(
            self.record.url,
            "/catalogue/id/C11827825/",
        )

    def test_subjects_with_data(self):
        """Test that subjects returns list of subjects when present"""
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["subjects"] = [
            "Military history",
            "World War II",
            "Intelligence services",
            "Government records",
        ]
        self.assertEqual(
            self.record.subjects,
            [
                "Military history",
                "World War II",
                "Intelligence services",
                "Government records",
            ],
        )

    @patch("app.records.models.SUBJECTS_LIMIT", 3)
    def test_subjects_respects_limit(self):
        """Test that subjects list is limited to SUBJECTS_LIMIT"""
        self.record = Record(self.template_details)
        # Create more subjects than the limit
        long_subjects_list = [
            "Subject 1",
            "Subject 2",
            "Subject 3",
            "Subject 4",  # This should be excluded
            "Subject 5",  # This should be excluded
        ]
        self.record._raw["subjects"] = long_subjects_list

        # Should only return first 3 items (mocked SUBJECTS_LIMIT)
        expected = long_subjects_list[:3]
        self.assertEqual(self.record.subjects, expected)
        self.assertEqual(len(self.record.subjects), 3)

    def test_subjects_with_single_item(self):
        """Test that subjects works correctly with a single item"""
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["subjects"] = ["Military records"]
        self.assertEqual(self.record.subjects, ["Military records"])

    def test_subjects_empty_list_in_data(self):
        """Test that subjects handles empty list in API data"""
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["subjects"] = []
        self.assertEqual(self.record.subjects, [])

    @patch("app.records.models.SUBJECTS_LIMIT", 5)
    def test_subjects_exactly_at_limit(self):
        """Test that subjects works when exactly at the limit"""
        self.record = Record(self.template_details)
        # Create exactly SUBJECTS_LIMIT items (mocked as 5)
        exact_limit_subjects = [
            "Subject 1",
            "Subject 2",
            "Subject 3",
            "Subject 4",
            "Subject 5",
        ]
        self.record._raw["subjects"] = exact_limit_subjects
        self.assertEqual(self.record.subjects, exact_limit_subjects)
        self.assertEqual(len(self.record.subjects), 5)

    def test_subjects_caching(self):
        """Test that subjects property is cached (since it uses @cached_property)"""
        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["subjects"] = ["Test subject"]

        # First access
        first_result = self.record.subjects

        # Modify the raw data
        self.record._raw["subjects"] = ["Modified subject"]

        # Second access should return cached result
        second_result = self.record.subjects

        # Should be the same object (cached)
        self.assertIs(first_result, second_result)
        self.assertEqual(
            second_result, ["Test subject"]
        )  # Original value, not modified
