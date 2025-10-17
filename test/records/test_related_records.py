from unittest.mock import Mock, patch

from app.records.models import Record
from app.records.related import (
    get_related_records_by_series,
    get_related_records_by_subjects,
)
from app.search.models import APISearchResponse
from django.test import TestCase


class RelatedRecordsBySubjectsTests(TestCase):
    """Tests for get_related_records_by_subjects function"""

    def setUp(self):
        """Set up common test data"""
        self.current_record_data = {
            "iaid": "C123456",
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
        # Mock API response with related records
        mock_api_response = Mock(spec=APISearchResponse)
        mock_api_response.records = [
            Record(
                {
                    "iaid": "C789012",
                    "summaryTitle": "Related War Diary 1",
                    "subjects": ["Army", "Conflict"],
                    "level": {"code": 7},
                }
            ),
            Record(
                {
                    "iaid": "C345678",
                    "summaryTitle": "Related War Diary 2",
                    "subjects": ["Army", "Diaries"],
                    "level": {"code": 7},
                }
            ),
        ]
        mock_search.return_value = mock_api_response

        result = get_related_records_by_subjects(self.current_record, limit=3)

        # Should return 2 related records
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], Record)
        self.assertEqual(result[0].iaid, "C789012")
        self.assertEqual(result[1].iaid, "C345678")

        # With new implementation, multiple searches are made (one per subject/level combo)
        # For Item level (7), similar levels are [6, 7] (Piece and Item)
        # 4 subjects × 2 levels = 8 calls
        self.assertEqual(mock_search.call_count, 8)

        # Verify that calls include correct filters
        all_calls = mock_search.call_args_list
        for call in all_calls:
            call_params = call[1]["params"]["filter"]
            self.assertIn("group:tna", call_params)
            # Should have exactly one subject and one level per call
            subject_filters = [
                f for f in call_params if f.startswith("subject:")
            ]
            level_filters = [f for f in call_params if f.startswith("level:")]
            self.assertEqual(len(subject_filters), 1)
            self.assertEqual(len(level_filters), 1)

    @patch("app.records.related.search_records")
    def test_filters_out_current_record(self, mock_search):
        """Test that the current record is filtered out of results"""
        mock_api_response = Mock(spec=APISearchResponse)
        mock_api_response.records = [
            Record(
                {
                    "iaid": "C123456",  # Same as current record
                    "summaryTitle": "Current Record",
                    "level": {"code": 7},
                }
            ),
            Record(
                {
                    "iaid": "C789012",
                    "summaryTitle": "Different Record",
                    "level": {"code": 7},
                }
            ),
        ]
        mock_search.return_value = mock_api_response

        result = get_related_records_by_subjects(self.current_record, limit=3)

        # Should only return the different record
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].iaid, "C789012")

    @patch("app.records.related.search_records")
    def test_respects_limit(self, mock_search):
        """Test that the limit parameter is respected"""
        mock_api_response = Mock(spec=APISearchResponse)
        # Return 5 records
        mock_api_response.records = [
            Record({"iaid": f"C{i}", "level": {"code": 7}}) for i in range(1, 6)
        ]
        mock_search.return_value = mock_api_response

        result = get_related_records_by_subjects(self.current_record, limit=2)

        # Should only return 2 records
        self.assertEqual(len(result), 2)

    def test_returns_empty_list_for_non_tna_record(self):
        """Test that non-TNA records return empty list"""
        non_tna_record = Record(
            {
                "iaid": "C123456",
                "subjects": ["Test Subject"],
                "groupArray": [{"value": "nonTna"}],
            }
        )

        result = get_related_records_by_subjects(non_tna_record, limit=3)

        self.assertEqual(result, [])

    def test_returns_empty_list_when_no_subjects(self):
        """Test that records without subjects return empty list"""
        record_without_subjects = Record(
            {
                "iaid": "C123456",
                "subjects": [],
                "groupArray": [{"value": "tna"}],
                "level": {"code": 7},
            }
        )

        result = get_related_records_by_subjects(
            record_without_subjects, limit=3
        )

        self.assertEqual(result, [])

    def test_returns_empty_list_when_no_level_code(self):
        """Test that records without level_code return empty list"""
        record_without_level = Record(
            {
                "iaid": "C123456",
                "subjects": ["Test Subject"],
                "groupArray": [{"value": "tna"}],
                # No level.code
            }
        )

        result = get_related_records_by_subjects(record_without_level, limit=3)

        self.assertEqual(result, [])

    @patch("app.records.related.search_records")
    @patch("app.records.related.logger")
    def test_handles_api_exception_gracefully(self, mock_logger, mock_search):
        """Test that API exceptions are handled and logged at debug level"""
        mock_search.side_effect = Exception("API Error")

        result = get_related_records_by_subjects(self.current_record, limit=3)

        self.assertEqual(result, [])
        # New implementation logs at debug level, not warning
        self.assertTrue(mock_logger.debug.called)

    @patch("app.records.related.search_records")
    def test_uses_correct_subject_filters(self, mock_search):
        """Test that subject filters are correctly formatted"""
        mock_api_response = Mock(spec=APISearchResponse)
        mock_api_response.records = []
        mock_search.return_value = mock_api_response

        get_related_records_by_subjects(self.current_record, limit=3)

        # Check that all subjects appear in at least one call
        all_subjects = {"Army", "Europe and Russia", "Conflict", "Diaries"}
        subjects_found = set()

        for call in mock_search.call_args_list:
            call_params = call[1]["params"]["filter"]
            for param in call_params:
                if param.startswith("subject:"):
                    subject = param.replace("subject:", "")
                    subjects_found.add(subject)

        self.assertEqual(subjects_found, all_subjects)


