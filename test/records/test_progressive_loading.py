"""Tests for progressive loading functionality."""

import json
from unittest.mock import Mock, patch

import responses
from app.records.views import (
    RecordDeliveryOptionsView,
    RecordDetailView,
    RecordRelatedRecordsView,
    RecordSubjectsEnrichmentView,
)
from django.conf import settings
from django.core.cache import cache
from django.test import RequestFactory, TestCase


class TestRecordDetailViewJsEnabled(TestCase):
    """Tests for RecordDetailView behaviour based on js_enabled cookie."""

    def setUp(self):
        self.factory = RequestFactory()
        cache.clear()

    @patch("app.records.mixins.cache")
    @patch("app.records.views.RecordEnrichmentHelper")
    @patch("app.records.mixins.record_details_by_id")
    @patch("app.main.global_alert.JSONAPIClient")
    def test_js_enabled_skips_full_enrichment(
        self,
        mock_client,
        mock_record_details,
        mock_enrichment_helper,
        mock_cache,
    ):
        """When js_enabled=true, view should skip full enrichment fetch."""
        mock_cache.get.return_value = None

        mock_record = Mock()
        mock_record.id = "C123456"
        mock_record.reference_number = "TEST 123"
        mock_record.custom_record_type = None
        mock_record.level = "Item"
        mock_record.level_code = 7
        mock_record.subjects = []
        mock_record.hierarchy_series = None
        mock_record.summary_title = "Test"
        mock_record.is_tna = True
        mock_record_details.return_value = mock_record

        mock_helper_instance = Mock()
        mock_helper_instance.fetch_distressing.return_value = False
        mock_enrichment_helper.return_value = mock_helper_instance

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = {}
        mock_client.return_value = mock_client_instance

        # Request with js_enabled cookie
        request = self.factory.get("/catalogue/id/C123456/")
        request.COOKIES["js_enabled"] = "true"

        view = RecordDetailView.as_view()
        response = view(request, id="C123456")

        # Should NOT call fetch_all (full enrichment)
        mock_helper_instance.fetch_all.assert_not_called()
        # Should only fetch distressing content
        mock_helper_instance.fetch_distressing.assert_called_once()

        # Context should have js_enabled=True
        self.assertTrue(response.context_data["js_enabled"])

    @patch("app.records.mixins.cache")
    @patch("app.records.views.RecordEnrichmentHelper")
    @patch("app.records.mixins.record_details_by_id")
    @patch("app.main.global_alert.JSONAPIClient")
    def test_js_disabled_fetches_full_enrichment(
        self,
        mock_client,
        mock_record_details,
        mock_enrichment_helper,
        mock_cache,
    ):
        """When js_enabled=false or missing, view should fetch full enrichment."""
        mock_cache.get.return_value = None

        mock_record = Mock()
        mock_record.id = "C123456"
        mock_record.reference_number = "TEST 123"
        mock_record.custom_record_type = None
        mock_record.level = "Item"
        mock_record.level_code = 7
        mock_record.subjects = []
        mock_record.hierarchy_series = None
        mock_record.summary_title = "Test"
        mock_record.is_tna = True
        mock_record_details.return_value = mock_record

        mock_helper_instance = Mock()
        mock_helper_instance.fetch_all.return_value = {
            "distressing_content": False,
            "related_records": [],
            "subjects_enrichment": {},
            "delivery_options": {},
        }
        mock_enrichment_helper.return_value = mock_helper_instance

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = {}
        mock_client.return_value = mock_client_instance

        # Request WITHOUT js_enabled cookie
        request = self.factory.get("/catalogue/id/C123456/")

        view = RecordDetailView.as_view()
        response = view(request, id="C123456")

        # Should call fetch_all for full enrichment
        mock_helper_instance.fetch_all.assert_called_once()

        # Context should have js_enabled=False
        self.assertFalse(response.context_data["js_enabled"])

    @patch("app.records.mixins.cache")
    @patch("app.records.views.RecordEnrichmentHelper")
    @patch("app.records.mixins.record_details_by_id")
    @patch("app.main.global_alert.JSONAPIClient")
    def test_js_enabled_false_fetches_full_enrichment(
        self,
        mock_client,
        mock_record_details,
        mock_enrichment_helper,
        mock_cache,
    ):
        """When js_enabled=false explicitly, view should fetch full enrichment."""
        mock_cache.get.return_value = None

        mock_record = Mock()
        mock_record.id = "C123456"
        mock_record.reference_number = "TEST 123"
        mock_record.custom_record_type = None
        mock_record.level = "Item"
        mock_record.level_code = 7
        mock_record.subjects = []
        mock_record.hierarchy_series = None
        mock_record.summary_title = "Test"
        mock_record.is_tna = True
        mock_record_details.return_value = mock_record

        mock_helper_instance = Mock()
        mock_helper_instance.fetch_all.return_value = {
            "distressing_content": False,
            "related_records": [],
            "subjects_enrichment": {},
            "delivery_options": {},
        }
        mock_enrichment_helper.return_value = mock_helper_instance

        mock_client_instance = Mock()
        mock_client_instance.get.return_value = {}
        mock_client.return_value = mock_client_instance

        # Request with js_enabled=false
        request = self.factory.get("/catalogue/id/C123456/")
        request.COOKIES["js_enabled"] = "false"

        view = RecordDetailView.as_view()
        response = view(request, id="C123456")

        # Should call fetch_all for full enrichment
        mock_helper_instance.fetch_all.assert_called_once()

        # Context should have js_enabled=False
        self.assertFalse(response.context_data["js_enabled"])


