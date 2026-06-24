from django.test import SimpleTestCase
from django.utils.module_loading import import_string

from app.errors.views import page_not_found_error_view


class Handler404WiringTestCase(SimpleTestCase):
    """The custom 404 handler only fires when DEBUG is False, so nothing else
    exercises it. This guards against a typo'd dotted path or a moved view."""

    def test_handler404_resolves_to_error_view(self):
        from config.urls import handler404

        self.assertIs(import_string(handler404), page_not_found_error_view)
