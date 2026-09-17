from urllib.parse import parse_qs

from django.http import QueryDict

from app.search.buckets import BucketKeys
from app.search.constants import FieldsConstant
from app.search.views import _build_advanced_search_query


def test_repeated_reference_number_and_dates():
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
    assert form.is_valid()

    qs, errors = _build_advanced_search_query(form)
    assert errors == []

    parsed = parse_qs(qs)

    # references should become repeated reference_number params
    assert parsed.get(FieldsConstant.REFERENCE_NUMBER) == ["REF1", "REF2"]

    # date parts should be present as separate params
    assert parsed.get(f"{FieldsConstant.COVERING_DATE_FROM}-year") == ["1990"]
    assert parsed.get(f"{FieldsConstant.COVERING_DATE_FROM}-month") == ["1"]
    assert parsed.get(f"{FieldsConstant.COVERING_DATE_FROM}-day") == ["2"]
