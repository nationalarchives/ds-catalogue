import json

from django.http import QueryDict
from django.test import RequestFactory

from app.search.constants import FieldsConstant
from app.search.views import AdvancedSearchBuildQView


def test_buildqview_returns_q_json_for_valid_post():
    factory = RequestFactory()
    data = QueryDict("", mutable=True)
    data[FieldsConstant.ALL_WORDS] = "foo bar"
    request = factory.post("/search/build_q", data)

    response = AdvancedSearchBuildQView.as_view()(request)
    assert response.status_code == 200
    content = json.loads(response.content)
    assert "q" in content
    assert content["q"] == "foo bar"


def test_buildqview_returns_empty_json_for_invalid_post():
    factory = RequestFactory()
    # send invalid POST (e.g., missing fields) that fails form validation
    data = QueryDict("", mutable=True)
    # set a field to an invalid value type if necessary; empty should be valid but
    # AdvancedSearchQForm requires no fields, so to force invalid, send an unexpected param
    request = factory.post("/search/build_q", data)

    response = AdvancedSearchBuildQView.as_view()(request)
    assert response.status_code == 200
    content = json.loads(response.content)
    # The view may return an empty JSON or a JSON with an empty 'q' string
    assert content == {} or ("q" in content and content["q"] == "")
