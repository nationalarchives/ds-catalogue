from unittest.mock import patch

from app.main.api import (
    fetch_global_notifications,
    fetch_landing_page_data,
    get_explore_the_collection,
)
from app.main.constants import (
    GLOBAL_NOTIFICATIONS_CACHE_KEY,
    LANDING_PAGE_CACHE_KEY,
    WAGTAIL_API_CACHE_TIMEOUT,
)
from django.core.cache import cache
from django.test import TestCase


class TestFetchGlobalNotifications(TestCase):
    """Tests for fetch_global_notifications function."""

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    @patch("app.main.api.wagtail_request_handler")
    def test_fetches_from_api_when_cache_empty(self, mock_handler):
        """Test that data is fetched from API when cache is empty."""
        mock_handler.return_value = {
            "global_alert": {"title": "Test Alert"},
            "mourning_notice": None,
        }

        result = fetch_global_notifications()

        mock_handler.assert_called_once_with("/globals/notifications/")
        self.assertEqual(result["global_alert"]["title"], "Test Alert")

    @patch("app.main.api.wagtail_request_handler")
    def test_returns_cached_data_when_available(self, mock_handler):
        """Test that cached data is returned without API call."""
        cached_data = {
            "global_alert": {"title": "Cached Alert"},
            "mourning_notice": None,
        }
        cache.set(
            GLOBAL_NOTIFICATIONS_CACHE_KEY,
            cached_data,
            timeout=WAGTAIL_API_CACHE_TIMEOUT,
        )

        result = fetch_global_notifications()

        mock_handler.assert_not_called()
        self.assertEqual(result["global_alert"]["title"], "Cached Alert")

    @patch("app.main.api.wagtail_request_handler")
    def test_caches_api_response(self, mock_handler):
        """Test that API response is cached."""
        mock_handler.return_value = {
            "global_alert": {"title": "New Alert"},
            "mourning_notice": None,
        }

        fetch_global_notifications()

        cached = cache.get(GLOBAL_NOTIFICATIONS_CACHE_KEY)
        self.assertIsNotNone(cached)
        self.assertEqual(cached["global_alert"]["title"], "New Alert")

    @patch("app.main.api.wagtail_request_handler")
    def test_returns_none_on_api_error(self, mock_handler):
        """Test that None is returned when API call fails."""
        mock_handler.side_effect = Exception("API Error")

        result = fetch_global_notifications()

        self.assertIsNone(result)

    @patch("app.main.api.wagtail_request_handler")
    def test_does_not_cache_on_api_error(self, mock_handler):
        """Test that failed API responses are not cached."""
        mock_handler.side_effect = Exception("API Error")

        fetch_global_notifications()

        cached = cache.get(GLOBAL_NOTIFICATIONS_CACHE_KEY)
        self.assertIsNone(cached)


class TestFetchGlobalNotificationsGetters(TestCase):
    """Tests for global_alert and mourning_notice access via fetch_global_notifications."""

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    @patch("app.main.api.wagtail_request_handler")
    def test_global_alert_present(self, mock_handler):
        """Test that global_alert is accessible when present."""
        mock_handler.return_value = {
            "global_alert": {
                "title": "Alert Title",
                "message": "<p>Alert message</p>",
                "alert_level": "high",
                "cascade": True,
                "uid": 12345,
            },
            "mourning_notice": None,
        }

        result = fetch_global_notifications()

        self.assertEqual(result["global_alert"]["title"], "Alert Title")
        self.assertEqual(result["global_alert"]["uid"], 12345)

    @patch("app.main.api.wagtail_request_handler")
    def test_global_alert_none_when_absent(self, mock_handler):
        """Test that global_alert is None when not present."""
        mock_handler.return_value = {
            "global_alert": None,
            "mourning_notice": None,
        }

        result = fetch_global_notifications()

        self.assertIsNone(result["global_alert"])

    @patch("app.main.api.wagtail_request_handler")
    def test_mourning_notice_present(self, mock_handler):
        """Test that mourning_notice is accessible when present."""
        mock_handler.return_value = {
            "global_alert": None,
            "mourning_notice": {
                "title": "Mourning Title",
                "message": "<p>Mourning message</p>",
            },
        }

        result = fetch_global_notifications()

        self.assertEqual(result["mourning_notice"]["title"], "Mourning Title")

    @patch("app.main.api.wagtail_request_handler")
    def test_mourning_notice_none_when_absent(self, mock_handler):
        """Test that mourning_notice is None when not present."""
        mock_handler.return_value = {
            "global_alert": None,
            "mourning_notice": None,
        }

        result = fetch_global_notifications()

        self.assertIsNone(result["mourning_notice"])


