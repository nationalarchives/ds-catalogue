from django.http import QueryDict
from django.test import SimpleTestCase

from app.search.forms import FieldsConstant, MDRSearchForm


def build_form(query_string: str) -> MDRSearchForm:
    """Returns the MDR form bound with the defaults set by the view."""

    data = QueryDict(query_string, mutable=True)
    data.setdefault(FieldsConstant.GROUP, "tna")
    data.setdefault(FieldsConstant.SORT, "")
    data.setdefault(FieldsConstant.DISPLAY, "list")
    return MDRSearchForm(data)


class MDRSearchFormTests(SimpleTestCase):
    def test_search_terms_required(self):
        form = build_form("q=&parish=&county=")

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors,
            {
                FieldsConstant.Q: {
                    "text": "Enter a manor name, parish name or historic county"
                }
            },
        )
        self.assertEqual(
            form.non_field_errors,
            [{"text": "Enter a manor name, parish name or historic county"}],
        )

    def test_any_one_search_term_is_valid(self):
        for query_string in ("q=richmond", "parish=Richmond", "county=Surrey"):
            with self.subTest(query_string=query_string):
                form = build_form(query_string)

                self.assertTrue(form.is_valid())
                self.assertEqual(form.errors, {})

    def test_search_terms_are_cleaned(self):
        form = build_form("q=+richmond+&parish=+Richmond+&county=Surrey")

        self.assertTrue(form.is_valid())
        self.assertEqual(form.fields[FieldsConstant.Q].cleaned, "richmond")
        self.assertEqual(form.fields[FieldsConstant.PARISH].cleaned, "Richmond")
        self.assertEqual(form.fields[FieldsConstant.COUNTY].cleaned, "Surrey")

    def test_invalid_county(self):
        form = build_form("q=richmond&county=Nowhere")

        self.assertFalse(form.is_valid())
        self.assertIn(FieldsConstant.COUNTY, form.errors)

    def test_country_filter(self):
        form = build_form("q=richmond&country=England&country=Wales")

        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.fields[FieldsConstant.COUNTRY].cleaned, ["England", "Wales"]
        )

    def test_invalid_country(self):
        form = build_form("q=richmond&country=France")

        self.assertFalse(form.is_valid())
        self.assertIn(FieldsConstant.COUNTRY, form.errors)

    def test_invalid_date_range(self):
        form = build_form(
            "q=richmond&covering_date_from-year=1900&covering_date_to-year=1800"
        )

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors,
            {
                FieldsConstant.COVERING_DATE_FROM: {
                    "text": "This date must be earlier than or equal to the 'to' date."
                }
            },
        )

    def test_long_filters_not_supported(self):
        form = build_form("q=richmond")

        self.assertNotIn(FieldsConstant.FILTER_LIST, form.fields)
