from django.urls import path

from app.search import views

urlpatterns = [
    path("search/", views.CatalogueSearchView.as_view(), name="catalogue"),
]
