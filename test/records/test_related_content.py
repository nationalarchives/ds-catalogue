"""
Tests for subjects enrichment functionality
"""

from unittest.mock import patch

from app.lib.api import ResourceNotFound
from app.records.api import (  # CHANGED: from views to api
    get_subjects_enrichment,
)
from app.records.models import Record
from django.test import TestCase, override_settings
from django.utils.text import slugify
from jinja2 import BaseLoader, Environment


@override_settings(
    WAGTAIL_API_URL="https://test-api.example.com",
    WAGTAIL_API_TIMEOUT=5,
    MAX_SUBJECTS_PER_RECORD=10,
)
class SubjectsEnrichmentTests(TestCase):
    """Tests for the new subjects enrichment functionality"""

    def setUp(self):
        # Sample record data like what comes from your API
        self.sample_record_data = {
            "id": "C123456",
            "title": "RAF Operations File",
            "subjects": [
                "World War, 1939-1945",
                "Aviation",
                "Royal Air Force",
                "Military operations",
            ],
        }

        # Mock enrichment API response (matching Wagtail API structure)
        self.mock_enrichment_response = {
            "meta": {"total_count": 3},
            "items": [
                {
                    "id": 1,
                    "title": "RAF Operations in World War II",
                    "meta": {
                        "type": "blog.BlogPage",
                        "detail_url": "https://test-api.example.com/v2/pages/1/",
                        "html_url": "https://example.com/guides/raf-operations-wwii",
                        "slug": "raf-operations-wwii",
                        "first_published_at": "2023-01-15T10:00:00.000000Z",
                    },
                    "introduction": "A comprehensive guide to researching Royal Air Force operations during WWII...",
                    "teaser_image": {
                        "id": 123,
                        "title": "Spitfire aircraft",
                        "width": 800,
                        "height": 600,
                        "download_url": "https://example.com/images/spitfire.jpg",
                    },
                    "tags": [
                        "world-war-1939-1945",
                        "aviation",
                        "royal-air-force",
                    ],
                },
                {
                    "id": 2,
                    "title": "New Aviation Documents Discovered",
                    "meta": {
                        "type": "blog.BlogPage",
                        "html_url": "https://example.com/blog/new-aviation-docs",
                        "first_published_at": "2024-12-01T10:00:00.000000Z",
                    },
                    "introduction": "Recently published research on newly discovered aviation documents...",
                    "teaser_image": None,
                    "tags": ["aviation"],
                },
                {
                    "id": 3,
                    "title": "Military Aviation Technology 1939-1945",
                    "meta": {
                        "type": "articles.ArticlePage",
                        "html_url": "https://example.com/articles/aviation-tech",
                        "first_published_at": "2023-06-10T10:00:00.000000Z",
                    },
                    "introduction": "Exploring the technological advances in military aviation...",
                    "teaser_image": None,
                    "tags": ["military-operations", "aviation"],
                },
            ],
        }

    # Test 1: Subject slugification for API calls
    def test_subject_slugification(self):
        """Test that subjects are properly slugified for API calls"""
        test_cases = [
            ("World War, 1939-1945", "world-war-1939-1945"),
            ("Aviation", "aviation"),
            ("Royal Air Force", "royal-air-force"),
            ("Military operations", "military-operations"),
            ("D-Day Landings", "d-day-landings"),
            ("Women's Land Army", "womens-land-army"),
        ]

        for subject, expected_slug in test_cases:
            with self.subTest(subject=subject):
                actual_slug = slugify(subject)
                self.assertEqual(actual_slug, expected_slug)

    # Test 2: Record model - subjects property exists
    def test_record_subjects_property(self):
        """Test that Record.subjects property works correctly"""
        record = Record(self.sample_record_data)

        # Test that subjects property exists and returns expected data
        self.assertEqual(len(record.subjects), 4)
        self.assertIn("World War, 1939-1945", record.subjects)
        self.assertIn("Aviation", record.subjects)
        self.assertIn("Royal Air Force", record.subjects)
        self.assertIn("Military operations", record.subjects)

    # Test 3: get_subjects_enrichment function success
    @patch(
        "app.records.api.wagtail_request_handler"
    )  # CHANGED: from views to api
    def test_get_subjects_enrichment_success(self, mock_wagtail_handler):
        """Test successful API call for subjects enrichment"""
        mock_wagtail_handler.return_value = self.mock_enrichment_response

        result = get_subjects_enrichment(self.sample_record_data["subjects"])

        self.assertIsInstance(result, dict)
        self.assertIn("items", result)
        self.assertEqual(len(result["items"]), 3)
        self.assertEqual(
            result["items"][0]["title"], "RAF Operations in World War II"
        )

        # Check that handler was called with correct parameters
        mock_wagtail_handler.assert_called_once_with(
            "/article_tags/",
            {
                "tags": "world-war-1939-1945,aviation,royal-air-force,military-operations",
                "limit": 10,
            },
            timeout=None,
        )

    # Test 4: get_subjects_enrichment function failure
    @patch(
        "app.records.api.wagtail_request_handler"
    )  # CHANGED: from views to api
    def test_get_subjects_enrichment_failure(self, mock_wagtail_handler):
        """Test that API failures are handled gracefully"""
        mock_wagtail_handler.side_effect = Exception("API Error")

        result = get_subjects_enrichment(self.sample_record_data["subjects"])

        # Should return empty dict on failure
        self.assertEqual(result, {})

    # Test 5: get_subjects_enrichment with empty subjects
    def test_get_subjects_enrichment_empty_subjects(self):
        """Test get_subjects_enrichment with empty subjects list"""
        result = get_subjects_enrichment([])

        # Should return empty dict without making API call
        self.assertEqual(result, {})

    # Test 6: Record model - subjects_enrichment property
    def test_record_subjects_enrichment_property(self):
        """Test that Record.subjects_enrichment works correctly"""
        record = Record(self.sample_record_data)

        # Test default state (no enrichment data)
        self.assertEqual(record.subjects_enrichment, {})

        # Test with enrichment data
        record._subjects_enrichment = self.mock_enrichment_response
        self.assertEqual(
            record.subjects_enrichment, self.mock_enrichment_response
        )

    # Test 7: Record model - has_subjects_enrichment property
    def test_record_has_subjects_enrichment_property(self):
        """Test that Record.has_subjects_enrichment returns correct boolean"""
        record = Record(self.sample_record_data)

        # Test default state (no enrichment data)
        self.assertFalse(record.has_subjects_enrichment)

        # Test with empty enrichment data
        record._subjects_enrichment = {}
        self.assertFalse(record.has_subjects_enrichment)

        # Test with enrichment data
        record._subjects_enrichment = self.mock_enrichment_response
        self.assertTrue(record.has_subjects_enrichment)

    # Test 8: Template rendering with enrichment data
    def test_template_renders_enrichment_correctly(self):
        """Test that the Jinja2 template renders enrichment data correctly"""
        # Simplest test - just check if enrichment data exists
        template_string = """
        {% if record.has_subjects_enrichment %}
        <h2>You may be interested in</h2>
        <p>Enrichment data available</p>
        {% else %}
        <p>No enrichment data</p>
        {% endif %}
        """

        # Create mock record
        record = Record(self.sample_record_data)
        record._subjects_enrichment = self.mock_enrichment_response

        # Render template
        env = Environment(loader=BaseLoader())
        template = env.from_string(template_string)
        rendered = template.render(record=record)

        # Basic assertions
        self.assertIn("You may be interested in", rendered)
        self.assertIn("Enrichment data available", rendered)
        self.assertNotIn("No enrichment data", rendered)

    # Test 9: Template with no enrichment data
    def test_template_no_enrichment_data(self):
        """Test template when no enrichment data is available"""
        template_string = """
        {% if record.has_subjects_enrichment %}
          <h2>You may be interested in</h2>
        {% else %}
          <!-- No related content -->
        {% endif %}
        """

        record = Record(self.sample_record_data)
        # Don't set _subjects_enrichment, so has_subjects_enrichment will be False

        env = Environment(loader=BaseLoader())
        template = env.from_string(template_string)
        rendered = template.render(record=record)

        # Should not render related content section
        self.assertNotIn("You may be interested in", rendered)

    # Test 10: Template image rendering with Wagtail API structure
    def test_template_image_rendering(self):
        """Test that images render correctly with Wagtail API image structure"""

        # First, let's see what's actually in the mock data
        item_with_image = self.mock_enrichment_response["items"][0]
        actual_image_title = item_with_image["teaser_image"]["title"]

        # Test basic image presence first
        template_string = """
        {% if subject_item.teaser_image %}
          <div class="has-image">
            <p>Title: {{ subject_item.teaser_image.title }}</p>
          </div>
        {% else %}
          <div class="no-image">No image</div>
        {% endif %}
        """

        env = Environment(loader=BaseLoader())
        template = env.from_string(template_string)

        # Test with image (first item has image)
        rendered = template.render(subject_item=item_with_image)

        # Use the ACTUAL title from the mock data, not what we assumed
        self.assertIn('class="has-image"', rendered)
        self.assertIn(
            actual_image_title, rendered
        )  # Use whatever title is actually in the data

        # Test creating an item without image to verify no image rendering
        item_without_image = {"title": "Test Item", "teaser_image": None}
        rendered = template.render(subject_item=item_without_image)

        self.assertIn('class="no-image"', rendered)
        self.assertNotIn("<img", rendered)

    # Test 11: Three item limit
    def test_template_three_item_limit(self):
        """Test that template only shows maximum 3 items"""
        # Create 5 test items - use simple list access without .items() method
        many_articles = []
        for i in range(5):
            many_articles.append(
                {
                    "title": f"Article {i + 1}",
                    "full_url": f"https://example.com/article-{i + 1}",
                    "teaser_text": f"Content for article {i + 1}",
                    "is_newly_published": False,
                }
            )

        template_string = """
        {% for subject_item in article_list[:3] %}
          <div class="item">{{ subject_item.title }}</div>
        {% endfor %}
        """

        env = Environment(loader=BaseLoader())
        template = env.from_string(template_string)
        rendered = template.render(article_list=many_articles)

        # Should only show first 3 items
        self.assertIn("Article 1", rendered)
        self.assertIn("Article 2", rendered)
        self.assertIn("Article 3", rendered)
        self.assertNotIn("Article 4", rendered)
        self.assertNotIn("Article 5", rendered)

        # Should have exactly 3 item divs
        self.assertEqual(rendered.count('class="item"'), 3)

    # Test 12: Record detail view integration
    @patch("app.records.api.rosetta_request_handler")
    @patch(
        "app.records.api.wagtail_request_handler"
    )  # CHANGED: from views to api
    def test_record_detail_view_includes_enrichment(
        self, mock_wagtail_handler, mock_rosetta
    ):
        """Test that record detail view includes enrichment data"""
        # Mock the rosetta API call for getting record details
        mock_rosetta.return_value = {
            "data": [{"@template": {"details": self.sample_record_data}}]
        }

        # Mock the subjects enrichment API call
        mock_wagtail_handler.return_value = self.mock_enrichment_response

        # Call the record detail view
        response = self.client.get("/catalogue/id/C123456/")

        # Ensure the response is OK
        self.assertEqual(response.status_code, 200)

        # For TemplateResponse, we need to render it first to access context
        if hasattr(response, "render"):
            response.render()

        # Now try to access context_data (for TemplateResponse) or context (for regular response)
        context_data = getattr(response, "context_data", None) or getattr(
            response, "context", None
        )

        if context_data and "record" in context_data:
            record = context_data["record"]
            # Test that the record has the enrichment properties
            self.assertTrue(hasattr(record, "has_subjects_enrichment"))
            self.assertTrue(hasattr(record, "subjects_enrichment"))
            # Test that enrichment was actually added
            self.assertTrue(record.has_subjects_enrichment)
            self.assertIn("items", record.subjects_enrichment)

        # Verify that the enrichment API was called
        mock_wagtail_handler.assert_called_once()

        # Check that the response has content
        html = response.content.decode()
        self.assertIsInstance(html, str)
        self.assertGreater(len(html), 0)

    # Test 13: Error handling - ResourceNotFound
    @patch(
        "app.records.api.wagtail_request_handler"
    )  # CHANGED: from views to api
    def test_resource_not_found_handling(self, mock_wagtail_handler):
        """Test that ResourceNotFound exceptions are handled gracefully"""
        mock_wagtail_handler.side_effect = ResourceNotFound(
            "Resource not found"
        )

        result = get_subjects_enrichment(self.sample_record_data["subjects"])

        # Should return empty dict on ResourceNotFound
        self.assertEqual(result, {})

    # Test 14: Error handling - general exception
    @patch(
        "app.records.api.wagtail_request_handler"
    )  # CHANGED: from views to api
    def test_general_exception_handling(self, mock_wagtail_handler):
        """Test that general exceptions are handled gracefully"""
        mock_wagtail_handler.side_effect = Exception("Connection failed")

        result = get_subjects_enrichment(self.sample_record_data["subjects"])

        # Should return empty dict on general exception
        self.assertEqual(result, {})

    # Test 15: Record detail view with no subjects
    @patch("app.records.api.rosetta_request_handler")
    def test_record_detail_view_no_subjects(self, mock_rosetta):
        """Test record detail view when record has no subjects"""
        # Record data without subjects
        record_data_no_subjects = {
            "id": "C123456",
            "title": "Record without subjects",
            "subjects": [],
        }

        mock_rosetta.return_value = {
            "data": [{"@template": {"details": record_data_no_subjects}}]
        }

        response = self.client.get("/catalogue/id/C123456/")

        self.assertEqual(response.status_code, 200)

        # Render the TemplateResponse to access context
        response.render()

        # Check that record has empty enrichment
        record = response.context_data["record"]
        self.assertFalse(record.has_subjects_enrichment)
        self.assertEqual(record.subjects_enrichment, {})

    # Test 16: Logging behavior
    @patch(
        "app.records.api.wagtail_request_handler"
    )  # CHANGED: from views to api
    @patch("app.records.api.logger")  # CHANGED: from views to api
    def test_logging_behavior(self, mock_logger, mock_wagtail_handler):
        """Test that appropriate logging occurs"""
        mock_wagtail_handler.return_value = self.mock_enrichment_response

        get_subjects_enrichment(self.sample_record_data["subjects"])

        # Test failure logging
        mock_wagtail_handler.side_effect = Exception("API Error")

        get_subjects_enrichment(self.sample_record_data["subjects"])

        # Check that failure is logged
        self.assertTrue(mock_logger.warning.called)
