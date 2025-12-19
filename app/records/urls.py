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
    # Progressive loading API endpoints
    path(
        r"id/<id>/enrichment/subjects/",
        views.RecordSubjectsEnrichmentView.as_view(),
        name="enrichment_subjects",
    ),
    path(
        r"id/<id>/enrichment/related/",
        views.RecordRelatedRecordsView.as_view(),
        name="enrichment_related",
    ),
    path(
        r"id/<id>/enrichment/delivery/",
        views.RecordDeliveryOptionsView.as_view(),
        name="enrichment_delivery",
    ),
    # TODO: Implement record_details_by_ref once Rosetta has support
    # path(
    #     r"ref/<path:reference>/",
    #     views.record_detail_by_reference,
    # ),
]