"""Tests for RecordEnrichmentHelper"""

from concurrent.futures import Future, ThreadPoolExecutor
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

    @override_settings(
        ENABLE_PARALLEL_API_CALLS=False,
        WAGTAIL_API_TIMEOUT=10,
        ROSETTA_ENRICHMENT_API_TIMEOUT=15,
        DELIVERY_OPTIONS_API_TIMEOUT=20,
    )
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

    @override_settings(
        ENABLE_PARALLEL_API_CALLS=True,
        WAGTAIL_API_TIMEOUT=10,
        ROSETTA_ENRICHMENT_API_TIMEOUT=15,
        DELIVERY_OPTIONS_API_TIMEOUT=20,
    )
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

    @override_settings(ROSETTA_ENRICHMENT_API_TIMEOUT=7)
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
        mock_subjects.assert_called_once_with(
            self.test_record, limit=3, timeout=7
        )
        mock_series.assert_called_once_with(
            self.test_record, limit=2, timeout=7
        )

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

    # Tests for new refactored methods

    @patch("app.records.enrichment.sentry_sdk")
    def test_submit_fetch_tasks_success(self, mock_sentry: Mock) -> None:
        """Test successful submission of all fetch tasks"""
        helper = RecordEnrichmentHelper(self.test_record)

        with patch.object(
            helper, "_should_include_delivery_options", return_value=True
        ):
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures_map = helper._submit_fetch_tasks(executor)

            # Should have 3 futures submitted
            self.assertEqual(len(futures_map), 3)
            self.assertIn("subjects", futures_map.values())
            self.assertIn("related", futures_map.values())
            self.assertIn("delivery", futures_map.values())

            # Sentry should not be called on success
            mock_sentry.capture_exception.assert_not_called()

    @patch("app.records.enrichment.logger")
    @patch("app.records.enrichment.ThreadPoolExecutor")
    def test_submit_fetch_tasks_handles_runtime_error(
        self, mock_executor_class: Mock, mock_logger: Mock
    ) -> None:
        """Test that RuntimeError during submit is handled gracefully"""
        helper = RecordEnrichmentHelper(self.test_record)

        # Create a mock executor
        mock_executor = Mock()
        mock_executor_class.return_value.__enter__.return_value = mock_executor

        # Track the fetch_subjects method by id
        subjects_method_id = id(helper._fetch_subjects)

        # Make submit raise RuntimeError for subjects only
        def submit_side_effect(fn, *args, **kwargs):
            if id(fn) == subjects_method_id:
                raise RuntimeError("Executor shutdown")
            # For other functions, return a mock future
            mock_future = Mock()
            return mock_future

        mock_executor.submit.side_effect = submit_side_effect

        futures_map = helper._submit_fetch_tasks(mock_executor)

        # Should only have related task (subjects failed)
        # Note: may have 2 if delivery is also submitted
        self.assertNotIn("subjects", futures_map.values())

        # Logger should be called for the failure
        mock_logger.error.assert_called()
        error_calls = [
            c for c in mock_logger.error.call_args_list if "subjects" in str(c)
        ]
        self.assertGreater(len(error_calls), 0)

    @patch("app.records.enrichment.sentry_sdk")
    def test_submit_fetch_tasks_skips_delivery_when_not_applicable(
        self, mock_sentry: Mock
    ) -> None:
        """Test that delivery options are not submitted when not applicable"""
        helper = RecordEnrichmentHelper(self.test_record)

        with (
            patch.object(helper, "_fetch_subjects"),
            patch.object(helper, "_fetch_related"),
            patch.object(
                helper, "_should_include_delivery_options", return_value=False
            ),
        ):

            with ThreadPoolExecutor(max_workers=3) as executor:
                futures_map = helper._submit_fetch_tasks(executor)

            # Should only have 2 futures (no delivery)
            self.assertEqual(len(futures_map), 2)
            self.assertNotIn("delivery", futures_map.values())

    @patch("app.records.enrichment.sentry_sdk")
    def test_process_future_result_success(self, mock_sentry: Mock) -> None:
        """Test successful processing of future results"""
        helper = RecordEnrichmentHelper(self.test_record)
        results = helper._empty_results()

        # Create mock future
        mock_future = Mock(spec=Future)
        mock_future.result.return_value = {"test": "data"}

        helper._process_future_result(mock_future, "subjects", 10, results)

        self.assertEqual(results["subjects_enrichment"], {"test": "data"})
        mock_sentry.capture_exception.assert_not_called()

    @patch("app.records.enrichment.sentry_sdk")
    def test_process_future_result_handles_timeout(
        self, mock_sentry: Mock
    ) -> None:
        """Test that timeout exceptions are handled and logged to Sentry"""
        from concurrent.futures import TimeoutError

        helper = RecordEnrichmentHelper(self.test_record)
        results = helper._empty_results()

        # Create mock future that times out
        mock_future = Mock(spec=Future)
        timeout_error = TimeoutError("Operation timed out")
        mock_future.result.side_effect = timeout_error

        helper._process_future_result(mock_future, "subjects", 5, results)

        # Results should remain empty
        self.assertEqual(results["subjects_enrichment"], {})

        # Sentry should be called
        mock_sentry.capture_exception.assert_called_once_with(timeout_error)
        mock_sentry.set_context.assert_called_once_with(
            "threadpool_fetch_failure",
            {
                "record_id": self.test_record.id,
                "task": "subjects",
                "timeout": 5,
            },
        )

    @patch("app.records.enrichment.sentry_sdk")
    def test_process_future_result_handles_generic_exception(
        self, mock_sentry: Mock
    ) -> None:
        """Test that generic exceptions are handled and logged to Sentry"""
        helper = RecordEnrichmentHelper(self.test_record)
        results = helper._empty_results()

        # Create mock future that raises exception
        mock_future = Mock(spec=Future)
        api_error = Exception("API Error")
        mock_future.result.side_effect = api_error

        helper._process_future_result(mock_future, "related", 10, results)

        # Results should remain empty
        self.assertEqual(results["related_records"], [])

        # Sentry should be called
        mock_sentry.capture_exception.assert_called_once_with(api_error)

    @override_settings(ENRICHMENT_TIMING_ENABLED=True)
    @patch("app.records.enrichment.logger")
    def test_log_completion_timing_enabled(self, mock_logger: Mock) -> None:
        """Test that timing is logged when flag is enabled"""
        helper = RecordEnrichmentHelper(self.test_record)
        completion_order = ["subjects", "related", "delivery"]
        completion_times = {
            "subjects": 0.342,
            "related": 0.589,
            "delivery": 0.847,
        }

        helper._log_completion_timing(completion_order, completion_times)

        mock_logger.info.assert_called_once()
        log_message = mock_logger.info.call_args[0][0]
        self.assertIn("completion order", log_message)
        self.assertIn("subjects: 0.342s", log_message)
        self.assertIn("related: 0.589s", log_message)
        self.assertIn("delivery: 0.847s", log_message)

    @override_settings(ENRICHMENT_TIMING_ENABLED=False)
    @patch("app.records.enrichment.logger")
    def test_log_completion_timing_disabled(self, mock_logger: Mock) -> None:
        """Test that timing is not logged when flag is disabled"""
        helper = RecordEnrichmentHelper(self.test_record)
        completion_order = ["subjects", "related"]
        completion_times = {"subjects": 0.5, "related": 0.7}

        helper._log_completion_timing(completion_order, completion_times)

        mock_logger.info.assert_not_called()

    @override_settings(ENRICHMENT_TIMING_ENABLED=True)
    @patch("app.records.enrichment.logger")
    def test_log_completion_timing_empty_list(self, mock_logger: Mock) -> None:
        """Test that nothing is logged when completion order is empty"""
        helper = RecordEnrichmentHelper(self.test_record)

        helper._log_completion_timing([], {})

        mock_logger.info.assert_not_called()

    @override_settings(
        ENABLE_PARALLEL_API_CALLS=True,
        ENRICHMENT_TIMING_ENABLED=True,
        WAGTAIL_API_TIMEOUT=10,
        ROSETTA_ENRICHMENT_API_TIMEOUT=15,
        DELIVERY_OPTIONS_API_TIMEOUT=20,
    )
    @patch("app.records.enrichment.has_distressing_content")
    @patch("app.records.enrichment.get_subjects_enrichment")
    @patch("app.records.enrichment.get_tna_related_records_by_subjects")
    @patch("app.records.enrichment.logger")
    def test_fetch_parallel_partial_failure(
        self,
        mock_logger: Mock,
        mock_related: Mock,
        mock_subjects: Mock,
        mock_distressing: Mock,
    ) -> None:
        """Test that parallel fetch handles partial failures gracefully"""
        # Subjects succeeds quickly
        mock_subjects.return_value = {"items": [{"title": "Test"}]}

        # Related raises an exception (will be caught in _fetch_related)
        mock_related.side_effect = Exception("API Error")

        # Distressing succeeds
        mock_distressing.return_value = True

        helper = RecordEnrichmentHelper(self.test_record, related_limit=3)
        result = helper.fetch_all()

        # Should have subjects data
        self.assertEqual(
            result["subjects_enrichment"], {"items": [{"title": "Test"}]}
        )

        # Related should be empty (failed, but caught in _fetch_related)
        self.assertEqual(result["related_records"], [])

        # Distressing should succeed
        self.assertTrue(result["distressing_content"])

        # Logger should have been called for the related records failure
        warning_calls = [
            c
            for c in mock_logger.warning.call_args_list
            if "related" in str(c).lower()
        ]
        self.assertGreater(len(warning_calls), 0)

    @patch("app.records.enrichment.sentry_sdk")
    def test_process_future_result_calls_sentry_on_timeout(
        self, mock_sentry: Mock
    ) -> None:
        """Test that Sentry is called when future.result() times out"""
        from concurrent.futures import TimeoutError

        helper = RecordEnrichmentHelper(self.test_record)
        results = helper._empty_results()

        # Create a mock future that times out
        mock_future = Mock()
        timeout_error = TimeoutError("Operation timed out")
        mock_future.result.side_effect = timeout_error

        # Call _process_future_result
        helper._process_future_result(mock_future, "subjects", 5, results)

        # Sentry should be called with the timeout error
        mock_sentry.capture_exception.assert_called_once_with(timeout_error)
        mock_sentry.set_context.assert_called_once_with(
            "threadpool_fetch_failure",
            {
                "record_id": self.test_record.id,
                "task": "subjects",
                "timeout": 5,
            },
        )

        # Results should remain empty
        self.assertEqual(results["subjects_enrichment"], {})

    @override_settings(ENABLE_PARALLEL_API_CALLS=True)
    @patch(
        "app.records.enrichment.API_TIMEOUTS",
        {"subjects": 5, "related": 10, "delivery": 15},
    )
    @patch("app.records.enrichment.has_distressing_content")
    @patch("app.records.enrichment.get_subjects_enrichment")
    @patch("app.records.enrichment.get_tna_related_records_by_subjects")
    def test_fetch_parallel_uses_individual_timeouts(
        self,
        mock_related: Mock,
        mock_subjects: Mock,
        mock_distressing: Mock,
    ) -> None:
        """Test that individual API timeouts are used correctly"""
        mock_subjects.return_value = {"items": []}
        mock_related.return_value = []
        mock_distressing.return_value = False

        helper = RecordEnrichmentHelper(self.test_record, related_limit=3)

        with patch.object(helper, "_process_future_result") as mock_process:
            helper.fetch_all()

            # Verify that _process_future_result was called with correct timeouts
            calls = mock_process.call_args_list

            # Extract timeout values from calls
            timeouts_used = set()
            for call_args in calls:
                if len(call_args[0]) >= 3:
                    timeouts_used.add(
                        call_args[0][2]
                    )  # timeout is 3rd argument

            # Should have used the custom timeouts (5, 10)
            self.assertTrue(5 in timeouts_used or 10 in timeouts_used)

    @override_settings(
        ENABLE_PARALLEL_API_CALLS=True,
        WAGTAIL_API_TIMEOUT=10,
        ROSETTA_ENRICHMENT_API_TIMEOUT=15,
        DELIVERY_OPTIONS_API_TIMEOUT=20,
    )
    @patch("app.records.enrichment.has_distressing_content")
    @patch("app.records.enrichment.get_subjects_enrichment")
    @patch("app.records.enrichment.get_tna_related_records_by_subjects")
    def test_fetch_parallel_with_timeout_parameters_passed_to_apis(
        self,
        mock_related: Mock,
        mock_subjects: Mock,
        mock_distressing: Mock,
    ) -> None:
        """Test that timeout parameters are passed through to API calls"""
        mock_subjects.return_value = {"items": []}
        mock_related.return_value = []
        mock_distressing.return_value = False

        helper = RecordEnrichmentHelper(self.test_record)
        helper.fetch_all()

        # Verify that get_subjects_enrichment was called with timeout
        mock_subjects.assert_called_once()
        call_kwargs = mock_subjects.call_args[1]
        self.assertIn("timeout", call_kwargs)
        self.assertEqual(call_kwargs["timeout"], 10)

    @override_settings(
        ENABLE_PARALLEL_API_CALLS=False,
        WAGTAIL_API_TIMEOUT=10,
        ROSETTA_ENRICHMENT_API_TIMEOUT=15,
        DELIVERY_OPTIONS_API_TIMEOUT=20,
    )
    @patch("app.records.enrichment.has_distressing_content")
    @patch("app.records.enrichment.get_subjects_enrichment")
    @patch("app.records.enrichment.get_tna_related_records_by_subjects")
    def test_fetch_sequential_passes_timeouts(
        self,
        mock_related: Mock,
        mock_subjects: Mock,
        mock_distressing: Mock,
    ) -> None:
        """Test that sequential fetch also passes timeout parameters"""
        mock_subjects.return_value = {"items": []}
        mock_related.return_value = []
        mock_distressing.return_value = False

        helper = RecordEnrichmentHelper(self.test_record)
        helper.fetch_all()

        # Verify timeout was passed to subjects API
        mock_subjects.assert_called_once()
        call_kwargs = mock_subjects.call_args[1]
        self.assertIn("timeout", call_kwargs)
        self.assertEqual(call_kwargs["timeout"], 10)
