from urllib.parse import parse_qs

from django.http import QueryDict
from django.test import SimpleTestCase

from app.search.buckets import BucketKeys
from app.search.constants import FieldsConstant
from app.search.views import _build_advanced_search_query


class AdvancedSearchQueryParamsTests(SimpleTestCase):
    def test_repeated_reference_number_and_dates(self):
        qd = QueryDict("", mutable=True)
        qd[FieldsConstant.GROUP] = BucketKeys.TNA.value
        # references entered as multiline input
        qd[FieldsConstant.REFERENCES] = "REF1\nREF2"

        # set covering date from as Y/M/D parts
        qd[f"{FieldsConstant.COVERING_DATE_FROM}-year"] = "1990"
        qd[f"{FieldsConstant.COVERING_DATE_FROM}-month"] = "1"
        qd[f"{FieldsConstant.COVERING_DATE_FROM}-day"] = "2"

        from app.search.forms import AdvancedSearchForm

        form = AdvancedSearchForm(data=qd)
        self.assertTrue(form.is_valid())

        qs, errors = _build_advanced_search_query(form)
        self.assertEqual(errors, [])

        parsed = parse_qs(qs)

        # references should become repeated reference_number params
        self.assertEqual(parsed.get(FieldsConstant.REFERENCE_NUMBER), ["REF1", "REF2"])

        # date parts should be present as separate params
        self.assertEqual(parsed.get(f"{FieldsConstant.COVERING_DATE_FROM}-year"), ["1990"])
        self.assertEqual(parsed.get(f"{FieldsConstant.COVERING_DATE_FROM}-month"), ["1"])
        self.assertEqual(parsed.get(f"{FieldsConstant.COVERING_DATE_FROM}-day"), ["2"])
