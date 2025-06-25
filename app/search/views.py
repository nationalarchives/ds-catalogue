import copy
import logging
import math
from typing import Any

from app.errors import views as errors_view
from app.lib.api import ResourceNotFound
from app.lib.pagination import pagination_object
from app.records.constants import CLOSURE_STATUSES, COLLECTIONS, TNA_LEVELS, TNA_SUBJECTS
from app.search.api import search_records
from config.jinja2 import qs_remove_value, qs_toggle_value
from django.http import (
    HttpRequest,
    HttpResponse,
)
from django.views.generic import TemplateView

from .buckets import CATALOGUE_BUCKETS, Bucket, BucketKeys, BucketList
from .constants import Sort
from .forms import CatalogueSearchForm
from .models import APISearchResponse

logger = logging.getLogger(__name__)


class PageNotFound(Exception):
    pass


class APIMixin:
    """A mixin to get the api result, processes api result, sets the context."""

    RESULTS_PER_PAGE = 20  # max records to show per page
    PAGE_LIMIT = 500  # max page number that can be queried

    # fields used to extract aggregation entries from the api result
    dynamic_choice_fields = ["level"]

    def get_api_result(self, query, results_per_page, page, sort, params):
        self.api_result = search_records(
            query=query,
            results_per_page=results_per_page,
            page=page,
            sort=sort,
            params=params,
        )
        return self.api_result

    def get_api_params(self, form, current_bucket: Bucket) -> dict:
        """The API params
        filter: for querying buckets, aggs
        aggs: for checkbox items with counts."""

        def add_filter(params: dict, value):
            if not isinstance(value, list):
                value = [value]
            return params.setdefault("filter", []).extend(value)

        params = {}

        # aggregations
        params.update({"aggs": current_bucket.aggregations})

        # filter records for a bucket
        add_filter(params, f"group:{current_bucket.key}")

        # filter aggregations for each field
        filter_aggregations = []
        for field_name in self.dynamic_choice_fields:
            filter_name = field_name
            selected_values = form.fields[field_name].cleaned
            selected_values = self.replace_input_data(
                field_name, selected_values
            )
            filter_aggregations.extend(
                (f"{filter_name}:{value}" for value in selected_values)
            )
            if filter_aggregations:
                add_filter(params, filter_aggregations)

        return params

    def replace_input_data(self, field_name, selected_values: list[str]):
        """Updates user input/represented data for API querying."""

        # TODO: #LEVEL this is a temporary update until API data switches to Department
        if field_name == "level":
            return [
                "Lettercode" if level == "Department" else level
                for level in selected_values
            ]
        return selected_values

    def process_api_result(
        self, form: CatalogueSearchForm, api_result: APISearchResponse
    ):
        """Update checkbox `choices` values on the form's `dynamic_choice_fields` to
        reflect data included in the API's `aggs` response."""

        for aggregation in api_result.aggregations:
            field_name = aggregation.get("name")
            if field_name in self.dynamic_choice_fields:
                choice_api_data = aggregation.get("entries", ())
                self.replace_api_data(field_name, choice_api_data)
                form.fields[field_name].update_choices(choice_api_data)

    def replace_api_data(
        self, field_name, entries_data: list[dict[str, str | int]]
    ):
        """Update API data for representation purpose."""

        # TODO: #LEVEL this is a temporary update until API data switches to Department
        if field_name == "level":
            for level_entry in entries_data:
                if level_entry.get("value") == "Lettercode":
                    level_entry["value"] = "Department"

    def get_context_data(self, **kwargs):
        context: dict = super().get_context_data(**kwargs)

        results = None
        stats = {"total": None, "results": None}
        if self.api_result:
            results = self.api_result.records
            stats = {
                "total": self.api_result.stats_total,
                "results": self.api_result.stats_results,
            }

        context.update(
            {
                "results": results,
                "stats": stats,
                "subjects": TNA_SUBJECTS,
            }
        )

        return context


