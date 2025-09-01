from app.search.utils import underscore_to_camelcase, camelcase_to_underscore
from django.test import SimpleTestCase


class TestUtils(SimpleTestCase):
    def test_camelcase_to_underscore(self):
        test_cases = {
            "simpleTest": "simple_test",
            "anotherExampleHere": "another_example_here",
            "nochange": "nochange",
            "withNumbers123": "with_numbers123",
            "mixedCASETest": "mixed_case_test",
        }

        for input_str, expected_output in test_cases.items():
            with self.subTest(input_str=input_str):
                self.assertEqual(camelcase_to_underscore(input_str), expected_output)
    
    def test_underscore_to_camelcase(self):
        test_cases = {
            "simple_test": "simpleTest",
            "another_example_here": "anotherExampleHere",
            "nochange": "nochange",
            "with_numbers_123": "withNumbers123",
            "mixed_CASE_test": "mixedCaseTest",
        }

        for input_str, expected_output in test_cases.items():
            with self.subTest(input_str=input_str):
                self.assertEqual(underscore_to_camelcase(input_str), expected_output)
