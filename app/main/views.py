import logging

from django.http import HttpResponse
from django.template import loader
from django.views.generic import TemplateView

from app.main.api import (
    fetch_global_notifications,
    get_explore_the_collection,
)

from .cache import get_subjects_grouped_by_letter

logger = logging.getLogger(__name__)


def index(request):
    template = loader.get_template("main/index.html")
    context = {"foo": "bar"}
    return HttpResponse(template.render(context, request))


class CatalogueView(TemplateView):
    template_name = "main/catalogue.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        explore = get_explore_the_collection()
        notifications = fetch_global_notifications()

        # context for the subjects picker
        subjects_grouped_by_letter = get_subjects_grouped_by_letter()
        disabled_letters = [
            letter
            for letter, subjects in subjects_grouped_by_letter.items()
            if not subjects
        ]

        context.update(
            {
                "latest_articles": explore.get("latest_articles", [])[:3],
                "top_pages": explore.get("top_pages", [])[:3],
                "global_alert": (
                    notifications.get("global_alert") if notifications else None
                ),
                "mourning_notice": (
                    notifications.get("mourning_notice") if notifications else None
                ),
                "disabled_letters": disabled_letters,
                "subjects_grouped_by_letter": subjects_grouped_by_letter,
            }
        )

        return context
