import logging

from django.http import HttpResponse
from django.template import loader

from .wagtail_api import (
    get_landing_page_global_alert,
    get_landing_page_mourning_notice,
    get_latest_articles,
    get_top_pages,
)

logger = logging.getLogger(__name__)


def index(request):
    template = loader.get_template("main/index.html")
    context = {"foo": "bar"}
    return HttpResponse(template.render(context, request))


def catalogue(request):
    template = loader.get_template("main/catalogue.html")
    
    context = {
        "pages": get_latest_articles()[:3],
        "top_pages": get_top_pages()[:3],
        "global_alert": get_landing_page_global_alert(),
        "mourning_notice": get_landing_page_mourning_notice(),
    }

    return HttpResponse(template.render(context, request))


def cookies(request):
    template = loader.get_template("main/cookies.html")
    context = {"foo": "bar"}
    return HttpResponse(template.render(context, request))