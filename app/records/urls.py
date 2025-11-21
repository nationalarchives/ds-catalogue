from app.records import api_views, views
from django.urls import path

api_urlpatterns = [
    # Progressive loading API endpoints
    path(
        "api/records/<str:record_id>/delivery-options/",
        api_views.delivery_options_api,
        name="api_delivery_options",
    ),
    path(
        "api/records/<str:record_id>/related/",
        api_views.related_records_api,
        name="api_related_records",
    ),
    path(
        "api/records/<str:record_id>/subjects-enrichment/",
        api_views.subjects_enrichment_api,
        name="api_subjects_enrichment",
    ),
    path(
        "api/records/<str:record_id>/available-online/",
        api_views.available_online_api,
        name="api_available_online",
    ),
    path(
        "api/records/<str:record_id>/available-in-person/",
        api_views.available_in_person_api,
        name="api_available_in_person",
    ),
]

urlpatterns = [
    path(
        r"id/<id:id>/",
        views.RecordDetailView.as_view(),
        name="details",
    ),
    path(
        r"id/<id:id>/related/",
        views.RelatedRecordsView.as_view(),
        name="related",
    ),
    path(
        r"id/<id:id>/help/",
        views.RecordsHelpView.as_view(),
        name="help",
    ),
    # TODO: Implement record_details_by_ref once Rosetta has support
    # path(
    #     r"ref/<path:reference>/",
    #     views.record_detail_by_reference,
    # ),
] + api_urlpatterns
