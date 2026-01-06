from unittest.mock import patch

from app.lib.xslt_transformations import SERIES_TRANSFORMATIONS
from app.records.models import Record
from config.jinja2 import sanitise_record_field
from django.test import SimpleTestCase


class SeriesTransformationTests(SimpleTestCase):
    maxDiff = None

    def setUp(self):

        self.template_details = {"some value": "some value"}

    def test_description_having_hierarchy_series_with_config_series_transformation(
        self,
    ):
        """Test that record.hierarchy_series returns the correct series Record
        and that description field is transformed correctly for a record
        having a hierarchy series with a configured transformation."""

        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["id"] = "C16128233"
        self.record._raw["reference_number"] = "ADM 240/1/1"
        self.record._raw["groupArray"] = [
            {"value": "record"},
            {"value": "tna"},
        ]
        self.record._raw["description"] = {
            "value": '<span class="scopecontent"><p>Name: <span class="persname"><span altrender="forenames" class="emph">Lewis Martin </span><span altrender="surname" class="emph">Wibmer</span></span>. </p><p>Rank: <span altrender="rank" class="emph">Commander</span>. </p><p>Date of Seniority: 07 March 1904. </p><p>Date of Birth: [not given]. </p><p>Place of Birth: [not given]. </p></span>',
            "raw": '<scopecontent>\r\n\t<p>Name: <persname><emph altrender="forenames">Lewis Martin </emph>\r\n\t\t\t<emph altrender="surname">Wibmer</emph></persname>. </p>\r\n\t<p>Rank: <emph altrender="rank">Commander</emph>. </p>\r\n\t<p>Date of Seniority: 07 March 1904. </p>\r\n\t<p>Date of Birth: [not given]. </p>\r\n\t<p>Place of Birth: [not given]. </p>\r\n</scopecontent>',
            "short": "\r\n\tName: Lewis Martin \r\n\t\t\tWibmer. \r\n\tRank: Commander. \r\n\tDate of Seniority: 07 March 1904. \r\n\tDate of Birth: [not given]. \r\n\tPlace of Birth: [not given]. \r\n",
            "noHtml": "\r\n\tName: Lewis Martin \r\n\t\t\tWibmer. \r\n\tRank: Commander. \r\n\tDate of Seniority: 07 March 1904. \r\n\tDate of Birth: [not given]. \r\n\tPlace of Birth: [not given]. \r\n",
        }

        self.record._raw["@hierarchy"] = [
            {
                "@admin": {"id": "C4"},
                "identifier": [{"reference_number": "ADM"}],
                "level": {"code": 1},
                "source": {"value": "CAT"},
                "summary": {
                    "title": "Records of the Admiralty, Naval Forces, Royal Marines, Coastguard, and related bodies"
                },
                "count": 2470001,
            },
            {
                "@admin": {"id": "C730"},
                "level": {"code": 2},
                "source": {"value": "CAT"},
                "summary": {
                    "title": "Records of the Royal Naval Volunteer Reserve"
                },
                "count": 88250,
            },
            {
                "@admin": {"id": "C1948"},
                "identifier": [{"reference_number": "ADM 240"}],
                "level": {"code": 3},
                "source": {"value": "CAT"},
                "summary": {
                    "title": "Admiralty: Royal Naval Reserve: Officers' Service Records"
                },
                "count": 28317,
            },
            {
                "@admin": {"id": "C2054560"},
                "identifier": [{"reference_number": "ADM 240/1"}],
                "level": {"code": 6},
                "source": {"value": "CAT"},
                "summary": {
                    "title": "Commanders. Date of Seniority: 1904-1907, Date of latest entry (approximate): 1907...."
                },
                "count": 32,
            },
            {
                "@admin": {"id": "C16128233"},
                "identifier": [{"reference_number": "ADM 240/1/1"}],
                "level": {"code": 7},
                "source": {"value": "CAT"},
                "summary": {
                    "title": "Name: Lewis Martin   Wibmer.  Rank: Commander.  Date of Seniority: 07 March 1904...."
                },
                "count": 1,
            },
        ]

        self.assertIsInstance(self.record.hierarchy_series, Record)
        self.assertEqual(self.record.hierarchy_series.id, "C1948")
        self.assertEqual(self.record.hierarchy_series.level, "Series")
        self.assertEqual(self.record.hierarchy_series.level_code, 3)
        self.assertEqual(
            self.record.hierarchy_series.reference_number, "ADM 240"
        )
        self.assertEqual(
            SERIES_TRANSFORMATIONS.get(
                self.record.hierarchy_series.reference_number
            ),
            "ADM_240.xsl",
        )

        self.assertEqual(
            self.record.description,
            """<dl class="tna-dl tna-dl--plain tna-dl--dotted">
<dt>Name</dt>
<dd>Wibmer, Lewis Martin </dd>
<dt>Rank</dt>
<dd>Commander</dd>
<dt>Date of seniority</dt>
<dd>07 March 1904. </dd>
<dt>Date of birth</dt>
<dd>[not given]</dd>
<dt>Place of birth</dt>
<dd>[not given]</dd>
</dl>""",
        )

        # test sanitisation as does in template
        self.assertEqual(
            sanitise_record_field(self.record.description),
            """<dl class="tna-dl tna-dl--plain tna-dl--dotted">
<dt>Name</dt>
<dd>Wibmer, Lewis Martin </dd>
<dt>Rank</dt>
<dd>Commander</dd>
<dt>Date of seniority</dt>
<dd>07 March 1904. </dd>
<dt>Date of birth</dt>
<dd>[not given]</dd>
<dt>Place of birth</dt>
<dd>[not given]</dd>
</dl>""",
        )

    def test_description_having_hierarchy_series_without_config_series_transformation(
        self,
    ):
        """Test that record.hierarchy_series returns the correct series Record
        and that description field is transformed correctly for a record
        having a hierarchy series without a configured transformation.

        Tests fallback to schema based transformation with Generic.xsl as description
        field does not have schema value"""

        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["id"] = "C4107384"
        self.record._raw["reference_number"] = "ADM 101/240"
        self.record._raw["groupArray"] = [
            {"value": "record"},
            {"value": "tna"},
        ]
        self.record._raw["description"] = {
            "value": '<span class="scopecontent"><p>MIRANDA, Surgeon H Slade: wounded of naval brigade in New Zealand: notes on Fiji.</p><p>For description purposes, ADM 101/240 has been split into two parts (1A and 1B), as follows: </p><p>Wounded of the Naval Brigade treated on board HMS Miranda, 29 April-31 Dec 1864: <a class="extref" href="C11529959">ADM 101/240/1A</a>. </p><p>HMS Miranda, 1 January -31 December 1864: <a class="extref" href="C11529960">ADM 101/240/1B</a>. </p><p>NOTE: The two parts are produced as a single document using this catalogue reference (ADM 101/240).</p></span>',
            "raw": "<scopecontent><p>MIRANDA, Surgeon H Slade: wounded of naval brigade in New Zealand: notes on Fiji.</p> <p>For description purposes, ADM 101/240 has been split into two parts (1A and 1B), as follows: </p> <p>Wounded of the Naval Brigade treated on board HMS Miranda, 29 April-31 Dec 1864: <extref href=&#34http://discovery.nationalarchives.gov.uk/SearchUI/details?Uri=C11529959&#34>ADM 101/240/1A</extref>. </p> <p>HMS Miranda, 1 January -31 December 1864: <extref href=&#34http://discovery.nationalarchives.gov.uk/SearchUI/details?Uri=C11529960&#34>ADM 101/240/1B</extref>. </p> <p>NOTE: The two parts are produced as a single document using this catalogue reference (ADM 101/240).</p></scopecontent>",
            "short": "MIRANDA, Surgeon H Slade: wounded of naval brigade in New Zealand: notes on Fiji. For description purposes, ADM 101/240 has been split into two parts (1A and 1B), as follows:  Wounded of the Naval Brigade treated on board HMS Miranda, 29 April-31 Dec",
            "noHtml": "MIRANDA, Surgeon H Slade: wounded of naval brigade in New Zealand: notes on Fiji. For description purposes, ADM 101/240 has been split into two parts (1A and 1B), as follows:  Wounded of the Naval Brigade treated on board HMS Miranda, 29 April-31 Dec 1864: ADM 101/240/1A.  HMS Miranda, 1 January -31 December 1864: ADM 101/240/1B.  NOTE: The two parts are produced as a single document using this catalogue reference (ADM 101/240).",
        }
        self.record._raw["@hierarchy"] = [
            {
                "@admin": {"id": "C4"},
                "identifier": [{"reference_number": "ADM"}],
                "level": {"code": 1},
                "source": {"value": "CAT"},
                "summary": {
                    "title": "Records of the Admiralty, Naval Forces, Royal Marines, Coastguard, and related bodies"
                },
                "count": 2470001,
            },
            {
                "@admin": {"id": "C707"},
                "level": {"code": 2},
                "source": {"value": "CAT"},
                "summary": {
                    "title": "Records of Medical and Prisoner of War Departments"
                },
                "count": 8063,
            },
            {
                "@admin": {"id": "C1810"},
                "identifier": [{"reference_number": "ADM 101"}],
                "level": {"code": 3},
                "source": {"value": "CAT"},
                "summary": {
                    "title": "Admiralty and predecessors: Office of the Director General of the Medical Department..."
                },
                "count": 4954,
            },
            {
                "@admin": {"id": "C74300"},
                "level": {"code": 4},
                "source": {"value": "CAT"},
                "summary": {"title": "AUSTRALIAN STATION"},
                "count": 100,
            },
            {
                "@admin": {"id": "C4107384"},
                "identifier": [{"reference_number": "ADM 101/240"}],
                "level": {"code": 6},
                "source": {"value": "CAT"},
                "summary": {
                    "title": "MIRANDA, Surgeon H Slade: wounded of naval brigade in New Zealand: notes on Fiji...."
                },
                "count": 1,
            },
        ]

        self.assertIsInstance(self.record.hierarchy_series, Record)
        self.assertEqual(self.record.hierarchy_series.id, "C1810")
        self.assertEqual(self.record.hierarchy_series.level, "Series")
        self.assertEqual(self.record.hierarchy_series.level_code, 3)
        self.assertEqual(
            self.record.hierarchy_series.reference_number, "ADM 101"
        )
        self.assertEqual(
            SERIES_TRANSFORMATIONS.get(
                self.record.hierarchy_series.reference_number
            ),
            None,
        )

        self.assertEqual(
            self.record.description,
            """<p>MIRANDA, Surgeon H Slade: wounded of naval brigade in New Zealand: """
            """notes on Fiji.</p> <p>For description purposes, ADM 101/240 has been split """
            """into two parts (1A and 1B), as follows: </p> <p>Wounded of the Naval Brigade """
            """treated on board HMS Miranda, 29 April-31 Dec 1864: """
            """<a href="http://discovery.nationalarchives.gov.uk/SearchUI/details?Uri=C11529959" """
            """title="Opens in a new tab" target="_blank">ADM 101/240/1A</a>. </p> """
            """<p>HMS Miranda, 1 January -31 December 1864: """
            """<a href="http://discovery.nationalarchives.gov.uk/SearchUI/details?Uri=C11529960" """
            """title="Opens in a new tab" target="_blank">ADM 101/240/1B</a>. </p> """
            """<p>NOTE: The two parts are produced as a single document using this catalogue reference """
            """(ADM 101/240).</p>""",
        )

        # test sanitisation as does in template
        self.assertEqual(
            sanitise_record_field(self.record.description),
            """<p>MIRANDA, Surgeon H Slade: wounded of naval brigade in New Zealand: """
            """notes on Fiji.</p><p>For description purposes, ADM 101/240 has been split """
            """into two parts (1A and 1B), as follows: </p><p>Wounded of the Naval Brigade """
            """treated on board HMS Miranda, 29 April-31 Dec 1864: """
            """<a href="/catalogue/id/C11529959/">ADM 101/240/1A</a>. """
            """</p><p>HMS Miranda, 1 January -31 December 1864: """
            """<a href="/catalogue/id/C11529960/">ADM 101/240/1B</a>. </p>"""
            """<p>NOTE: The two parts are produced as a single document using this catalogue reference """
            """(ADM 101/240).</p>""",
        )
