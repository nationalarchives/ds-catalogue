import threading
from unittest.mock import Mock, patch

from app.records.mixins import RelatedRecordsMixin
from app.records.models import Record
from app.records.related import (
    get_related_records_by_series,
    get_tna_related_records_by_subjects,
)
from app.search.models import APISearchResponse
from django.test import TestCase


class RelatedRecordsBySubjectsTests(TestCase):
    """Tests for get_tna_related_records_by_subjects function"""

    def setUp(self):
        """Set up common test data"""
        self.current_record_data = {
            "id": "C123456",
            "referenceNumber": "WO 95/1234",
            "summaryTitle": "Test War Diary",
            "subjects": ["Army", "Europe and Russia", "Conflict", "Diaries"],
            "groupArray": [{"value": "tna"}],
            "level": {"code": 7},  # Item level
        }
        self.current_record = Record(self.current_record_data)

    @patch("app.records.related.search_records")
    def test_returns_related_records_when_found(self, mock_search):
        """Test that related records are returned when found"""
        # Mock API response with related records (need at least 10 to satisfy fetch_limit = 10)
        mock_api_response = Mock(spec=APISearchResponse)
        mock_api_response.records = [
            Record(
                {
                    "id": "C789012",
                    "summaryTitle": "Related War Diary 1",
                    "subjects": ["Army", "Conflict"],
                    "level": {"code": 7},
                }
            ),
            Record(
                {
                    "id": "C345678",
                    "summaryTitle": "Related War Diary 2",
                    "subjects": ["Army", "Diaries"],
                    "level": {"code": 7},
                }
            ),
            Record(
                {
                    "id": "C999999",
                    "summaryTitle": "Related War Diary 3",
                    "subjects": ["Army", "Conflict", "Diaries"],
                    "level": {"code": 7},
                }
            ),
            Record(
                {
                    "id": "C888888",
                    "summaryTitle": "Related War Diary 4",
                    "subjects": ["Army"],
                    "level": {"code": 6},
                }
            ),
            Record(
                {
                    "id": "C777777",
                    "summaryTitle": "Related War Diary 5",
                    "subjects": ["Diaries"],
                    "level": {"code": 8},
                }
            ),
            Record(
                {
                    "id": "C666666",
                    "summaryTitle": "Related War Diary 6",
                    "subjects": ["Conflict"],
                    "level": {"code": 7},
                }
            ),
            Record(
                {
                    "id": "C555555",
                    "summaryTitle": "Related War Diary 7",
                    "subjects": ["Army", "Conflict"],
                    "level": {"code": 6},
                }
            ),
            Record(
                {
                    "id": "C444444",
                    "summaryTitle": "Related War Diary 8",
                    "subjects": ["Army", "Diaries"],
                    "level": {"code": 8},
                }
            ),
            Record(
                {
                    "id": "C333333",
                    "summaryTitle": "Related War Diary 9",
                    "subjects": ["Conflict"],
                    "level": {"code": 7},
                }
            ),
            Record(
                {
                    "id": "C222222",
                    "summaryTitle": "Related War Diary 10",
                    "subjects": ["Army"],
                    "level": {"code": 7},
                }
            ),
        ]

        # Mock will be called twice: once for all subjects, once for individual subjects
        mock_search.return_value = mock_api_response

        # Call the function with limit 3
        result = get_tna_related_records_by_subjects(
            self.current_record, limit=3
        )

        # Should return 3 random records from the 10 available (excluding current)
        self.assertEqual(len(result), 3)
        # Verify none of them are the current record
        for record in result:
            self.assertNotEqual(record.id, self.current_record.id)

    @patch("app.records.related.search_records")
    def test_returns_empty_list_when_no_subjects(self, mock_search):
        """Test that empty list is returned when record has no subjects"""
        record_without_subjects = Record(
            {
                "id": "C123456",
                "summaryTitle": "Record without subjects",
                "groupArray": [{"value": "tna"}],
                "level": {"code": 7},
            }
        )

        result = get_tna_related_records_by_subjects(
            record_without_subjects, limit=3
        )

        self.assertEqual(result, [])
        mock_search.assert_not_called()

    @patch("app.records.related.search_records")
    def test_returns_empty_list_for_non_tna_records(self, mock_search):
        """Test that non-TNA records return empty list"""
        non_tna_record = Record(
            {
                "id": "C123456",
                "summaryTitle": "Non-TNA Record",
                "subjects": ["Army"],
                "groupArray": [{"value": "nonTna"}],
                "level": {"code": 7},
            }
        )

        result = get_tna_related_records_by_subjects(non_tna_record, limit=3)

        self.assertEqual(result, [])
        mock_search.assert_not_called()

    @patch("app.records.related.search_records")
    def test_excludes_current_record_from_results(self, mock_search):
        """Test that the current record is excluded from results"""
        mock_api_response = Mock(spec=APISearchResponse)
        # Include the current record in the API response
        mock_api_response.records = [
            self.current_record,  # This should be excluded
            Record(
                {
                    "id": "C789012",
                    "summaryTitle": "Different Record",
                    "level": {"code": 7},
                }
            ),
        ]
        mock_search.return_value = mock_api_response

        result = get_tna_related_records_by_subjects(
            self.current_record, limit=3
        )

        # Should only contain the different record
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, "C789012")

    @patch("app.records.related.search_records")
    @patch("app.records.related.logger")
    def test_handles_search_exception_gracefully(
        self, mock_logger, mock_search
    ):
        """Test that search exceptions are caught and logged"""
        mock_search.side_effect = Exception("Search failed")

        result = get_tna_related_records_by_subjects(
            self.current_record, limit=3
        )

        # Should return empty list when search fails
        self.assertEqual(result, [])


