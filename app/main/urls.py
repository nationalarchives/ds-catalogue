from app.main import views
from django.urls import path

urlpatterns = [
    path("", views.index, name="index"),
    path("catalogue/", views.catalogue, name="catalogue"),
]
