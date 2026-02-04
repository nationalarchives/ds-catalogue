"""Tests for utility functions in util.py"""

import os
from unittest.mock import patch

from config.util import get_bool_env, get_int_env
from django.test import TestCase


class TestGetIntEnv(TestCase):
    """Tests for get_int_env function"""

    def test_returns_valid_integer(self):
        """Test that valid integer string is parsed correctly"""
        with patch.dict(os.environ, {"TEST_VAR": "10"}):
            self.assertEqual(get_int_env("TEST_VAR", 5), 10)

    def test_not_set_returns_default(self):
        """Test that unset environment variable returns default"""
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(get_int_env("TEST_VAR", 5), 5)

    def test_empty_string_returns_default(self):
        """Test that empty string returns default"""
        with patch.dict(os.environ, {"TEST_VAR": ""}):
            self.assertEqual(get_int_env("TEST_VAR", 5), 5)

    def test_zero_returns_default(self):
        """Test that zero returns default (prevents dangerous timeout)"""
        with patch.dict(os.environ, {"TEST_VAR": "0"}):
            self.assertEqual(get_int_env("TEST_VAR", 5), 5)

    def test_invalid_string_returns_default(self):
        """Test that non-numeric string returns default"""
        with patch.dict(os.environ, {"TEST_VAR": "abc"}):
            self.assertEqual(get_int_env("TEST_VAR", 5), 5)

    def test_whitespace_stripped(self):
        """Test that whitespace is stripped from valid values"""
        with patch.dict(os.environ, {"TEST_VAR": "  10  "}):
            self.assertEqual(get_int_env("TEST_VAR", 5), 10)


class TestGetBoolEnv(TestCase):
    """Tests for get_bool_env function"""

    def test_true_values(self):
        """Test that true values return True"""
        for value in ["true", "True", "yes", "1"]:
            with patch.dict(os.environ, {"TEST_VAR": value}):
                self.assertTrue(get_bool_env("TEST_VAR", False))

    def test_false_values(self):
        """Test that false values return False"""
        for value in ["false", "False", "no", "0"]:
            with patch.dict(os.environ, {"TEST_VAR": value}):
                self.assertFalse(get_bool_env("TEST_VAR", True))

    def test_not_set_returns_default(self):
        """Test that unset environment variable returns default"""
        with patch.dict(os.environ, {}, clear=True):
            self.assertTrue(get_bool_env("TEST_VAR", True))
            self.assertFalse(get_bool_env("TEST_VAR", False))

    def test_empty_string_returns_default(self):
        """Test that empty string returns default"""
        with patch.dict(os.environ, {"TEST_VAR": ""}):
            self.assertTrue(get_bool_env("TEST_VAR", True))

    def test_invalid_string_returns_default(self):
        """Test that invalid string returns default"""
        with patch.dict(os.environ, {"TEST_VAR": "invalid"}):
            self.assertFalse(get_bool_env("TEST_VAR", False))
