"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from urllib.parse import urljoin

from app.errors.views import page_not_found_error_view, server_error_view
from app.records import converters
from django.apps import apps
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import include, path, re_path, register_converter
from django.utils.http import url_has_allowed_host_and_scheme

register_converter(converters.IDConverter, "id")

handler404 = "app.errors.views.page_not_found_error_view"


# ==========================================
# beta.nationalarchives.gov.uk redirects
# ------------------------------------------
# When this service is hosted using the beta
# subdomain it will have to handle redirects
# for any content that used to be accessible
# through the subdomain, and forward them on
# to the live site.
# These routes should be removed after about
# 6 months, at the start of December 2025.
# ==========================================
def redirect_to_live_site(request):
    allowed_paths = [
        "/explore-the-collection/",
        "/people/",
    ]
    if any(request.path.startswith(path) for path in allowed_paths):
        new_url = urljoin("https://www.nationalarchives.gov.uk", request.path)
        return HttpResponseRedirect(new_url)
    return HttpResponseRedirect("https://www.nationalarchives.gov.uk")


old_beta_site_redirect_urls = [
    re_path(r"^explore-the-collection/.*$", redirect_to_live_site),
    re_path(r"^people/.*$", redirect_to_live_site),
]
# ==========================================
# END beta.nationalarchives.gov.uk redirects
# ==========================================

urlpatterns = (
    [
        path("", include(("app.main.urls", "main"), namespace="main")),
        path("healthcheck/", include("app.healthcheck.urls")),
        path(
            "catalogue/",
            include(("app.search.urls", "search"), namespace="search"),
        ),
        path(
            "catalogue/",
            include(("app.records.urls", "records"), namespace="records"),
        ),
        path(
            "404/",
            page_not_found_error_view,
        ),
        path("admin/", admin.site.urls),
    ]
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + old_beta_site_redirect_urls
)

if apps.is_installed("debug_toolbar"):
    urlpatterns = [
        path("__debug__/", include("debug_toolbar.urls")),
    ] + urlpatterns

if settings.DEBUG:
    urlpatterns += [
        path(
            "500/",
            server_error_view,
        )
    ]
