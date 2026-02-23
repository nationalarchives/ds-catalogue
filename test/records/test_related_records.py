from unittest.mock import Mock, patch

from app.records.models import Record
from app.records.related import (
    get_related_records_by_series,
    get_tna_related_records_by_subjects,
)
from django.test import TestCase


class TestRelatedRecordsBySubjects(TestCase):
    """Tests for get_tna_related_records_by_subjects function"""

    @patch("app.records.related.random.sample")
    @patch("app.records.related._search_by_subject_matches")
    def test_returns_random_selection_when_more_than_limit(
        self, mock_search, mock_sample
    ):
        """Test that function returns random selection when candidates exceed limit"""
        mock_record = Mock(spec=Record)
        mock_record.is_tna = True
        mock_record.subjects = ["Army", "Navy"]

        # Mock _search_by_subject_matches to return 10 records
        mock_records = [Mock(spec=Record, id=f"C{i}") for i in range(1, 11)]
        mock_search.return_value = mock_records

        # Mock random.sample to return first 3
        mock_sample.return_value = mock_records[:3]

        result = get_tna_related_records_by_subjects(mock_record, limit=3)

        # Should call random.sample with the 10 records and limit of 3
        mock_sample.assert_called_once_with(mock_records, 3)
        self.assertEqual(len(result), 3)

    @patch("app.records.related._search_by_subject_matches")
    def test_returns_all_when_less_than_limit(self, mock_search):
        """Test that function returns all records when fewer than limit"""
        mock_record = Mock(spec=Record)
        mock_record.is_tna = True
        mock_record.subjects = ["Army"]

        # Mock _search_by_subject_matches to return only 2 records
        mock_records = [Mock(spec=Record, id=f"C{i}") for i in range(1, 3)]
        mock_search.return_value = mock_records

        result = get_tna_related_records_by_subjects(mock_record, limit=3)

        # Should return all 2 records without sampling
        self.assertEqual(len(result), 2)
        self.assertEqual(result, mock_records)

    def test_returns_empty_for_non_tna_record(self):
        """Test that non-TNA records return empty list"""
        mock_record = Mock(spec=Record)
        mock_record.is_tna = False
        mock_record.subjects = ["Army"]

        result = get_tna_related_records_by_subjects(mock_record, limit=3)

        self.assertEqual(result, [])

    def test_returns_empty_when_no_subjects(self):
        """Test that records without subjects return empty list"""
        mock_record = Mock(spec=Record)
        mock_record.is_tna = True
        mock_record.subjects = []

        result = get_tna_related_records_by_subjects(mock_record, limit=3)

        self.assertEqual(result, [])


class TestRelatedRecordsBySeries(TestCase):
    """Tests for get_related_records_by_series function"""

    @patch("app.records.related.search_records")
    def test_returns_records_from_same_series(self, mock_search):
        """Test that function returns records from the same series"""
        # Create mock series
        mock_series = Mock()
        mock_series.reference_number = "WO 95"
        mock_series.id = "C12345"

        # Create mock record with series
        mock_record = Mock(spec=Record)
        mock_record.is_tna = True
        mock_record.hierarchy_series = mock_series
        mock_record.id = "C111"

        # Mock search results
        mock_result = Mock()
        mock_result.records = [
            Mock(spec=Record, id="C111"),  # Current record (should be filtered)
            Mock(spec=Record, id="C222"),
            Mock(spec=Record, id="C333"),
            Mock(spec=Record, id="C444"),
        ]
        mock_search.return_value = mock_result

        result = get_related_records_by_series(mock_record, limit=3)

        # Should return 3 records, excluding the current one
        self.assertEqual(len(result), 3)
        self.assertNotIn(mock_record.id, [r.id for r in result])

    @patch("app.records.related.search_records")
    def test_stops_at_limit(self, mock_search):
        """Test that function stops when limit is reached"""
        mock_series = Mock()
        mock_series.reference_number = "WO 95"

        mock_record = Mock(spec=Record)
        mock_record.is_tna = True
        mock_record.hierarchy_series = mock_series
        mock_record.id = "C111"

        # Mock many results
        mock_result = Mock()
        mock_result.records = [
            Mock(spec=Record, id=f"C{i}") for i in range(200, 210)
        ]
        mock_search.return_value = mock_result

        result = get_related_records_by_series(mock_record, limit=3)

        # Should return exactly 3 records
        self.assertEqual(len(result), 3)

    def test_returns_empty_for_non_tna_record(self):
        """Test that non-TNA records return empty list"""
        mock_record = Mock(spec=Record)
        mock_record.is_tna = False
        mock_record.hierarchy_series = Mock()

        result = get_related_records_by_series(mock_record, limit=3)

        self.assertEqual(result, [])

    def test_returns_empty_when_no_series(self):
        """Test that records without series return empty list"""
        mock_record = Mock(spec=Record)
        mock_record.is_tna = True
        mock_record.hierarchy_series = None

        result = get_related_records_by_series(mock_record, limit=3)

        self.assertEqual(result, [])

    @patch("app.records.related.search_records")
    def test_handles_api_error_gracefully(self, mock_search):
        """Test that API errors are handled and return empty list"""
        mock_series = Mock()
        mock_series.reference_number = "WO 95"

        mock_record = Mock(spec=Record)
        mock_record.is_tna = True
        mock_record.hierarchy_series = mock_series

        # Mock search to raise exception
        mock_search.side_effect = Exception("API Error")

        result = get_related_records_by_series(mock_record, limit=3)

        # Should return empty list on error
        self.assertEqual(result, [])
