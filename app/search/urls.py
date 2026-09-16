from django.urls import path

from app.search import views

urlpatterns = [
    path("search/", views.CatalogueSearchView.as_view(), name="catalogue"),
    path("advanced-search/", views.advanced_search, name="advanced_search"),
    path(
        "advanced-search-js/",
        views.advanced_search_js,
        name="advanced_search_js",
    ),
]
