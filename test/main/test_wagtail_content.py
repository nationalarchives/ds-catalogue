from unittest.mock import Mock, patch

from app.main.constants import (
    LANDING_PAGE_CACHE_KEY,
    NOTIFICATIONS_CACHE_KEY,
    WAGTAIL_API_CACHE_TIMEOUT,
)
from app.main.wagtail_content import (
    fetch_landing_page_data,
    fetch_notifications_data,
    get_global_alert,
    get_landing_page_global_alert,
    get_landing_page_mourning_notice,
    get_latest_articles,
    get_mourning_notice,
    get_top_pages,
)
from django.core.cache import cache
from django.test import TestCase, override_settings


class TestFetchNotificationsData(TestCase):
    """Tests for fetch_notifications_data function."""

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    @patch("app.main.wagtail_content.JSONAPIClient")
    def test_fetches_from_api_when_cache_empty(self, mock_client_class):
        """Test that data is fetched from API when cache is empty."""
        mock_client = Mock()
        mock_client.get.return_value = {
            "global_alert": {"title": "Test Alert"},
            "mourning_notice": None,
        }
        mock_client_class.return_value = mock_client

        result = fetch_notifications_data()

        mock_client.get.assert_called_once_with("/globals/notifications/")
        self.assertEqual(result["global_alert"]["title"], "Test Alert")

    @patch("app.main.wagtail_content.JSONAPIClient")
    def test_returns_cached_data_when_available(self, mock_client_class):
        """Test that cached data is returned without API call."""
        cached_data = {
            "global_alert": {"title": "Cached Alert"},
            "mourning_notice": None,
        }
        cache.set(
            NOTIFICATIONS_CACHE_KEY,
            cached_data,
            timeout=WAGTAIL_API_CACHE_TIMEOUT,
        )

        result = fetch_notifications_data()

        mock_client_class.assert_not_called()
        self.assertEqual(result["global_alert"]["title"], "Cached Alert")

    @patch("app.main.wagtail_content.JSONAPIClient")
    def test_caches_api_response(self, mock_client_class):
        """Test that API response is cached."""
        mock_client = Mock()
        mock_client.get.return_value = {
            "global_alert": {"title": "New Alert"},
            "mourning_notice": None,
        }
        mock_client_class.return_value = mock_client

        fetch_notifications_data()

        cached = cache.get(NOTIFICATIONS_CACHE_KEY)
        self.assertIsNotNone(cached)
        self.assertEqual(cached["global_alert"]["title"], "New Alert")

    @patch("app.main.wagtail_content.JSONAPIClient")
    def test_returns_none_on_api_error(self, mock_client_class):
        """Test that None is returned when API call fails."""
        mock_client = Mock()
        mock_client.get.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client

        result = fetch_notifications_data()

        self.assertIsNone(result)

    @patch("app.main.wagtail_content.JSONAPIClient")
    def test_does_not_cache_on_api_error(self, mock_client_class):
        """Test that failed API responses are not cached."""
        mock_client = Mock()
        mock_client.get.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client

        fetch_notifications_data()

        cached = cache.get(NOTIFICATIONS_CACHE_KEY)
        self.assertIsNone(cached)


