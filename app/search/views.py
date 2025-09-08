import copy
import logging
import math
from typing import Any

from app.errors import views as errors_view
from app.lib.api import JSONAPIClient, ResourceNotFound
from app.lib.pagination import pagination_object
from app.records.constants import (
    CLOSURE_STATUSES,
    TNA_LEVELS,
    TNA_SUBJECTS,
)
from app.search.api import search_records
from config.jinja2 import qs_remove_value, qs_toggle_value
from django.conf import settings
from django.http import (
    HttpRequest,
    HttpResponse,
    QueryDict,
)
from django.views.generic import TemplateView

from .buckets import CATALOGUE_BUCKETS, Bucket, BucketKeys, BucketList
from .constants import (
    FILTER_DATATYPE_RECORD,
    PAGE_LIMIT,
    RESULTS_PER_PAGE,
    Sort,
)
from .forms import CatalogueSearchForm, FieldsConstant
from .models import APISearchResponse

logger = logging.getLogger(__name__)


class PageNotFound(Exception):
    pass


class APIMixin:
    """A mixin to get the api result, processes api result, sets the context."""

    # fields used to extract aggregation entries from the api result
    dynamic_choice_fields = [FieldsConstant.LEVEL, FieldsConstant.COLLECTION]

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

        # applies to catalogue records to filter records with iaid in the results
        if current_bucket.key == BucketKeys.NONTNA.value:
            add_filter(params, FILTER_DATATYPE_RECORD)

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

        if form.fields[FieldsConstant.ONLINE].cleaned == "true":
            add_filter(params, "digitised:true")

        date_params = form.get_api_date_params()
        params.update(date_params)

        return params

    def replace_input_data(self, field_name, selected_values: list[str]):
        """Updates user input/represented data for API querying."""

        # TODO: #LEVEL this is a temporary update until API data switches to Department
        if field_name == FieldsConstant.LEVEL:
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
                form.fields[field_name].update_choices(
                    choice_api_data, form.fields[field_name].value
                )

    def replace_api_data(
        self, field_name, entries_data: list[dict[str, str | int]]
    ):
        """Update API data for representation purpose."""

        # TODO: #LEVEL this is a temporary update until API data switches to Department
        if field_name == FieldsConstant.LEVEL:
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
        self.current_bucket_key = self.form.fields[FieldsConstant.GROUP].value
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
            FieldsConstant.GROUP: self.default_group,
            FieldsConstant.SORT: self.default_sort,
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
                self.query = self.form.fields[FieldsConstant.Q].cleaned
                self.sort = self.form.fields[FieldsConstant.SORT].cleaned
                self.current_bucket = self.bucket_list.get_bucket(
                    self.form.fields[FieldsConstant.GROUP].cleaned
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
            results_per_page=RESULTS_PER_PAGE,
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

        pages = math.ceil(self.api_result.stats_total / RESULTS_PER_PAGE)
        if pages > PAGE_LIMIT:
            pages = PAGE_LIMIT

        if self.page > pages:
            raise PageNotFound

        results_range = {
            "from": ((self.page - 1) * RESULTS_PER_PAGE) + 1,
            "to": ((self.page - 1) * RESULTS_PER_PAGE)
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
            }
        )

        if self.api_result:
            self.bucket_list.update_buckets_for_display(
                query=self.query,
                buckets=self.api_result.buckets,
                current_bucket_key=self.current_bucket_key,
            )

        selected_filters = self.build_selected_filters_list()

        global_alerts_client = JSONAPIClient(settings.WAGTAIL_API_URL)
        global_alerts_client.add_parameters(
            {"fields": "_,global_alert,mourning_notice"}
        )
        try:
            context["global_alert"] = global_alerts_client.get(
                f"/pages/{settings.WAGTAIL_HOME_PAGE_ID}"
            )
        except Exception as e:
            logger.error(e)
            context["global_alert"] = {}

        context.update(
            {
                "bucket_list": self.bucket_list,
                "selected_filters": selected_filters,
                "bucket_keys": BucketKeys,
            }
        )
        return context

    def build_selected_filters_list(self):
        """Build a list of selected filters with their labels and removal URLs."""
        selected_filters = []

        # Add each type of filter
        selected_filters.extend(self._add_search_within_filter())
        selected_filters.extend(self._add_online_filter())
        selected_filters.extend(self._add_date_filters())
        selected_filters.extend(self._add_level_filters())
        selected_filters.extend(self._add_closure_status_filters())
        selected_filters.extend(self._add_collection_filters())

        return selected_filters

    def _add_search_within_filter(self):
        """Add search within filter if present."""
        filters = []
        search_within = self.request.GET.get("search_within")
        if search_within:
            filters.append(
                {
                    "label": f"Sub query {search_within}",
                    "href": f"?{qs_remove_value(self.request.GET, 'search_within')}",
                    "title": "Remove search within",
                }
            )
        return filters

    def _add_online_filter(self):
        """Add online filter if present."""
        filters = []
        online = self.request.GET.get("online")
        if online:
            filters.append(
                {
                    "label": "Online only",
                    "href": f"?{qs_remove_value(self.request.GET, 'online')}",
                    "title": "Remove online only",
                }
            )
        return filters

    def _add_date_filters(self):
        """Add all date-related filters."""
        filters = []

        # Record date filters
        filters.extend(self._add_record_date_filters())
        # Opening date filters
        filters.extend(self._add_opening_date_filters())

        return filters

    def _add_record_date_filters(self):
        """Add record date from/to filters."""
        filters = []

        rd_from = self.form.fields[FieldsConstant.RECORD_DATE_FROM].cleaned
        if rd_from:
            formatted_date = rd_from.strftime("%d %B %Y")
            filters.append(
                {
                    "label": f"Record date from: {formatted_date}",
                    "href": f"?{self._remove_date_params(self.request.GET, 'rd_from')}",
                    "title": "Remove record from date",
                }
            )

        rd_to = self.form.fields[FieldsConstant.RECORD_DATE_TO].cleaned
        if rd_to:
            formatted_date = rd_to.strftime("%d %B %Y")
            filters.append(
                {
                    "label": f"Record date to: {formatted_date}",
                    "href": f"?{self._remove_date_params(self.request.GET, 'rd_to')}",
                    "title": "Remove record to date",
                }
            )

        return filters

    def _add_opening_date_filters(self):
        """Add opening date from/to filters."""
        filters = []

        od_from = self.form.fields[FieldsConstant.OPENING_DATE_FROM].cleaned
        if od_from:
            formatted_date = od_from.strftime("%d %B %Y")
            filters.append(
                {
                    "label": f"Opening date from: {formatted_date}",
                    "href": f"?{self._remove_date_params(self.request.GET, 'od_from')}",
                    "title": "Remove opening from date",
                }
            )

        od_to = self.form.fields[FieldsConstant.OPENING_DATE_TO].cleaned
        if od_to:
            formatted_date = od_to.strftime("%d %B %Y")
            filters.append(
                {
                    "label": f"Opening date to: {formatted_date}",
                    "href": f"?{self._remove_date_params(self.request.GET, 'od_to')}",
                    "title": "Remove opening to date",
                }
            )

        return filters

    def _add_level_filters(self):
        """Add level filters."""
        filters = []
        levels = self.form.fields[FieldsConstant.LEVEL].value

        if levels:
            levels_lookup = {v: v for _, v in TNA_LEVELS.items()}

            for level in levels:
                level_label = levels_lookup.get(level, level)
                filters.append(
                    {
                        "label": f"Level: {level_label}",
                        "href": f"?{qs_toggle_value(self.request.GET, 'level', level)}",
                        "title": f"Remove {level_label} level",
                    }
                )

        return filters

    def _add_closure_status_filters(self):
        """Add closure status filters."""
        filters = []
        closure_statuses = self.request.GET.getlist("closure_status")

        for closure_status in closure_statuses:
            status_label = CLOSURE_STATUSES.get(closure_status)
            filters.append(
                {
                    "label": f"Closure status: {status_label}",
                    "href": f"?{qs_toggle_value(self.request.GET, 'closure_status', closure_status)}",
                    "title": f"Remove {status_label} closure status",
                }
            )

        return filters

    def _add_collection_filters(self):
        """Add collection filters."""
        filters = []
        collections = self.form.fields[FieldsConstant.COLLECTION].value

        if collections:
            choice_labels = self.form.fields[
                FieldsConstant.COLLECTION
            ].configured_choice_labels

            for collection in collections:
                collection_label = choice_labels.get(collection, collection)
                filters.append(
                    {
                        "label": f"Collection: {collection_label}",
                        "href": f"?{qs_toggle_value(self.request.GET, 'collection', collection)}",
                        "title": f"Remove {collection_label} collection",
                    }
                )

        return filters

    def _remove_date_params(self, query_dict, date_field_prefix):
        """Helper method to remove all date component parameters for a given date field"""
        # Create a mutable copy
        new_qs = query_dict.copy()

        # Remove all three components for this date field
        for suffix in ["-year", "-month", "-day"]:
            param_name = f"{date_field_prefix}{suffix}"
            if param_name in new_qs:
                del new_qs[param_name]

        return new_qs.urlencode()
