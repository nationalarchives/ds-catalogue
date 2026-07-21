from django.urls import path

from app.main import views

urlpatterns = [
    path("", views.index, name="index"),
    path("catalogue/", views.CatalogueView.as_view(), name="catalogue"),
]
