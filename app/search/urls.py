from app.search import views
from django.urls import path

urlpatterns = [
    path("search/", views.CatalogueSearchView.as_view(), name="catalogue"),
    path("advanced-search/", views.advanced_search, name="advanced_search"),
]
