from typing import Any

from app.lib.analytics_mixins import DataLayerMixin
from django.http import HttpRequest


class SearchDataLayerMixin(DataLayerMixin):
    """
    A mixin applied to Search classes to allow them to customise the Analytics
    datalayer.
    """

    content_group: str = "Search the catalogue"

    def get_datalayer_data(self, request: HttpRequest) -> dict[str, Any]:

        data = super().get_datalayer_data(request)

        # update datalayer attributes for search pages
        data["page_type"] = "catalogue_search"

        # Add/Init search specific attributes
        data.update(
            content_source="",
            search_type="",
            search_term="",
            search_total="",  # Use actual number
            search_filters="",  # Count of filters applied (e.g., Collection + Online Only)
        )
        return data
