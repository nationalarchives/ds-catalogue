from django.test import TestCase

from app.search.views import APIMixin


class APIMixinReplaceMethodsTests(TestCase):

    def setUp(self):
        self.apimixin = APIMixin()

    def test_replace_input_data_level_field_name(self):

        self.field_name = "level"
        self.selected_values = ["Division", "Department"]
        self.selected_values = self.apimixin.replace_input_data(
            self.field_name, self.selected_values
        )
        self.assertEqual(self.selected_values, ["Division", "Lettercode"])

    def test_replace_api_data_level_field_name(self):

        self.field_name = "level"
        self.entries_data = [
            {"value": "Division", "doc_count": 1215},
            {"value": "Lettercode", "doc_count": 435},
        ]

        self.apimixin.replace_api_data(self.field_name, self.entries_data)
        self.assertEqual(
            self.entries_data,
            [
                {"value": "Division", "doc_count": 1215},
                {"value": "Department", "doc_count": 435},
            ],
        )