class TestFetchLandingPageData(TestCase):
    """Tests for fetch_landing_page_data function."""

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    @patch("app.main.wagtail_content.JSONAPIClient")
    def test_fetches_from_api_when_cache_empty(self, mock_client_class):
        """Test that data is fetched from API when cache is empty."""
        mock_client = Mock()
        mock_client.get.return_value = {
            "global_alert": None,
            "mourning_notice": None,
            "explore_the_collection": {
                "top_pages": [{"title": "Page 1"}],
                "latest_articles": [{"title": "Article 1"}],
            },
        }
        mock_client_class.return_value = mock_client

        result = fetch_landing_page_data()

        mock_client.get.assert_called_once_with("/catalogue/landing/")
        self.assertEqual(
            result["explore_the_collection"]["top_pages"][0]["title"], "Page 1"
        )

    @patch("app.main.wagtail_content.JSONAPIClient")
    def test_returns_cached_data_when_available(self, mock_client_class):
        """Test that cached data is returned without API call."""
        cached_data = {
            "global_alert": None,
            "mourning_notice": None,
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

        mock_client_class.assert_not_called()
        self.assertEqual(
            result["explore_the_collection"]["top_pages"][0]["title"],
            "Cached Page",
        )

    @patch("app.main.wagtail_content.JSONAPIClient")
    def test_caches_api_response(self, mock_client_class):
        """Test that API response is cached."""
        mock_client = Mock()
        mock_client.get.return_value = {
            "global_alert": None,
            "mourning_notice": None,
            "explore_the_collection": {
                "top_pages": [{"title": "New Page"}],
                "latest_articles": [],
            },
        }
        mock_client_class.return_value = mock_client

        fetch_landing_page_data()

        cached = cache.get(LANDING_PAGE_CACHE_KEY)
        self.assertIsNotNone(cached)
        self.assertEqual(
            cached["explore_the_collection"]["top_pages"][0]["title"],
            "New Page",
        )

    @patch("app.main.wagtail_content.JSONAPIClient")
    def test_returns_none_on_api_error(self, mock_client_class):
        """Test that None is returned when API call fails."""
        mock_client = Mock()
        mock_client.get.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client

        result = fetch_landing_page_data()

        self.assertIsNone(result)


class TestGetGlobalAlert(TestCase):
    """Tests for get_global_alert function."""

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    @patch("app.main.wagtail_content.fetch_notifications_data")
    def test_returns_global_alert_when_present(self, mock_fetch):
        """Test that global_alert is returned when present."""
        mock_fetch.return_value = {
            "global_alert": {
                "title": "Alert Title",
                "message": "<p>Alert message</p>",
                "alert_level": "high",
                "cascade": True,
                "uid": 12345,
            },
            "mourning_notice": None,
        }

        result = get_global_alert()

        self.assertEqual(result["title"], "Alert Title")
        self.assertEqual(result["uid"], 12345)

    @patch("app.main.wagtail_content.fetch_notifications_data")
    def test_returns_none_when_no_alert(self, mock_fetch):
        """Test that None is returned when no global_alert."""
        mock_fetch.return_value = {
            "global_alert": None,
            "mourning_notice": None,
        }

        result = get_global_alert()

        self.assertIsNone(result)

    @patch("app.main.wagtail_content.fetch_notifications_data")
    def test_returns_none_when_fetch_fails(self, mock_fetch):
        """Test that None is returned when fetch fails."""
        mock_fetch.return_value = None

        result = get_global_alert()

        self.assertIsNone(result)


class TestGetMourningNotice(TestCase):
    """Tests for get_mourning_notice function."""

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    @patch("app.main.wagtail_content.fetch_notifications_data")
    def test_returns_mourning_notice_when_present(self, mock_fetch):
        """Test that mourning_notice is returned when present."""
        mock_fetch.return_value = {
            "global_alert": None,
            "mourning_notice": {
                "title": "Mourning Title",
                "message": "<p>Mourning message</p>",
            },
        }

        result = get_mourning_notice()

        self.assertEqual(result["title"], "Mourning Title")

    @patch("app.main.wagtail_content.fetch_notifications_data")
    def test_returns_none_when_no_notice(self, mock_fetch):
        """Test that None is returned when no mourning_notice."""
        mock_fetch.return_value = {
            "global_alert": None,
            "mourning_notice": None,
        }

        result = get_mourning_notice()

        self.assertIsNone(result)

    @patch("app.main.wagtail_content.fetch_notifications_data")
    def test_returns_none_when_fetch_fails(self, mock_fetch):
        """Test that None is returned when fetch fails."""
        mock_fetch.return_value = None

        result = get_mourning_notice()

        self.assertIsNone(result)


class TestGetTopPages(TestCase):
    """Tests for get_top_pages function."""

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    @patch("app.main.wagtail_content.fetch_landing_page_data")
    def test_returns_top_pages_when_present(self, mock_fetch):
        """Test that top_pages list is returned when present."""
        mock_fetch.return_value = {
            "global_alert": None,
            "mourning_notice": None,
            "explore_the_collection": {
                "top_pages": [
                    {"id": 1, "title": "Page 1"},
                    {"id": 2, "title": "Page 2"},
                ],
                "latest_articles": [],
            },
        }

        result = get_top_pages()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["title"], "Page 1")

    @patch("app.main.wagtail_content.fetch_landing_page_data")
    def test_returns_empty_list_when_no_pages(self, mock_fetch):
        """Test that empty list is returned when no top_pages."""
        mock_fetch.return_value = {
            "global_alert": None,
            "mourning_notice": None,
            "explore_the_collection": {
                "top_pages": [],
                "latest_articles": [],
            },
        }

        result = get_top_pages()

        self.assertEqual(result, [])

    @patch("app.main.wagtail_content.fetch_landing_page_data")
    def test_returns_empty_list_when_fetch_fails(self, mock_fetch):
        """Test that empty list is returned when fetch fails."""
        mock_fetch.return_value = None

        result = get_top_pages()

        self.assertEqual(result, [])

    @patch("app.main.wagtail_content.fetch_landing_page_data")
    def test_returns_empty_list_when_explore_missing(self, mock_fetch):
        """Test that empty list is returned when explore_the_collection is missing."""
        mock_fetch.return_value = {
            "global_alert": None,
            "mourning_notice": None,
        }

        result = get_top_pages()

        self.assertEqual(result, [])