class RelatedRecordsBySeriesTests(TestCase):
    """Tests for get_related_records_by_series function"""

    def setUp(self):
        """Set up common test data"""
        self.current_record_data = {
            "id": "C123456",
            "summaryTitle": "Test Record",
            "groupArray": [{"value": "tna"}],
            "level": {"code": 7},
            "@hierarchy": [
                {
                    "@admin": {"id": "C10958"},
                    "identifier": [{"reference_number": "MH 115"}],
                    "level": {"code": 3},
                }
            ],
        }
        self.current_record = Record(self.current_record_data)

    @patch("app.records.related.search_records")
    def test_returns_series_records_excluding_current(self, mock_search):
        """Test that series records are returned but current record is excluded"""
        mock_api_response = Mock(spec=APISearchResponse)
        mock_api_response.records = [
            Record({"id": "C123456", "level": {"code": 7}}),  # Current record
            Record({"id": "C234567", "level": {"code": 7}}),
            Record({"id": "C345678", "level": {"code": 7}}),
        ]
        mock_search.return_value = mock_api_response

        result = get_related_records_by_series(self.current_record, limit=2)

        # Should exclude current record and return only 2
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].id, "C234567")
        self.assertEqual(result[1].id, "C345678")

    def test_returns_empty_for_non_tna_records(self):
        """Test that non-TNA records return empty list"""
        non_tna_record = Record(
            {
                "id": "C123456",
                "groupArray": [{"value": "nonTna"}],
                "level": {"code": 7},
            }
        )

        result = get_related_records_by_series(non_tna_record, limit=3)

        self.assertEqual(result, [])

    def test_returns_empty_when_no_series_in_hierarchy(self):
        """Test that records without series in hierarchy return empty list"""
        record_without_series = Record(
            {
                "id": "C123456",
                "groupArray": [{"value": "tna"}],
                "level": {"code": 7},
                # No @hierarchy
            }
        )

        result = get_related_records_by_series(record_without_series, limit=3)

        self.assertEqual(result, [])

    def test_returns_empty_when_series_has_no_reference_number(self):
        """Test handling when series exists but has no reference number"""
        record_data = {
            "id": "C123456",
            "groupArray": [{"value": "tna"}],
            "level": {"code": 7},
            "@hierarchy": [
                {
                    "@admin": {"id": "C10958"},
                    "level": {"code": 3},
                    # No identifier with reference_number
                }
            ],
        }
        record = Record(record_data)

        result = get_related_records_by_series(record, limit=3)

        self.assertEqual(result, [])

    @patch("app.records.related.search_records")
    def test_respects_limit(self, mock_search):
        """Test that limit parameter is respected"""
        mock_api_response = Mock(spec=APISearchResponse)
        mock_api_response.records = [
            Record({"id": f"C{i}", "level": {"code": 6}}) for i in range(1, 6)
        ]
        mock_search.return_value = mock_api_response

        result = get_related_records_by_series(self.current_record, limit=2)

        self.assertEqual(len(result), 2)

    @patch("app.records.related.search_records")
    @patch("app.records.related.logger")
    def test_handles_api_exception_gracefully(self, mock_logger, mock_search):
        """Test that API exceptions return empty list and log at debug level"""
        mock_search.side_effect = Exception("API Error")

        result = get_related_records_by_series(self.current_record, limit=3)

        self.assertEqual(result, [])


