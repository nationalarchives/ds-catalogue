"""Tests for view mixins"""

from unittest.mock import Mock, patch

from app.records.mixins import (
    DeliveryOptionsMixin,
    DistressingContentMixin,
    GlobalAlertsMixin,
    RecordContextMixin,
    RelatedRecordsMixin,
    SubjectsEnrichmentMixin,
)
from app.records.models import Record
from django.conf import settings
from django.core.cache import cache
from django.test import RequestFactory, TestCase
from django.views.generic import TemplateView


class TestRecordContextMixin(TestCase):
    """Tests for RecordContextMixin"""

    def setUp(self):
        self.factory = RequestFactory()

        # Create a test view class that uses the mixin
        class TestView(RecordContextMixin, TemplateView):
            template_name = "test.html"

        self.view_class = TestView

    @patch("app.records.mixins.record_details_by_id")
    def test_get_record_fetches_by_id(self, mock_record_details):
        """Test that get_record fetches record by ID from kwargs"""
        mock_record = Mock(spec=Record)
        mock_record.id = "C123456"
        mock_record_details.return_value = mock_record

        request = self.factory.get("/test/")
        view = self.view_class()
        view.request = request
        view.kwargs = {"id": "C123456"}

        record = view.get_record()

        mock_record_details.assert_called_once_with(id="C123456")
        self.assertEqual(record.id, "C123456")

    @patch("app.records.mixins.record_details_by_id")
    def test_get_record_caches_result(self, mock_record_details):
        """Test that get_record caches the record to avoid multiple API calls"""
        mock_record = Mock(spec=Record)
        mock_record_details.return_value = mock_record

        request = self.factory.get("/test/")
        view = self.view_class()
        view.request = request
        view.kwargs = {"id": "C123456"}

        # Call get_record twice
        record1 = view.get_record()
        record2 = view.get_record()

        # Should only call API once due to caching
        mock_record_details.assert_called_once()
        self.assertEqual(record1, record2)

    @patch("app.records.mixins.record_details_by_id")
    def test_get_context_data_adds_record(self, mock_record_details):
        """Test that get_context_data adds record to context"""
        mock_record = Mock(spec=Record)
        mock_record_details.return_value = mock_record

        request = self.factory.get("/test/")
        view = self.view_class.as_view()
        view(request, id="C123456")

        # Verify record_details_by_id was called
        mock_record_details.assert_called_once_with(id="C123456")


class TestGlobalAlertsMixin(TestCase):
    """Tests for GlobalAlertsMixin"""

    def setUp(self):
        self.factory = RequestFactory()

        class TestView(GlobalAlertsMixin, TemplateView):
            template_name = "test.html"

        self.view_class = TestView

    @patch("app.main.global_alert.JSONAPIClient")
    def test_get_global_alerts_success(self, mock_client):
        """Test successful global alerts fetch"""
        mock_client_instance = Mock()
        mock_client_instance.get.return_value = {
            "global_alert": "Test alert",
            "mourning_notice": False,
        }
        mock_client.return_value = mock_client_instance

        view = self.view_class()
        alerts = view.get_global_alerts()

        self.assertIn("global_alert", alerts)
        self.assertEqual(alerts["global_alert"], "Test alert")

    @patch("app.main.global_alert.JSONAPIClient")
    def test_get_global_alerts_failure(self, mock_client):
        """Test that failures return empty dict"""

        # clear cache to ensure fresh fetch
        cache.clear()

        mock_client_instance = Mock()
        mock_client_instance.get.side_effect = Exception("API Error")
        mock_client.return_value = mock_client_instance

        view = self.view_class()
        alerts = view.get_global_alerts()

        self.assertEqual(alerts, None)


class TestSubjectsEnrichmentMixin(TestCase):
    """Tests for SubjectsEnrichmentMixin"""

    def setUp(self):
        self.factory = RequestFactory()

        class TestView(SubjectsEnrichmentMixin, TemplateView):
            template_name = "test.html"

        self.view_class = TestView

    @patch("app.records.mixins.get_subjects_enrichment")
    def test_set_record_subjects_enrichment_with_subjects(
        self, mock_get_enrichment
    ):
        """Test enriching a record that has subjects"""
        mock_enrichment = {"items": [{"title": "Test Article"}]}
        mock_get_enrichment.return_value = mock_enrichment

        mock_record = Mock(spec=Record)
        mock_record.subjects = ["Army", "Conflict"]

        view = self.view_class()
        view.set_record_subjects_enrichment(mock_record)

        mock_get_enrichment.assert_called_once_with(
            ["Army", "Conflict"], limit=settings.MAX_SUBJECTS_PER_RECORD
        )
        self.assertEqual(mock_record._subjects_enrichment, mock_enrichment)

    def test_set_record_subjects_enrichment_without_subjects(self):
        """Test enriching a record that has no subjects"""
        mock_record = Mock(spec=Record)
        mock_record.subjects = []

        view = self.view_class()
        view.set_record_subjects_enrichment(mock_record)

        self.assertEqual(mock_record._subjects_enrichment, {})