class RelatedRecordsBySeriesTests(TestCase):
    """Tests for get_related_records_by_series function"""

    def setUp(self):
        """Set up common test data"""
        # Create a mock series record
        self.series_record_data = {
            "iaid": "C10958",
            "referenceNumber": "MH 115",
            "summaryTitle": "Ministry of Health Series",
            "level": {"code": 3},
        }

        self.current_record_data = {
            "iaid": "C1717132",
            "referenceNumber": "MH 115/646",
            "summaryTitle": "Wantage Hospital",
            "groupArray": [{"value": "tna"}],
            "level": {"code": 6},  # Piece level
            "@hierarchy": [
                {
                    "@admin": {"id": "C10958"},
                    "identifier": [{"reference_number": "MH 115"}],
                    "level": {"code": 3},
                    "summary": {"title": "Ministry of Health Series"},
                }
            ],
        }
        self.current_record = Record(self.current_record_data)

    @patch("app.records.related.search_records")
    def test_returns_related_records_from_same_series(self, mock_search):
        """Test that related records from same series are returned"""
        mock_api_response = Mock(spec=APISearchResponse)
        mock_api_response.records = [
            Record(
                {
                    "iaid": "C1717133",
                    "referenceNumber": "MH 115/647",
                    "summaryTitle": "Another Hospital",
                    "level": {"code": 6},
                }
            ),
            Record(
                {
                    "iaid": "C1717134",
                    "referenceNumber": "MH 115/648",
                    "summaryTitle": "Yet Another Hospital",
                    "level": {"code": 6},
                }
            ),
        ]
        mock_search.return_value = mock_api_response

        result = get_related_records_by_series(self.current_record, limit=3)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].iaid, "C1717133")
        self.assertEqual(result[1].iaid, "C1717134")

        # With new implementation, searches are made for each similar level
        # For Piece level (6), similar levels are [5, 6, 7] (Sub-sub-series, Piece, Item)
        self.assertEqual(mock_search.call_count, 3)

        # Verify all calls use the series reference
        for call in mock_search.call_args_list:
            self.assertEqual(call[1]["query"], "MH 115")

    @patch("app.records.related.search_records")
    def test_filters_out_current_record(self, mock_search):
        """Test that current record is excluded from results"""
        mock_api_response = Mock(spec=APISearchResponse)
        mock_api_response.records = [
            Record(
                {
                    "iaid": "C1717132",  # Current record
                    "referenceNumber": "MH 115/646",
                    "level": {"code": 6},
                }
            ),
            Record(
                {
                    "iaid": "C1717133",
                    "referenceNumber": "MH 115/647",
                    "level": {"code": 6},
                }
            ),
        ]
        mock_search.return_value = mock_api_response

        result = get_related_records_by_series(self.current_record, limit=3)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].iaid, "C1717133")

    def test_returns_empty_list_when_no_series(self):
        """Test that records without hierarchy_series return empty list"""
        record_without_series = Record(
            {
                "iaid": "C123456",
                "groupArray": [{"value": "tna"}],
                "level": {"code": 7},
                # No @hierarchy
            }
        )

        result = get_related_records_by_series(record_without_series, limit=3)

        self.assertEqual(result, [])

    def test_returns_empty_list_when_series_has_no_reference(self):
        """Test handling when series exists but has no reference number"""
        record_data = {
            "iaid": "C123456",
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
            Record({"iaid": f"C{i}", "level": {"code": 6}}) for i in range(1, 6)
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
        # New implementation logs at debug level
        self.assertTrue(mock_logger.debug.called)


class RelatedRecordsIntegrationTests(TestCase):
    """Integration tests for related records in views"""

    @patch("app.records.api.rosetta_request_handler")
    @patch("app.records.related.search_records")
    def test_record_detail_view_includes_related_records_by_subjects(
        self, mock_search, mock_rosetta
    ):
        """Test that record detail view includes related records"""
        # Mock main record response
        mock_rosetta.return_value = {
            "data": [
                {
                    "@template": {
                        "details": {
                            "iaid": "C123456",
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

        # Mock related records response
        mock_api_response = Mock(spec=APISearchResponse)
        mock_api_response.records = [
            Record(
                {
                    "iaid": "C789012",
                    "summaryTitle": "Related Record 1",
                    "level": {"code": 7},
                }
            ),
            Record(
                {
                    "iaid": "C345678",
                    "summaryTitle": "Related Record 2",
                    "level": {"code": 7},
                }
            ),
        ]
        mock_search.return_value = mock_api_response

        response = self.client.get("/catalogue/id/C123456/")

        self.assertEqual(response.status_code, 200)

        # Check context has related_records
        self.assertIn("related_records", response.context_data)
        related = response.context_data["related_records"]
        self.assertEqual(len(related), 2)
        self.assertEqual(related[0].iaid, "C789012")
        self.assertEqual(related[1].iaid, "C345678")

    @patch("app.records.api.rosetta_request_handler")
    @patch("app.records.related.search_records")
    def test_backfills_with_series_when_subjects_insufficient(
        self, mock_search, mock_rosetta
    ):
        """Test that series records are used to backfill when subjects return < 3"""
        # Mock main record with series
        mock_rosetta.return_value = {
            "data": [
                {
                    "@template": {
                        "details": {
                            "iaid": "C123456",
                            "summaryTitle": "Test Record",
                            "subjects": ["Army"],
                            "groupArray": [{"value": "tna"}],
                            "level": {"code": 6},
                            "heldByCount": 100,
                            "@hierarchy": [
                                {
                                    "@admin": {"id": "C10958"},
                                    "identifier": [
                                        {"reference_number": "MH 115"}
                                    ],
                                    "level": {"code": 3},
                                }
                            ],
                        }
                    }
                }
            ]
        }

        # Mock search_records to return different results for subject/series searches
        # With new implementation, there will be multiple calls
        subject_response = Mock(spec=APISearchResponse)
        subject_response.records = [
            Record({"iaid": "C111", "level": {"code": 7}}),
        ]

        series_response = Mock(spec=APISearchResponse)
        series_response.records = [
            Record({"iaid": "C222", "level": {"code": 6}}),
            Record({"iaid": "C333", "level": {"code": 6}}),
        ]

        # Set up responses for multiple calls
        # Subject searches (1 subject × 3 levels) + Series searches (3 levels)
        mock_search.side_effect = [
            subject_response,  # Subject search level 1
            subject_response,  # Subject search level 2
            subject_response,  # Subject search level 3
            series_response,  # Series search level 1
            series_response,  # Series search level 2
            series_response,  # Series search level 3
        ]

        response = self.client.get("/catalogue/id/C123456/")

        self.assertEqual(response.status_code, 200)

        # Should have 3 related records total (1 from subjects + 2 from series)
        related = response.context_data["related_records"]
        self.assertEqual(len(related), 3)
        self.assertEqual(related[0].iaid, "C111")  # From subjects
        self.assertEqual(related[1].iaid, "C222")  # From series
        self.assertEqual(related[2].iaid, "C333")  # From series

    @patch("app.records.api.rosetta_request_handler")
    def test_no_related_records_for_non_tna(self, mock_rosetta):
        """Test that non-TNA records don't get related records"""
        mock_rosetta.return_value = {
            "data": [
                {
                    "@template": {
                        "details": {
                            "iaid": "C123456",
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