class TestRecordSubjectsEnrichmentView(TestCase):
    """Tests for the subjects enrichment API endpoint."""

    def setUp(self):
        self.factory = RequestFactory()
        cache.clear()

    @patch("app.records.mixins.cache")
    @patch("app.records.mixins.record_details_by_id")
    def test_returns_json_response(self, mock_record_details, mock_cache):
        """Endpoint should return JSON response."""
        mock_cache.get.return_value = None

        mock_record = Mock()
        mock_record.id = "C123456"
        mock_record.subjects = ["History", "War"]
        mock_record.has_subjects_enrichment = True
        mock_record_details.return_value = mock_record

        request = self.factory.get("/catalogue/id/C123456/enrichment/subjects/")
        view = RecordSubjectsEnrichmentView.as_view()

        with patch("app.records.views.render_to_string") as mock_render:
            mock_render.return_value = "<div>Related content</div>"
            response = view(request, id="C123456")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        data = json.loads(response.content)
        self.assertIn("success", data)
        self.assertIn("has_content", data)
        self.assertIn("html", data)

    @patch("app.records.mixins.cache")
    @patch("app.records.mixins.record_details_by_id")
    def test_no_content_when_no_subjects(self, mock_record_details, mock_cache):
        """Endpoint should return has_content=False when record has no subjects."""
        mock_cache.get.return_value = None

        mock_record = Mock()
        mock_record.id = "C123456"
        mock_record.subjects = []
        mock_record.has_subjects_enrichment = False
        mock_record_details.return_value = mock_record

        request = self.factory.get("/catalogue/id/C123456/enrichment/subjects/")
        view = RecordSubjectsEnrichmentView.as_view()
        response = view(request, id="C123456")

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data["success"])
        self.assertFalse(data["has_content"])


class TestRecordRelatedRecordsView(TestCase):
    """Tests for the related records enrichment API endpoint."""

    def setUp(self):
        self.factory = RequestFactory()
        cache.clear()

    @patch("app.records.mixins.cache")
    @patch("app.records.views.RecordEnrichmentHelper")
    @patch("app.records.mixins.record_details_by_id")
    def test_returns_json_response(
        self, mock_record_details, mock_helper, mock_cache
    ):
        """Endpoint should return JSON response with related records."""
        mock_cache.get.return_value = None

        mock_record = Mock()
        mock_record.id = "C123456"
        mock_record_details.return_value = mock_record

        mock_helper_instance = Mock()
        mock_helper_instance.fetch_related.return_value = [
            Mock(id="C111", summary_title="Related 1"),
            Mock(id="C222", summary_title="Related 2"),
        ]
        mock_helper.return_value = mock_helper_instance

        request = self.factory.get("/catalogue/id/C123456/enrichment/related/")
        view = RecordRelatedRecordsView.as_view()

        with patch("app.records.views.render_to_string") as mock_render:
            mock_render.return_value = "<div>Related records</div>"
            response = view(request, id="C123456")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        data = json.loads(response.content)
        self.assertTrue(data["success"])
        self.assertTrue(data["has_content"])

    @patch("app.records.mixins.cache")
    @patch("app.records.views.RecordEnrichmentHelper")
    @patch("app.records.mixins.record_details_by_id")
    def test_no_content_when_no_related_records(
        self, mock_record_details, mock_helper, mock_cache
    ):
        """Endpoint should return has_content=False when no related records."""
        mock_cache.get.return_value = None

        mock_record = Mock()
        mock_record.id = "C123456"
        mock_record_details.return_value = mock_record

        mock_helper_instance = Mock()
        mock_helper_instance.fetch_related.return_value = []
        mock_helper.return_value = mock_helper_instance

        request = self.factory.get("/catalogue/id/C123456/enrichment/related/")
        view = RecordRelatedRecordsView.as_view()

        with patch("app.records.views.render_to_string") as mock_render:
            mock_render.return_value = ""
            response = view(request, id="C123456")

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data["success"])
        self.assertFalse(data["has_content"])


