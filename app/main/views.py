import logging

from app.lib.api import JSONAPIClient
from django.conf import settings
from django.http import HttpResponse
from django.template import loader

logger = logging.getLogger(__name__)


def index(request):
    template = loader.get_template("main/index.html")
    context = {"foo": "bar"}
    return HttpResponse(template.render(context, request))


def catalogue(request):
    template = loader.get_template("main/catalogue.html")
    context = {}

    pages_client = JSONAPIClient(settings.WAGTAIL_API_URL)
    pages_client.add_parameters(
        {
            "child_of": settings.WAGTAIL_EXPLORE_THE_COLLECTION_PAGE_ID,
            "limit": 3,
            "order": "-first_published_at",
        }
    )
    try:
        response_data = pages_client.get("/pages/")
        context["pages"] = response_data.get("items", [])
    except Exception as e:
        logger.error(e)
        context["pages"] = []

    top_pages_client = JSONAPIClient(settings.WAGTAIL_API_URL)
    top_pages_client.add_parameters(
        {
            "child_of": settings.WAGTAIL_HOME_PAGE_ID,
            "limit": 3,
            "order": "-first_published_at",
        }
    )
    try:
        response_data = top_pages_client.get("/pages/")
        context["top_pages"] = response_data.get("items", [])
    except Exception as e:
        logger.error(e)
        context["top_pages"] = []

    return HttpResponse(template.render(context, request))


def cookies(request):
    template = loader.get_template("main/cookies.html")
    context = {"foo": "bar"}
    return HttpResponse(template.render(context, request))