class TestFetchLandingPageData(TestCase):
    """Tests for fetch_landing_page_data function."""

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    @patch("app.main.api.wagtail_request_handler")
    def test_fetches_from_api_when_cache_empty(self, mock_handler):
        """Test that data is fetched from API when cache is empty."""
        mock_handler.return_value = {
            "global_alert": None,
            "mourning_notice": None,
            "explore_the_collection": {
                "top_pages": [{"title": "Page 1"}],
                "latest_articles": [{"title": "Article 1"}],
            },
        }

        result = fetch_landing_page_data()

        mock_handler.assert_called_once_with("/catalogue/landing/")
        self.assertEqual(
            result["explore_the_collection"]["top_pages"][0]["title"], "Page 1"
        )

    @patch("app.main.api.wagtail_request_handler")
    def test_returns_cached_data_when_available(self, mock_handler):
        """Test that cached data is returned without API call."""
        cached_data = {
            "explore_the_collection": {
                "top_pages": [{"title": "Cached Page"}],
                "latest_articles": [],
            },
        }
        cache.set(
            LANDING_PAGE_CACHE_KEY,
            cached_data,
            timeout=WAGTAIL_API_CACHE_TIMEOUT,
        )

        result = fetch_landing_page_data()

        mock_handler.assert_not_called()
        self.assertEqual(
            result["explore_the_collection"]["top_pages"][0]["title"],
            "Cached Page",
        )

    @patch("app.main.api.wagtail_request_handler")
    def test_caches_api_response(self, mock_handler):
        """Test that API response is cached."""
        mock_handler.return_value = {
            "global_alert": None,
            "mourning_notice": None,
            "explore_the_collection": {
                "top_pages": [{"title": "New Page"}],
                "latest_articles": [],
            },
        }

        fetch_landing_page_data()

        cached = cache.get(LANDING_PAGE_CACHE_KEY)
        self.assertIsNotNone(cached)
        self.assertEqual(
            cached["explore_the_collection"]["top_pages"][0]["title"],
            "New Page",
        )

    @patch("app.main.api.wagtail_request_handler")
    def test_returns_none_on_api_error(self, mock_handler):
        """Test that None is returned when API call fails."""
        mock_handler.side_effect = Exception("API Error")

        result = fetch_landing_page_data()

        self.assertIsNone(result)

    @patch("app.main.api.wagtail_request_handler")
    def test_populates_notifications_cache_when_empty(self, mock_handler):
        """Test that notifications cache is populated from landing page response."""
        mock_handler.return_value = {
            "global_alert": {"title": "Alert from landing"},
            "mourning_notice": None,
            "explore_the_collection": {
                "top_pages": [],
                "latest_articles": [],
            },
        }

        fetch_landing_page_data()

        notifications_cached = cache.get(GLOBAL_NOTIFICATIONS_CACHE_KEY)
        self.assertIsNotNone(notifications_cached)
        self.assertEqual(
            notifications_cached["global_alert"]["title"], "Alert from landing"
        )

    @patch("app.main.api.wagtail_request_handler")
    def test_does_not_overwrite_existing_notifications_cache(
        self, mock_handler
    ):
        """Test that an already-warm notifications cache is not overwritten."""
        existing_notifications = {
            "global_alert": {"title": "Already cached alert"},
            "mourning_notice": None,
        }
        cache.set(
            GLOBAL_NOTIFICATIONS_CACHE_KEY,
            existing_notifications,
            timeout=WAGTAIL_API_CACHE_TIMEOUT,
        )
        mock_handler.return_value = {
            "global_alert": {"title": "Landing alert"},
            "mourning_notice": None,
            "explore_the_collection": {
                "top_pages": [],
                "latest_articles": [],
            },
        }

        fetch_landing_page_data()

        notifications_cached = cache.get(GLOBAL_NOTIFICATIONS_CACHE_KEY)
        self.assertEqual(
            notifications_cached["global_alert"]["title"],
            "Already cached alert",
        )


class TestGetExploreTheCollection(TestCase):
    """Tests for get_explore_the_collection function."""

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    @patch("app.main.api.fetch_landing_page_data")
    def test_returns_explore_the_collection_when_present(self, mock_fetch):
        """Test that explore_the_collection data is returned when present."""
        mock_fetch.return_value = {
            "explore_the_collection": {
                "top_pages": [
                    {"id": 1, "title": "Page 1"},
                    {"id": 2, "title": "Page 2"},
                ],
                "latest_articles": [
                    {"id": 1, "title": "Article 1"},
                ],
            },
        }

        result = get_explore_the_collection()

        self.assertEqual(len(result["top_pages"]), 2)
        self.assertEqual(result["top_pages"][0]["title"], "Page 1")
        self.assertEqual(len(result["latest_articles"]), 1)
        self.assertEqual(result["latest_articles"][0]["title"], "Article 1")

    @patch("app.main.api.fetch_landing_page_data")
    def test_returns_empty_dict_when_fetch_fails(self, mock_fetch):
        """Test that empty dict is returned when fetch fails."""
        mock_fetch.return_value = None

        result = get_explore_the_collection()

        self.assertEqual(result, {})

    @patch("app.main.api.fetch_landing_page_data")
    def test_returns_empty_dict_when_explore_missing(self, mock_fetch):
        """Test that empty dict is returned when explore_the_collection is missing."""
        mock_fetch.return_value = {}

        result = get_explore_the_collection()

        self.assertEqual(result, {})
