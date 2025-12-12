"""Tests for RecordEnrichmentHelper"""

from typing import Any
from unittest.mock import Mock, patch

from app.records.enrichment import RecordEnrichmentHelper
from app.records.models import Record
from django.test import TestCase, override_settings


class TestRecordEnrichmentHelper(TestCase):
    """Tests for the RecordEnrichmentHelper class"""

    def setUp(self) -> None:
        """Set up test record"""
        self.test_record = Mock(spec=Record)
        self.test_record.id = "C123456"
        self.test_record.subjects = ["Army", "Conflict"]
        self.test_record.custom_record_type = ""
        self.test_record.is_tna = True
        self.test_record.level_code = 7
        self.test_record.reference_number = "WO 95/1234"

    @override_settings(ENABLE_PARALLEL_API_CALLS=False)
    @patch("app.records.enrichment.has_distressing_content")
    @patch("app.records.enrichment.get_related_records_by_series")
    @patch("app.records.enrichment.get_tna_related_records_by_subjects")
    @patch("app.records.enrichment.get_subjects_enrichment")
    def test_fetch_all_sequential(
        self,
        mock_subjects: Mock,
        mock_related_subjects: Mock,
        mock_related_series: Mock,
        mock_distressing: Mock,
    ) -> None:
        """Test sequential fetching when feature flag is off"""
        mock_subjects.return_value = {"items": []}
        mock_related_subjects.return_value = []
        mock_related_series.return_value = []
        mock_distressing.return_value = False

        helper = RecordEnrichmentHelper(self.test_record, related_limit=3)
        result = helper.fetch_all()

        # Verify all methods were called
        mock_subjects.assert_called_once()
        mock_related_subjects.assert_called_once()
        mock_distressing.assert_called_once()

        # Verify result structure
        self.assertIn("subjects_enrichment", result)
        self.assertIn("related_records", result)
        self.assertIn("delivery_options", result)
        self.assertIn("distressing_content", result)

    @override_settings(ENABLE_PARALLEL_API_CALLS=True)
    @patch("app.records.enrichment.has_distressing_content")
    @patch("app.records.enrichment.get_related_records_by_series")
    @patch("app.records.enrichment.get_tna_related_records_by_subjects")
    @patch("app.records.enrichment.get_subjects_enrichment")
    def test_fetch_all_parallel(
        self,
        mock_subjects: Mock,
        mock_related_subjects: Mock,
        mock_related_series: Mock,
        mock_distressing: Mock,
    ) -> None:
        """Test parallel fetching when feature flag is on"""
        mock_subjects.return_value = {"items": []}
        mock_related_subjects.return_value = []
        mock_related_series.return_value = []
        mock_distressing.return_value = False

        helper = RecordEnrichmentHelper(self.test_record, related_limit=3)
        result = helper.fetch_all()

        # Verify all methods were called
        mock_subjects.assert_called_once()
        mock_related_subjects.assert_called_once()
        mock_distressing.assert_called_once()

        # Verify result structure
        self.assertIn("subjects_enrichment", result)
        self.assertIn("related_records", result)
        self.assertIn("delivery_options", result)
        self.assertIn("distressing_content", result)

    @patch("app.records.enrichment.get_subjects_enrichment")
    def test_fetch_subjects_success(self, mock_subjects: Mock) -> None:
        """Test that subject fetching returns data correctly"""
        expected_data: dict[str, Any] = {"items": [{"title": "Test Article"}]}
        mock_subjects.return_value = expected_data

        helper = RecordEnrichmentHelper(self.test_record)
        result = helper._fetch_subjects()

        # get_subjects_enrichment handles its own errors, so we just verify success case
        self.assertEqual(result, expected_data)

    @patch("app.records.enrichment.get_tna_related_records_by_subjects")
    @patch("app.records.enrichment.get_related_records_by_series")
    def test_fetch_related_backfills_from_series(
        self, mock_series: Mock, mock_subjects: Mock
    ) -> None:
        """Test that related records backfill from series when needed"""
        # Subjects returns only 1 record
        mock_subjects.return_value = [Mock(spec=Record, id="C111")]

        # Series returns 2 more records
        mock_series.return_value = [
            Mock(spec=Record, id="C222"),
            Mock(spec=Record, id="C333"),
        ]

        helper = RecordEnrichmentHelper(self.test_record, related_limit=3)
        result = helper._fetch_related()

        self.assertEqual(len(result), 3)
        mock_subjects.assert_called_once_with(self.test_record, limit=3)
        mock_series.assert_called_once_with(self.test_record, limit=2)

    @patch("app.records.enrichment.get_tna_related_records_by_subjects")
    def test_fetch_related_handles_errors(self, mock_subjects: Mock) -> None:
        """Test that related records errors are handled gracefully"""
        mock_subjects.side_effect = Exception("API Error")

        helper = RecordEnrichmentHelper(self.test_record, related_limit=3)
        result = helper._fetch_related()

        # Should return empty list on error
        self.assertEqual(result, [])

    def test_should_include_delivery_for_archon(self) -> None:
        """Test that ARCHON records should not include delivery options"""
        self.test_record.custom_record_type = "ARCHON"

        helper = RecordEnrichmentHelper(self.test_record)
        result = helper._should_include_delivery_options()

        self.assertFalse(result)

    def test_should_include_delivery_for_creators(self) -> None:
        """Test that CREATORS records should not include delivery options"""
        self.test_record.custom_record_type = "CREATORS"

        helper = RecordEnrichmentHelper(self.test_record)
        result = helper._should_include_delivery_options()

        self.assertFalse(result)

    @patch("app.records.enrichment.delivery_options_request_handler")
    @patch("app.records.enrichment.get_availability_group")
    def test_fetch_delivery_success(
        self, mock_get_group: Mock, mock_api_handler: Mock
    ) -> None:
        """Test successful delivery options fetch"""
        from app.deliveryoptions.constants import AvailabilityCondition

        mock_api_handler.return_value = [
            {"options": AvailabilityCondition.OrderOriginal.value}
        ]

        mock_group = Mock()
        mock_group.name = "AVAILABLE_IN_PERSON"
        mock_get_group.return_value = mock_group

        helper = RecordEnrichmentHelper(self.test_record)
        result = helper._fetch_delivery_options()

        self.assertIn("delivery_option", result)
        self.assertEqual(result["delivery_option"], "OrderOriginal")
        self.assertIn("do_availability_group", result)
        self.assertIn("delivery_options_heading", result)
        self.assertIn("tna_discovery_link", result)

    @patch("app.records.enrichment.delivery_options_request_handler")
    def test_fetch_delivery_handles_errors(
        self, mock_api_handler: Mock
    ) -> None:
        """Test that delivery options errors are handled gracefully"""
        mock_api_handler.side_effect = Exception("API Error")

        helper = RecordEnrichmentHelper(self.test_record)
        result = helper._fetch_delivery_options()

        # Should return empty dict on error
        self.assertEqual(result, {})

    @patch("app.records.enrichment.has_distressing_content")
    def test_fetch_distressing_success(self, mock_distressing: Mock) -> None:
        """Test successful distressing content check"""
        mock_distressing.return_value = True

        helper = RecordEnrichmentHelper(self.test_record)
        result = helper._fetch_distressing()

        self.assertTrue(result)

    @patch("app.records.enrichment.has_distressing_content")
    def test_fetch_distressing_handles_errors(
        self, mock_distressing: Mock
    ) -> None:
        """Test that distressing content errors are handled gracefully"""
        mock_distressing.side_effect = Exception("API Error")

        helper = RecordEnrichmentHelper(self.test_record)
        result = helper._fetch_distressing()

        # Should return False on error
        self.assertFalse(result)