class RelatedRecordsMixinTests(TestCase):
    """Unit tests for RelatedRecordsMixin - tests backfill logic directly"""

    @patch("app.records.related.search_records")
    def test_get_related_records_backfills_with_series_when_subjects_insufficient(
        self, mock_search
    ):
        """Test that series records are used to backfill when subjects return < 3"""

        # Create test record with series
        current_record = Record(
            {
                "id": "C123456",
                "summaryTitle": "Test Record",
                "subjects": ["Army"],
                "groupArray": [{"value": "tna"}],
                "level": {"code": 6},
                "@hierarchy": [
                    {
                        "@admin": {"id": "C10958"},
                        "identifier": [{"reference_number": "MH 115"}],
                        "level": {"code": 3},
                    }
                ],
            }
        )

        # Mock responses
        subject_response_first = Mock(spec=APISearchResponse)
        subject_response_first.records = [
            Record(
                {
                    "id": "C111",
                    "level": {"code": 7},
                    "groupArray": [{"value": "tna"}],
                }
            ),
        ]

        subject_response_second = Mock(spec=APISearchResponse)
        subject_response_second.records = [
            Record(
                {
                    "id": "C111",
                    "level": {"code": 7},
                    "groupArray": [{"value": "tna"}],
                }
            ),
        ]

        series_response = Mock(spec=APISearchResponse)
        series_response.records = [
            Record(
                {
                    "id": "C123456",  # Current record - will be filtered
                    "level": {"code": 6},
                    "groupArray": [{"value": "tna"}],
                }
            ),
            Record(
                {
                    "id": "C222",
                    "level": {"code": 6},
                    "groupArray": [{"value": "tna"}],
                }
            ),
            Record(
                {
                    "id": "C333",
                    "level": {"code": 6},
                    "groupArray": [{"value": "tna"}],
                }
            ),
        ]

        mock_search.side_effect = [
            subject_response_first,
            subject_response_second,
            series_response,
        ]

        # Test the mixin method directly (no HTTP request, no threading)
        mixin = RelatedRecordsMixin()
        mixin.related_records_limit = 3

        related = mixin.get_related_records(current_record)

        # Verify backfill behavior: 1 from subjects + 2 from series
        self.assertEqual(len(related), 3)
        self.assertEqual(related[0].id, "C111")  # From subjects
        self.assertEqual(related[1].id, "C222")  # From series (backfilled)
        self.assertEqual(related[2].id, "C333")  # From series (backfilled)


class RelatedRecordsIntegrationTests(TestCase):
    """Integration tests for related records in views"""

    @patch("app.records.api.rosetta_request_handler")
    @patch("app.records.views.RecordDetailView.fetch_enrichment_data_parallel")
    def test_related_records_appear_on_detail_page(
        self, mock_fetch_parallel, mock_rosetta
    ):
        """Test that related records appear on the record detail page"""

        # Mock main record response
        mock_rosetta.return_value = {
            "data": [
                {
                    "@template": {
                        "details": {
                            "id": "C123456",
                            "summaryTitle": "Test Record",
                            "subjects": ["Army", "Conflict"],
                            "groupArray": [{"value": "tna"}],
                            "level": {"code": 7},
                            "heldByCount": 100,
                        }
                    }
                }
            ]
        }

        # Mock the parallel fetch to return related records
        def mock_fetch(record):
            return {
                "subjects_enrichment": {},
                "related_records": [
                    Record(
                        {
                            "id": "C789012",
                            "summaryTitle": "Related Record 1",
                            "level": {"code": 7},
                        }
                    ),
                    Record(
                        {
                            "id": "C345678",
                            "summaryTitle": "Related Record 2",
                            "level": {"code": 7},
                        }
                    ),
                ],
                "delivery_options": {},
                "distressing_content": False,
            }

        mock_fetch_parallel.side_effect = mock_fetch

        response = self.client.get("/catalogue/id/C123456/")

        self.assertEqual(response.status_code, 200)

        # Check context has related_records
        self.assertIn("related_records", response.context_data)
        related = response.context_data["related_records"]
        self.assertEqual(len(related), 2)
        self.assertEqual(related[0].id, "C789012")
        self.assertEqual(related[1].id, "C345678")

    @patch("app.records.api.rosetta_request_handler")
    def test_no_related_records_for_non_tna(self, mock_rosetta):
        """Test that non-TNA records don't get related records"""
        mock_rosetta.return_value = {
            "data": [
                {
                    "@template": {
                        "details": {
                            "id": "C123456",
                            "summaryTitle": "Non-TNA Record",
                            "groupArray": [{"value": "nonTna"}],
                            "heldByCount": 100,
                        }
                    }
                }
            ]
        }

        response = self.client.get("/catalogue/id/C123456/")

        self.assertEqual(response.status_code, 200)
        related = response.context_data["related_records"]
        self.assertEqual(len(related), 0)