class TestGetLatestArticles(TestCase):
    """Tests for get_latest_articles function."""

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    @patch("app.main.wagtail_content.fetch_landing_page_data")
    def test_returns_latest_articles_when_present(self, mock_fetch):
        """Test that latest_articles list is returned when present."""
        mock_fetch.return_value = {
            "global_alert": None,
            "mourning_notice": None,
            "explore_the_collection": {
                "top_pages": [],
                "latest_articles": [
                    {"id": 1, "title": "Article 1"},
                    {"id": 2, "title": "Article 2"},
                    {"id": 3, "title": "Article 3"},
                ],
            },
        }

        result = get_latest_articles()

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["title"], "Article 1")

    @patch("app.main.wagtail_content.fetch_landing_page_data")
    def test_returns_empty_list_when_no_articles(self, mock_fetch):
        """Test that empty list is returned when no latest_articles."""
        mock_fetch.return_value = {
            "global_alert": None,
            "mourning_notice": None,
            "explore_the_collection": {
                "top_pages": [],
                "latest_articles": [],
            },
        }

        result = get_latest_articles()

        self.assertEqual(result, [])

    @patch("app.main.wagtail_content.fetch_landing_page_data")
    def test_returns_empty_list_when_fetch_fails(self, mock_fetch):
        """Test that empty list is returned when fetch fails."""
        mock_fetch.return_value = None

        result = get_latest_articles()

        self.assertEqual(result, [])


class TestGetLandingPageGlobalAlert(TestCase):
    """Tests for get_landing_page_global_alert function."""

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    @patch("app.main.wagtail_content.fetch_landing_page_data")
    def test_returns_global_alert_from_landing_page_data(self, mock_fetch):
        """Test that global_alert is returned from landing page data."""
        mock_fetch.return_value = {
            "global_alert": {
                "title": "Landing Alert",
                "uid": 99999,
            },
            "mourning_notice": None,
            "explore_the_collection": {},
        }

        result = get_landing_page_global_alert()

        self.assertEqual(result["title"], "Landing Alert")

    @patch("app.main.wagtail_content.fetch_landing_page_data")
    def test_returns_none_when_fetch_fails(self, mock_fetch):
        """Test that None is returned when fetch fails."""
        mock_fetch.return_value = None

        result = get_landing_page_global_alert()

        self.assertIsNone(result)


class TestGetLandingPageMourningNotice(TestCase):
    """Tests for get_landing_page_mourning_notice function."""

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    @patch("app.main.wagtail_content.fetch_landing_page_data")
    def test_returns_mourning_notice_from_landing_page_data(self, mock_fetch):
        """Test that mourning_notice is returned from landing page data."""
        mock_fetch.return_value = {
            "global_alert": None,
            "mourning_notice": {
                "title": "Landing Mourning",
                "message": "<p>Message</p>",
            },
            "explore_the_collection": {},
        }

        result = get_landing_page_mourning_notice()

        self.assertEqual(result["title"], "Landing Mourning")

    @patch("app.main.wagtail_content.fetch_landing_page_data")
    def test_returns_none_when_fetch_fails(self, mock_fetch):
        """Test that None is returned when fetch fails."""
        mock_fetch.return_value = None

        result = get_landing_page_mourning_notice()

        self.assertIsNone(result)
