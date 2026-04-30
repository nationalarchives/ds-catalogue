from app.records.constants import TNA_ARCHON_CODE, RecordTypes
from app.records.models import Record
from django.test import SimpleTestCase


class NonTnaArchonRecordCollectionUrlTests(SimpleTestCase):
    """Tests urls presented for This Archives Collections - for the archon_catalogue_url
    and archon_discovery_url properties of non-TNA ARCHON records."""

    maxDiff = None

    def setUp(self):

        self.template_details = {"some value": "some value"}

    def test_archon_catalogue_url(
        self,
    ):
        """Tests archon_catalogue_url property for a non-TNA ARCHON record."""

        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["id"] = "A13531985"
        self.record._raw["referenceNumber"] = "188"
        self.record._raw["source"] = "ARCHON"
        self.record._raw["cleanTitle"] = "Shakespeare Birthplace Trust"
        self.record._raw["summaryTitle"] = (
            "Shakespeare Birthplace Trust is longer than clean title"
        )

        self.assertEqual(self.record.custom_record_type, RecordTypes.ARCHON)
        self.assertNotEqual(self.record.reference_number, TNA_ARCHON_CODE)
        self.assertEqual(
            self.record.clean_title_or_summary_title,
            "Shakespeare Birthplace Trust",
        )

        self.assertEqual(
            self.record.archon_catalogue_url,
            "/catalogue/search/?group=nonTna&held_by=Shakespeare+Birthplace+Trust",
        )

    def test_archon_discovery_url(
        self,
    ):
        """Tests archon_discovery_url property for a non-TNA ARCHON record."""

        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["id"] = "A13531985"
        self.record._raw["referenceNumber"] = "188"
        self.record._raw["source"] = "ARCHON"
        self.record._raw["cleanTitle"] = "Shakespeare Birthplace Trust"
        self.record._raw["summaryTitle"] = (
            "Shakespeare Birthplace Trust is longer than clean title"
        )

        self.assertEqual(self.record.custom_record_type, RecordTypes.ARCHON)
        self.assertNotEqual(self.record.reference_number, TNA_ARCHON_CODE)
        self.assertEqual(
            self.record.clean_title_or_summary_title,
            "Shakespeare Birthplace Trust",
        )

        self.assertEqual(
            self.record.archon_discovery_url,
            "https://discovery.nationalarchives.gov.uk/results/r?_q=%2A&_hb=oth&_nrar=188",
        )


class TnaArchonRecordCollectionUrlTests(SimpleTestCase):
    """Tests urls presented for This Archives Collections - for the archon_catalogue_url
    and archon_discovery_url properties of TNA ARCHON records."""

    maxDiff = None

    def setUp(self):

        self.template_details = {"some value": "some value"}

    def test_archon_catalogue_url(
        self,
    ):
        """Tests archon_catalogue_url property for a TNA ARCHON record."""

        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["id"] = "A13530124"
        self.record._raw["referenceNumber"] = "66"
        self.record._raw["source"] = "ARCHON"

        self.assertEqual(self.record.custom_record_type, RecordTypes.ARCHON)
        self.assertEqual(self.record.reference_number, TNA_ARCHON_CODE)

        self.assertEqual(
            self.record.archon_catalogue_url,
            "/catalogue/",
        )

    def test_archon_discovery_url(
        self,
    ):
        """Tests archon_discovery_url property for a TNA ARCHON record."""

        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["id"] = "A13530124"
        self.record._raw["referenceNumber"] = "66"
        self.record._raw["source"] = "ARCHON"

        self.assertEqual(self.record.custom_record_type, RecordTypes.ARCHON)
        self.assertEqual(self.record.reference_number, TNA_ARCHON_CODE)

        self.assertEqual(
            self.record.archon_discovery_url,
            "https://discovery.nationalarchives.gov.uk/results/r?_q=%2A&_hb=tna",
        )
