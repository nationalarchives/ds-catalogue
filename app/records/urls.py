from app.records import views
from django.urls import path

urlpatterns = [
    path(
        r"id/<id>/",
        views.RecordDetailView.as_view(),
        name="details",
    ),
    path(
        r"id/<id>/related/",
        views.RelatedRecordsView.as_view(),
        name="related",
    ),
    path(
        r"id/<id>/help/",
        views.RecordsHelpView.as_view(),
        name="help",
    ),
    # TODO: Implement record_details_by_ref once Rosetta has support
    # path(
    #     r"ref/<path:reference>/",
    #     views.record_detail_by_reference,
    # ),
]