class TestRecordDeliveryOptionsView(TestCase):
    """Tests for the delivery options enrichment API endpoint."""

    def setUp(self):
        self.factory = RequestFactory()
        cache.clear()

    @patch("app.records.mixins.cache")
    @patch("app.records.views.RecordEnrichmentHelper")
    @patch("app.records.mixins.record_details_by_id")
    def test_returns_json_response_with_sections(
        self, mock_record_details, mock_helper, mock_cache
    ):
        """Endpoint should return JSON with multiple sections."""
        mock_cache.get.return_value = None

        mock_record = Mock()
        mock_record.id = "C123456"
        mock_record_details.return_value = mock_record

        mock_helper_instance = Mock()
        mock_helper_instance.fetch_delivery_options.return_value = {
            "do_availability_group": "AVAILABLE_ONLINE",
            "delivery_option": "DigitizedDiscovery",
            "delivery_options_heading": "How to order it",
            "delivery_instructions": ["Step 1", "Step 2"],
            "tna_discovery_link": "https://discovery.nationalarchives.gov.uk/details/r/C123456",
        }
        mock_helper.return_value = mock_helper_instance

        request = self.factory.get("/catalogue/id/C123456/enrichment/delivery/")
        view = RecordDeliveryOptionsView.as_view()

        with patch("app.records.views.render_to_string") as mock_render:
            mock_render.return_value = "<div>Content</div>"
            response = view(request, id="C123456")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        data = json.loads(response.content)
        self.assertTrue(data["success"])
        self.assertTrue(data["has_content"])
        self.assertIn("sections", data)
        self.assertIn("available_online", data["sections"])
        self.assertIn("available_in_person", data["sections"])
        self.assertIn("analytics", data)

    @patch("app.records.mixins.cache")
    @patch("app.records.views.RecordEnrichmentHelper")
    @patch("app.records.mixins.record_details_by_id")
    def test_returns_analytics_data(
        self, mock_record_details, mock_helper, mock_cache
    ):
        """Endpoint should include analytics data in response."""
        mock_cache.get.return_value = None

        mock_record = Mock()
        mock_record.id = "C123456"
        mock_record_details.return_value = mock_record

        mock_helper_instance = Mock()
        mock_helper_instance.fetch_delivery_options.return_value = {
            "do_availability_group": "AVAILABLE_ONLINE",
            "delivery_option": "DigitizedDiscovery",
        }
        mock_helper.return_value = mock_helper_instance

        request = self.factory.get("/catalogue/id/C123456/enrichment/delivery/")
        view = RecordDeliveryOptionsView.as_view()

        with patch("app.records.views.render_to_string") as mock_render:
            mock_render.return_value = "<div>Content</div>"
            response = view(request, id="C123456")

        data = json.loads(response.content)
        self.assertEqual(
            data["analytics"]["delivery_option"], "DigitizedDiscovery"
        )
        self.assertEqual(
            data["analytics"]["delivery_option_category"], "AVAILABLE_ONLINE"
        )


class TestRecordCaching(TestCase):
    """Tests for record caching in RecordContextMixin."""

    def setUp(self):
        cache.clear()

    @responses.activate
    def test_record_cached_between_requests(self):
        """Record should be cached and reused for enrichment endpoints."""
        # Set up mock response for Rosetta API
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C123456",
            json={
                "data": [
                    {
                        "@template": {
                            "details": {
                                "id": "C123456",
                                "title": "Test Title",
                                "source": "CAT",
                                "heldByCount": 100,
                            }
                        }
                    }
                ]
            },
            status=200,
        )

        # First request - should call API
        self.client.get("/catalogue/id/C123456/enrichment/subjects/")

        # Should have made exactly one API call
        self.assertEqual(len(responses.calls), 1)

        # Second request - should use cache
        self.client.get("/catalogue/id/C123456/enrichment/related/")

        # Should still have only one API call (cached)
        self.assertEqual(len(responses.calls), 1)

    @responses.activate
    def test_different_records_not_cached_together(self):
        """Different records should have separate cache entries."""
        # Set up mock responses for two different records
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C111111",
            json={
                "data": [
                    {
                        "@template": {
                            "details": {
                                "id": "C111111",
                                "title": "Record 1",
                                "source": "CAT",
                                "heldByCount": 100,
                            }
                        }
                    }
                ]
            },
            status=200,
        )
        responses.add(
            responses.GET,
            f"{settings.ROSETTA_API_URL}/get?id=C222222",
            json={
                "data": [
                    {
                        "@template": {
                            "details": {
                                "id": "C222222",
                                "title": "Record 2",
                                "source": "CAT",
                                "heldByCount": 100,
                            }
                        }
                    }
                ]
            },
            status=200,
        )

        # Request first record
        self.client.get("/catalogue/id/C111111/enrichment/subjects/")
        self.assertEqual(len(responses.calls), 1)

        # Request second record - should make new API call
        self.client.get("/catalogue/id/C222222/enrichment/subjects/")
        self.assertEqual(len(responses.calls), 2)

        # Request first record again - should use cache
        self.client.get("/catalogue/id/C111111/enrichment/related/")
        self.assertEqual(len(responses.calls), 2)
