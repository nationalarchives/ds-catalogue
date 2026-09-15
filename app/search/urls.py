from django.urls import path

from app.search import views

urlpatterns = [
    path("search/", views.CatalogueSearchView.as_view(), name="catalogue"),
    path(
        "advanced-search/", views.AdvancedSearchView.as_view(), name="advanced_search"
    ),
    path(
        "advanced-search/build-q/",
        views.AdvancedSearchBuildQView.as_view(),
        name="advanced_search_build_q",
    ),
]