class CatalogueSearchFormMixin(APIMixin, TemplateView):
    """A mixin that supports form operations"""

    default_group = BucketKeys.TNA.value
    default_sort = Sort.RELEVANCE.value  # sort includes ordering

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        """Creates the form instance and some attributes"""

        super().setup(request, *args, **kwargs)
        self.form = CatalogueSearchForm(**self.get_form_kwargs())
        self.bucket_list: BucketList = copy.deepcopy(CATALOGUE_BUCKETS)
        self.current_bucket_key = self.form.fields["group"].value
        self.api_result = None

    def get_form_kwargs(self) -> dict[str, Any]:
        """Returns request data with default values if not given."""

        kwargs = {}
        data = self.request.GET.copy()

        # remove param with empty string values to properly set default values ex group v/s required settings
        for key in list(data.keys()):
            if all(value == "" for value in data.getlist(key)):
                del data[key]

        # Add any default values
        for k, v in self.get_defaults().items():
            data.setdefault(k, v)

        kwargs["data"] = data
        return kwargs

    def get_defaults(self):
        """sets default for request"""

        return {
            "group": self.default_group,
            "sort": self.default_sort,
        }

    def get(self, request, *args, **kwargs) -> HttpResponse:
        """
        Overrrides TemplateView.get() to process the form
        For an invalid page renders page not found, otherwise renders the template
        with the form.
        """

        try:
            self.page  # checks valid page
            if self.form.is_valid():
                self.query = self.form.fields["q"].cleaned
                self.sort = self.form.fields["sort"].cleaned
                self.current_bucket = self.bucket_list.get_bucket(
                    self.form.fields["group"].cleaned
                )
                return self.form_valid()
            else:
                return self.form_invalid()
        except PageNotFound:
            # for page=<invalid page number>, page > page limit
            return errors_view.page_not_found_error_view(request=self.request)
        except ResourceNotFound:
            # no results
            return self.form_invalid()
        except Exception as e:
            logger.error(str(e))
            return errors_view.server_error_view(request=request)

    @property
    def page(self) -> int:
        try:
            page = int(self.request.GET.get("page", 1))
            if page < 1:
                raise ValueError
        except (ValueError, KeyError):
            raise PageNotFound
        return page

    def form_valid(self):
        """Gets the api result and processes it after the form and fields
        are cleaned and validated. Renders with form, context."""

        self.api_result = self.get_api_result(
            query=self.query,
            results_per_page=self.RESULTS_PER_PAGE,
            page=self.page,
            sort=self.sort,
            params=self.get_api_params(self.form, self.current_bucket),
        )
        self.process_api_result(self.form, self.api_result)
        context = self.get_context_data(form=self.form)
        return self.render_to_response(context=context)

    def form_invalid(self):
        """Renders invalid form, context."""

        context = self.get_context_data(form=self.form)
        return self.render_to_response(context=context)

    def get_context_data(self, **kwargs):
        context: dict = super().get_context_data(**kwargs)

        results_range = pagination = None
        if self.api_result:
            results_range, pagination = self.paginate_api_result()
            self.bucket_list.update_buckets_for_display(
                query=self.query,
                buckets=self.api_result.buckets,
                current_bucket_key=self.current_bucket_key,
            )
        context.update(
            {
                "bucket_list": self.bucket_list,
                "results_range": results_range,
                "pagination": pagination,
            }
        )
        return context

    def paginate_api_result(self) -> tuple | HttpResponse:

        pages = math.ceil(self.api_result.stats_total / self.RESULTS_PER_PAGE)
        if pages > self.PAGE_LIMIT:
            pages = self.PAGE_LIMIT

        if self.page > pages:
            raise PageNotFound

        results_range = {
            "from": ((self.page - 1) * self.RESULTS_PER_PAGE) + 1,
            "to": ((self.page - 1) * self.RESULTS_PER_PAGE)
            + self.api_result.stats_results,
        }

        pagination = pagination_object(self.page, pages, self.request.GET)

        return (results_range, pagination)


class CatalogueSearchView(CatalogueSearchFormMixin):

    template_name = "search/catalogue.html"

    def get_context_data(self, **kwargs):
        context: dict = super().get_context_data(**kwargs)

        context.update(
            {
                "closure_statuses": CLOSURE_STATUSES,
                "collections": COLLECTIONS,
            }
        )

        if self.api_result:
            self.bucket_list.update_buckets_for_display(
                query=self.query,
                buckets=self.api_result.buckets,
                current_bucket_key=self.current_bucket_key,
            )

        selected_filters = build_selected_filters_list(self.request)

        context.update(
            {
                "bucket_list": self.bucket_list,
                "selected_filters": selected_filters,
                "bucket_keys": BucketKeys,
            }
        )
        return context


# TODO: move into Catalogue Search View when integrating with API
def build_selected_filters_list(request):
    selected_filters = []
    # if request.GET.get("q", None):
    #     selected_filters.append(
    #         {
    #             "label": f"\"{request.GET.get('q')}\"",
    #             "href": f"?{qs_remove_value(request.GET, 'q')}",
    #             "title": f"Remove query: \"{request.GET.get('q')}\"",
    #         }
    #     )
    if request.GET.get("search_within", None):
        selected_filters.append(
            {
                "label": f'Sub query "{request.GET.get("search_within")}"',
                "href": f"?{qs_remove_value(request.GET, 'search_within')}",
                "title": "Remove search within",
            }
        )
    if request.GET.get("date_from", None):
        selected_filters.append(
            {
                "label": f"Record date from: {request.GET.get("date_from")}",
                "href": f"?{qs_remove_value(request.GET, 'date_from')}",
                "title": "Remove record from date",
            }
        )
    if request.GET.get("date_to", None):
        selected_filters.append(
            {
                "label": f"Record date to: {request.GET.get("date_to")}",
                "href": f"?{qs_remove_value(request.GET, 'date_to')}",
                "title": "Remove record to date",
            }
        )
    if levels := request.GET.getlist("level", None):
        levels_lookup = {}
        for _, v in TNA_LEVELS.items():
            levels_lookup.update({v: v})

        for level in levels:
            selected_filters.append(
                {
                    "label": f"Level: {levels_lookup.get(level, level)}",
                    "href": f"?{qs_toggle_value(request.GET, 'level', level)}",
                    "title": f"Remove {levels_lookup.get(level)} level",
                }
            )
    if closure_statuses := request.GET.getlist("closure_status", None):
        for closure_status in closure_statuses:
            selected_filters.append(
                {
                    "label": f"Closure status: {CLOSURE_STATUSES.get(closure_status)}",
                    "href": f"?{qs_toggle_value(request.GET, 'closure_status', closure_status)}",
                    "title": f"Remove {CLOSURE_STATUSES.get(closure_status)} closure status",
                }
            )
    if collections := request.GET.getlist("collections", None):
        for collection in collections:
            selected_filters.append(
                {
                    "label": f"Collection: {COLLECTIONS.get(collection)}",
                    "href": f"?{qs_toggle_value(request.GET, 'collections', collection)}",
                    "title": f"Remove {COLLECTIONS.get(collection)} collection",
                }
            )
    return selected_filters
