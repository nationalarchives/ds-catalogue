from app.records.constants import TNA_SUBJECTS
from app.search.buckets import CATALOGUE_BUCKETS, BucketKeys, Aggregation
from app.search.forms import CatalogueSearchTnaForm, FieldsConstant
from django.http import QueryDict
from django.test import TestCase


class CatalogueSearchFormSubjectsTests(TestCase):
    """Tests for the subjects field in CatalogueSearchTnaForm."""

    def test_subjects_field_exists_in_form(self):
        """Test that subjects field is properly added to the form."""
        form = CatalogueSearchTnaForm()

        self.assertIn(FieldsConstant.SUBJECTS, form.fields)
        self.assertEqual(form.fields[FieldsConstant.SUBJECTS].name, "subjects")
        self.assertEqual(form.fields[FieldsConstant.SUBJECTS].label, "Subjects")

    def test_subjects_field_has_correct_choices(self):
        """Test that subjects field has all TNA_SUBJECTS as choices."""
        form = CatalogueSearchTnaForm()
        subjects_field = form.fields[FieldsConstant.SUBJECTS]

        # Check that configured choices match SUBJECT_CHOICES (which are sorted)
        from app.records.constants import SUBJECT_CHOICES

        expected_choices = (
            SUBJECT_CHOICES  # Keep as tuple, don't convert to list
        )
        self.assertEqual(subjects_field.configured_choices, expected_choices)

        # Check a few specific subjects are present
        choice_values = [
            choice[0] for choice in subjects_field.configured_choices
        ]
        choice_labels = [
            choice[1] for choice in subjects_field.configured_choices
        ]

        self.assertIn("1", choice_values)
        self.assertIn("Armed Forces (General Administration)", choice_labels)
        self.assertIn("2", choice_values)
        self.assertIn("Army", choice_labels)
        self.assertIn("100", choice_values)
        self.assertIn("Disarmament", choice_labels)

    def test_subjects_field_validation_settings(self):
        """Test that subjects field has correct validation settings."""
        form = CatalogueSearchTnaForm()
        subjects_field = form.fields[FieldsConstant.SUBJECTS]

        # Should not validate input since it's set to False
        self.assertFalse(subjects_field.validate_input)
        self.assertFalse(subjects_field.required)

    def test_subjects_field_with_valid_data(self):
        """Test subjects field with valid subject names."""
        # Use QueryDict to properly simulate form data
        form_data = QueryDict(mutable=True)
        form_data.setlist("subjects", ["Army", "Navy", "Air Force"])
        form_data["q"] = "military"
        form_data["group"] = "tna"
        form_data["sort"] = ""

        form = CatalogueSearchTnaForm(data=form_data)
        self.assertTrue(form.is_valid())

        subjects_field = form.fields[FieldsConstant.SUBJECTS]
        self.assertEqual(subjects_field.value, ["Army", "Navy", "Air Force"])
        self.assertEqual(subjects_field.cleaned, ["Army", "Navy", "Air Force"])

    def test_subjects_field_with_empty_data(self):
        """Test subjects field with no subjects selected."""
        # Use QueryDict for form data
        form_data = QueryDict(mutable=True)
        form_data["q"] = "test"
        form_data["group"] = "tna"
        form_data["sort"] = ""

        form = CatalogueSearchTnaForm(data=form_data)
        self.assertTrue(form.is_valid())

        subjects_field = form.fields[FieldsConstant.SUBJECTS]
        self.assertEqual(subjects_field.value, [])
        self.assertEqual(subjects_field.cleaned, [])

    def test_subjects_field_configured_choice_labels(self):
        """Test that configured_choice_labels property works correctly."""
        form = CatalogueSearchTnaForm()
        subjects_field = form.fields[FieldsConstant.SUBJECTS]

        choice_labels = subjects_field.configured_choice_labels

        # Check it's a dictionary mapping ID to label
        self.assertIsInstance(choice_labels, dict)
        self.assertEqual(
            choice_labels["1"], "Armed Forces (General Administration)"
        )
        self.assertEqual(choice_labels["2"], "Army")
        self.assertEqual(choice_labels["6"], "Navy")
        self.assertEqual(choice_labels["18"], "Air Force")
        self.assertEqual(choice_labels["100"], "Disarmament")

    def test_subjects_field_items_property(self):
        """Test the items property for checkbox rendering."""
        # Use QueryDict for form data
        form_data = QueryDict(mutable=True)
        form_data.setlist("subjects", ["2", "6"])  # Use numeric IDs
        form_data["q"] = "military"
        form_data["group"] = "tna"
        form_data["sort"] = ""

        form = CatalogueSearchTnaForm(data=form_data)
        form.is_valid()

        subjects_field = form.fields[FieldsConstant.SUBJECTS]
        items = subjects_field.items

        # Should include all configured choices
        self.assertEqual(len(items), len(TNA_SUBJECTS))

        # Check that selected items are marked as checked
        army_item = next(item for item in items if item["value"] == "2")
        navy_item = next(item for item in items if item["value"] == "6")
        air_force_item = next(item for item in items if item["value"] == "18")

        self.assertEqual(army_item["text"], "Army")  # Note the formatted text
        self.assertEqual(army_item["value"], "2")
        self.assertTrue(army_item["checked"])

        self.assertEqual(navy_item["text"], "Navy")
        self.assertEqual(navy_item["value"], "6")
        self.assertTrue(navy_item["checked"])

        self.assertEqual(air_force_item["text"], "Air Force")
        self.assertEqual(air_force_item["value"], "18")
        self.assertNotIn("checked", air_force_item)

    def test_form_has_correct_number_of_fields(self):
        """Test that the form has the expected number of fields including subjects."""
        form = CatalogueSearchTnaForm()

        # Should have: q, group, sort, level, collection, subjects, online
        self.assertEqual(len(form.fields), 7)

        expected_fields = [
            FieldsConstant.Q,
            FieldsConstant.GROUP,
            FieldsConstant.SORT,
            FieldsConstant.LEVEL,
            FieldsConstant.COLLECTION,
            FieldsConstant.SUBJECTS,
            FieldsConstant.ONLINE,
        ]

        for field_name in expected_fields:
            self.assertIn(field_name, form.fields)
