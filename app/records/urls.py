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
    # Progressive loading fragment endpoints
    path(
        r"id/<id>/fragments/delivery-options/",
        views.DeliveryOptionsFragmentView.as_view(),
        name="fragment_delivery_options",
    ),
    path(
        r"id/<id>/fragments/related-records/",
        views.RelatedRecordsFragmentView.as_view(),
        name="fragment_related_records",
    ),
    path(
        r"id/<id>/fragments/subjects-enrichment/",
        views.SubjectsEnrichmentFragmentView.as_view(),
        name="fragment_subjects_enrichment",
    ),
    # TODO: Implement record_details_by_ref once Rosetta has support
    # path(
    #     r"ref/<path:reference>/",
    #     views.record_detail_by_reference,
    # ),
]