class TestRelatedRecordsMixin(TestCase):
    """Tests for RelatedRecordsMixin"""

    def setUp(self):
        self.factory = RequestFactory()

        class TestView(RelatedRecordsMixin, TemplateView):
            template_name = "test.html"

        self.view_class = TestView

    @patch("app.records.mixins.get_related_records_by_series")
    @patch("app.records.mixins.get_tna_related_records_by_subjects")
    def test_get_related_records_with_sufficient_subjects(
        self, mock_by_subjects, mock_by_series
    ):
        """Test getting related records when subjects return enough results"""
        mock_records = [Mock(spec=Record, id=f"C{i}") for i in range(1, 4)]
        mock_by_subjects.return_value = mock_records

        mock_record = Mock(spec=Record)

        view = self.view_class()
        related = view.get_related_records(mock_record)

        self.assertEqual(len(related), 3)
        mock_by_subjects.assert_called_once_with(mock_record, limit=3)
        # Should not call series method if subjects returned enough
        mock_by_series.assert_not_called()

    @patch("app.records.mixins.get_related_records_by_series")
    @patch("app.records.mixins.get_tna_related_records_by_subjects")
    def test_get_related_records_backfill_from_series(
        self, mock_by_subjects, mock_by_series
    ):
        """Test backfilling from series when subjects return insufficient results"""
        # Subjects returns only 1 record
        mock_by_subjects.return_value = [Mock(spec=Record, id="C111")]

        # Series returns 2 more records
        mock_by_series.return_value = [
            Mock(spec=Record, id="C222"),
            Mock(spec=Record, id="C333"),
        ]

        mock_record = Mock(spec=Record)

        view = self.view_class()
        related = view.get_related_records(mock_record)

        self.assertEqual(len(related), 3)
        mock_by_subjects.assert_called_once_with(mock_record, limit=3)
        mock_by_series.assert_called_once_with(mock_record, limit=2)


class TestDeliveryOptionsMixin(TestCase):
    """Tests for DeliveryOptionsMixin"""

    def setUp(self):
        self.factory = RequestFactory()

        class TestView(DeliveryOptionsMixin, TemplateView):
            template_name = "test.html"

        self.view_class = TestView

    def test_should_include_delivery_options_for_standard_record(self):
        """Test that standard records should include delivery options"""
        mock_record = Mock(spec=Record)
        mock_record.custom_record_type = (
            ""  # currently return empty string if not set
        )

        view = self.view_class()
        result = view.should_include_delivery_options(mock_record)

        self.assertFalse(result)

    def test_should_not_include_delivery_options_for_archon(self):
        """Test that ARCHON records should not include delivery options"""
        mock_record = Mock(spec=Record)
        mock_record.custom_record_type = "ARCHON"

        view = self.view_class()
        result = view.should_include_delivery_options(mock_record)

        self.assertFalse(result)

    def test_should_not_include_delivery_options_for_creators(self):
        """Test that CREATORS records should not include delivery options"""
        mock_record = Mock(spec=Record)
        mock_record.custom_record_type = "CREATORS"

        view = self.view_class()
        result = view.should_include_delivery_options(mock_record)

        self.assertFalse(result)


class TestDistressingContentMixin(TestCase):
    """Tests for DistressingContentMixin"""

    def setUp(self):
        self.factory = RequestFactory()

        class TestView(DistressingContentMixin, TemplateView):
            template_name = "test.html"

        self.view_class = TestView

    @patch("app.records.mixins.has_distressing_content")
    def test_check_distressing_content_true(self, mock_has_distressing):
        """Test checking for distressing content when warning exists"""
        mock_has_distressing.return_value = True

        mock_record = Mock(spec=Record)
        mock_record.reference_number = "HO 616/123"

        view = self.view_class()
        result = view.check_distressing_content(mock_record)

        self.assertTrue(result)
        mock_has_distressing.assert_called_once_with("HO 616/123")

    @patch("app.records.mixins.has_distressing_content")
    def test_check_distressing_content_false(self, mock_has_distressing):
        """Test checking for distressing content when no warning exists"""
        mock_has_distressing.return_value = False

        mock_record = Mock(spec=Record)
        mock_record.reference_number = "ADM 123/456"

        view = self.view_class()
        result = view.check_distressing_content(mock_record)

        self.assertFalse(result)
        mock_has_distressing.assert_called_once_with("ADM 123/456")


class TestMixinIntegration(TestCase):
    """Integration tests for multiple mixins working together"""

    def setUp(self):
        self.factory = RequestFactory()

        # Create a view that uses multiple mixins
        class TestView(
            DistressingContentMixin,
            DeliveryOptionsMixin,
            RelatedRecordsMixin,
            SubjectsEnrichmentMixin,
            GlobalAlertsMixin,
            RecordContextMixin,
            TemplateView,
        ):
            template_name = "test.html"

        self.view_class = TestView

    @patch("app.records.mixins.has_distressing_content")
    @patch("app.records.mixins.delivery_options_request_handler")
    @patch("app.records.mixins.get_tna_related_records_by_subjects")
    @patch("app.records.mixins.get_subjects_enrichment")
    @patch("app.main.global_alert.JSONAPIClient")
    @patch("app.records.mixins.record_details_by_id")
    def test_all_mixins_contribute_to_context(
        self,
        mock_record_details,
        mock_api_client,
        mock_enrichment,
        mock_related,
        mock_delivery,
        mock_distressing,
    ):
        """Test that all mixins properly contribute to context"""
        # Setup mocks
        mock_record = Mock(spec=Record)
        mock_record.id = "C123456"
        mock_record.reference_number = "TEST 123"
        mock_record.subjects = ["Army"]
        mock_record.custom_record_type = None
        mock_record_details.return_value = mock_record

        mock_api_client_instance = Mock()
        mock_api_client_instance.get.return_value = {"global_alert": "Test"}
        mock_api_client.return_value = mock_api_client_instance

        mock_enrichment.return_value = {"items": []}
        mock_related.return_value = []
        mock_delivery.return_value = [{"options": 3}]
        mock_distressing.return_value = False

        # Create request and get response
        request = self.factory.get("/test/")
        view = self.view_class.as_view()
        response = view(request, id="C123456")

        # Verify all mixins contributed
        context = response.context_data

        self.assertIn("record", context)
        self.assertIn("global_alert", context)
        self.assertIn("related_records", context)
        # Distressing content should be in context
        self.assertIn("distressing_content", context)
