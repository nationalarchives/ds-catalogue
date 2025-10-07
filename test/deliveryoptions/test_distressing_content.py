from app.deliveryoptions.delivery_options import (
    _get_dcs_prefix_variants,
    has_distressing_content,
)
from django.test import SimpleTestCase, override_settings


class TestDistressingContentMatch(SimpleTestCase):
    """Tests for distressing content matching functionality"""

    def setUp(self):
        """Clear the LRU cache before each test"""
        _get_dcs_prefix_variants.cache_clear()

    @override_settings(
        DCS_PREFIXES=[
            "HO 616",
            "AB 41",
            "J 14",
            "LOC 5",
            "HO 397",
            "ILB 2",
            "LEV 1",
            "GTI 2",
            "GTI 102",
            "ICSA 1",
            "ICSA 2",
            "ICSA 3",
            "ICSA 4",
            "ICSA 5",
            "ICSA 6",
            "ICSA 7",
            "ES 38",
        ]
    )
    def test_matching_prefix_with_slash_returns_true(self):
        """Test that references with distressing content prefixes followed by slash return True"""
        test_cases = [
            "HO 616/123",
            "AB 41/456",
            "J 14/789",
            "LOC 5/1",
            "HO 397/2",
            "ILB 2/3",
            "LEV 1/4",
            "GTI 2/5",
            "GTI 102/6",
            "ICSA 1/7",
            "ICSA 7/8",
            "ES 38/9",
        ]

        for reference in test_cases:
            with self.subTest(reference=reference):
                self.assertTrue(has_distressing_content(reference))

    @override_settings(
        DCS_PREFIXES=[
            "HO 616",
            "AB 41",
            "GTI 2",
            "GTI 102",
        ]
    )
    def test_exact_match_without_slash_returns_true(self):
        """Test that references that exactly match the prefix (no slash) return True"""
        test_cases = [
            "HO 616",
            "AB 41",
            "GTI 2",
            "GTI 102",
        ]

        for reference in test_cases:
            with self.subTest(reference=reference):
                self.assertTrue(has_distressing_content(reference))

    @override_settings(
        DCS_PREFIXES=[
            "HO 616",
            "AB 41",
            "J 14",
            "LOC 5",
            "GTI 2",
            "GTI 102",
        ]
    )
    def test_non_matching_prefix_returns_false(self):
        """Test that references without distressing content prefixes return False"""
        test_cases = [
            "DEFE 65",
            "AIR 79/962",
            "WO 208",
            "ADM 223",
            "C 32/18",
            "PROB 11",
            "RG 9",
        ]

        for reference in test_cases:
            with self.subTest(reference=reference):
                self.assertFalse(has_distressing_content(reference))

    @override_settings(
        DCS_PREFIXES=[
            "HO 616",
            "AB 41",
            "GTI 2",
            "GTI 102",
        ]
    )
    def test_prefix_with_additional_characters_no_slash_returns_false(self):
        """Test that prefix followed by characters (not slash) returns False"""
        test_cases = [
            "HO 6161",  # Extra digit
            "HO 616A",  # Extra letter
            "AB 411",  # Extra digit
            "GTI 20",  # Looks like GTI 2 but has extra digit
            "GTI 1020",  # Looks like GTI 102 but has extra digit
            "GTI 2X",  # GTI 2 with letter
        ]

        for reference in test_cases:
            with self.subTest(reference=reference):
                self.assertFalse(has_distressing_content(reference))

    @override_settings(
        DCS_PREFIXES=[
            "HO 616",
            "AB 41",
            "GTI 2",
            "GTI 102",
        ]
    )
    def test_partial_prefix_match_returns_false(self):
        """Test that partial prefix matches return False"""
        test_cases = [
            "HO 61",  # Partial match of HO 616
            "HO 6",  # Partial match of HO 616
            "AB 4",  # Partial match of AB 41
            "GTI 1",  # Not GTI 2 or GTI 102
            "GTI 10",  # Partial match of GTI 102
            "H",  # Partial match of HO 616
        ]

        for reference in test_cases:
            with self.subTest(reference=reference):
                self.assertFalse(has_distressing_content(reference))

    @override_settings(
        DCS_PREFIXES=[
            "GTI 2",
            "GTI 102",
        ]
    )
    def test_longer_prefix_does_not_conflict_with_shorter(self):
        """Test that GTI 102 and GTI 2 are distinguished correctly"""
        # GTI 102 matches
        self.assertTrue(has_distressing_content("GTI 102"))
        self.assertTrue(has_distressing_content("GTI 102/1"))

        # GTI 2 matches
        self.assertTrue(has_distressing_content("GTI 2"))
        self.assertTrue(has_distressing_content("GTI 2/1"))

        # These should NOT match
        self.assertFalse(has_distressing_content("GTI 10"))
        self.assertFalse(has_distressing_content("GTI 1"))
        self.assertFalse(has_distressing_content("GTI 20"))
        self.assertFalse(has_distressing_content("GTI 1020"))

    @override_settings(DCS_PREFIXES=[])
    def test_empty_prefix_list_returns_false(self):
        """Test that empty prefix list returns False for any reference"""
        test_cases = [
            "HO 616/123",
            "AB 41/456",
            "DEFE 65",
            "GTI 2",
        ]

        for reference in test_cases:
            with self.subTest(reference=reference):
                self.assertFalse(has_distressing_content(reference))
