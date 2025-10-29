from __future__ import annotations

import logging
import re
from typing import Any

import sentry_sdk
from app.lib.xslt_transformations import apply_schema_xsl, apply_series_xsl
from app.records.constants import NON_TNA_LEVELS, SUBJECTS_LIMIT, TNA_LEVELS
from app.records.utils import (
    change_discovery_record_details_links,
    extract,
    format_extref_links,
    format_link,
)
from config.jinja2 import format_number
from django.urls import NoReverseMatch, reverse
from django.utils.functional import cached_property
from lxml import etree

from .constants import MISSING_COUNT_TEXT
from .converters import IDConverter

logger = logging.getLogger(__name__)


class APIModel:
    def __init__(self, raw_data: dict[str, Any]):
        self._raw = raw_data

    def get(self, key: str, default: Any) -> Any:
        """
        Attempts to extract `key` from `self._raw` and return the value.
        """
        if "." in key:
            try:
                return extract(self._raw, key, default)
            except Exception:
                return default
        try:
            return self._raw[key]
        except KeyError:
            return default


class APIResponse(APIModel):
    def __init__(self, raw_data: dict[str, Any]):
        self._raw = raw_data

    @cached_property
    def record(self) -> Record:
        if "@template" in self._raw and "details" in self._raw["@template"]:
            return Record(self._raw["@template"]["details"])
        raise Exception("Record template not found in response")


class Record(APIModel):
    def __init__(self, raw_data: dict[str, Any]):
        self._raw = raw_data

    def __str__(self):
        return f"{self.summary_title} ({self.iaid})"

    @cached_property
    def iaid(self) -> str:
        """
        Return the "iaid" value for this record. If the data is unavailable,
        or is not a valid iaid, a blank string is returned.
        """
        try:
            candidate = self._raw["iaid"]
        except KeyError:
            # value from other places
            candidate = self.get("@admin.id", default="")

        if not candidate:
            # value from other places
            identifiers = self.get("identifier", ())
            for item in identifiers:
                try:
                    candidate = item["iaid"]
                except KeyError:
                    candidate = ""

        if candidate and re.match(IDConverter.regex, candidate):
            # value is not guaranteed to be a valid 'iaid', so we must
            # check it before returning it as one
            return candidate
        return ""

    @cached_property
    def source(self) -> str:
        """Returns the api value of the attr if found, empty str otherwise."""
        return self.get("source", "")

    @cached_property
    def custom_record_type(self) -> str:
        """
        Returns a custom record type.
        TODO: custom record type for identifying CREATORS.
        """
        return self.source

    @cached_property
    def reference_number(self) -> str:
        """Returns the api value of the attr if found, empty str otherwise."""
        if candidate := self.get("referenceNumber", ""):
            return candidate

        # value from other places
        identifiers = self.get("identifier", [])
        for item in identifiers:
            try:
                return item["reference_number"]
            except KeyError:
                pass

        return ""

    @cached_property
    def title(self) -> str:
        """Returns the api value of the attr if found, empty str otherwise."""
        return self.get("title", "")

    @cached_property
    def summary_title(self) -> str:
        """Returns the api value of the attr if found, empty str otherwise."""
        if details_summary_title := self.get("summaryTitle", ""):
            return details_summary_title
        return self.get("summary.title", "")

    @cached_property
    def clean_summary_title(self) -> str:
        """Returns the api value of the attr if found, summary_title str otherwise."""
        return self.get("cleanSummaryTitle", self.summary_title)

    @cached_property
    def date_covering(self) -> str:
        """Returns the api value of the attr if found, empty str otherwise."""
        return self.get("dateCovering", "")

    @cached_property
    def creator(self) -> list[str]:
        """Returns the api value of the attr if found, empty list otherwise."""
        return self.get("creator", [])

    @cached_property
    def dimensions(self) -> str:
        """Returns the api value of the attr if found, empty str otherwise."""
        return self.get("dimensions", "")

    @cached_property
    def former_department_reference(self) -> str:
        """Returns the api value of the attr if found, empty str otherwise."""
        return self.get("formerDepartmentReference", "")

    @cached_property
    def former_pro_reference(self) -> str:
        """Returns the api value of the attr if found, empty str otherwise."""
        return self.get("formerProReference", "")

    @cached_property
    def language(self) -> str:
        """Returns the api value of the attr if found, empty str otherwise."""
        return self.get("language", "")

    @cached_property
    def legal_status(self) -> str:
        """Returns the api value of the attr if found, empty str otherwise."""
        return self.get("legalStatus", "")

    @cached_property
    def level(self) -> str:
        """Returns level name for tna, non tna level codes"""
        if self.is_tna:
            return TNA_LEVELS.get(str(self.level_code), "")
        return NON_TNA_LEVELS.get(str(self.level_code), "")

    @cached_property
    def level_code(self) -> int | None:
        """Returns the api value of the attr if found, None otherwise."""
        return self.get("level.code", None)

    @cached_property
    def map_designation(self) -> str:
        """Returns the api value of the attr if found, empty str otherwise."""
        return self.get("mapDesignation", "")

    @cached_property
    def map_scale(self) -> str:
        """Returns the api value of the attr if found, empty str otherwise."""
        return self.get("mapScale", "")

    @cached_property
    def note(self) -> str:
        """Returns the api value of the attr if found, empty str otherwise."""
        return self.get("note", "")

    @cached_property
    def physical_condition(self) -> str:
        """Returns the api value of the attr if found, empty str otherwise."""
        return self.get("physicalCondition", "")

    @cached_property
    def physical_description(self) -> str:
        """Returns the api value of the attr if found, empty str otherwise."""
        return self.get("physicalDescription", "")

    @cached_property
    def held_by(self) -> str:
        """Returns the api value of the attr if found, empty str otherwise."""
        return self.get("heldBy", "")

    @cached_property
    def held_by_id(self) -> str:
        """Returns the api value of the attr if found, empty str otherwise."""
        return self.get("heldById", "")

    @cached_property
    def held_by_url(self) -> str:
        """Returns url path if the id is found, empty str otherwise."""
        if self.held_by_id:
            # TODO: Temporary link to Discovery until archon template is ready
            return f"https://discovery.nationalarchives.gov.uk/details/a/{self.held_by_id}"
            try:
                return reverse(
                    "records:details",
                    kwargs={"id": self.held_by_id},
                )
            except NoReverseMatch:
                # warning for partially valid record
                logger.warning(
                    f"held_by_url:Record({self.iaid}):No reverse match for record_details with held_by_id={self.held_by_id}"
                )
        return ""

    @cached_property
    def held_by_count(self) -> str:
        """Returns the api value formatted of the attr if found, default text otherwise.
        Usually expected to be present to show in the UI."""

        count = self.get("heldByCount", None)
        if not count:
            # Handles missing value by logging the issue and continuing without user-facing impact.
            message = "held_by_count is missing for the record"
            logger.error(message)
            sentry_sdk.capture_message(message, level="error")
            return MISSING_COUNT_TEXT
        return format_number(count)

    @cached_property
    def access_condition(self) -> str:
        """Returns the api value of the attr if found, empty str otherwise."""
        return self.get("accessCondition", "")

    @cached_property
    def closure_status(self) -> str:
        """Returns the api value of the attr if found, empty str otherwise."""
        return self.get("closureStatus", "")

    @cached_property
    def record_opening(self) -> str:
        """Returns the api value of the attr if found, empty str otherwise."""
        return self.get("recordOpening", "")

    @cached_property
    def accruals(self) -> str:
        """Returns the api value of the attr if found, empty str otherwise."""
        return self.get("accruals", "")

    @cached_property
    def accumulation_dates(self) -> str:
        """Returns the api value of the attr if found, empty str otherwise."""
        return self.get("accumulationDates", "")

    @cached_property
    def appraisal_information(self) -> str:
        """Returns the api value of the attr if found, empty str otherwise."""
        return self.get("appraisalInformation", "")

    @cached_property
    def copies_information(self) -> str:
        """Returns the api value of the attr if found, empty str otherwise."""
        return self.get("copiesInformation", "")

    @cached_property
    def custodial_history(self) -> str:
        """Returns the api value of the attr if found, empty str otherwise."""
        return self.get("custodialHistory", "")

    @cached_property
    def immediate_source_of_acquisition(self) -> str:
        """Returns the api value of the attr if found, empty str otherwise."""
        return self.get("immediateSourceOfAcquisition", "")

    @cached_property
    def location_of_originals(self) -> list[str]:
        """Returns the api value of the attr if found, empty list otherwise."""
        return self.get("locationOfOriginals", [])

    @cached_property
    def restrictions_on_use(self) -> str:
        """Returns the api value of the attr if found, empty str otherwise."""
        return self.get("restrictionsOnUse", "")

    @cached_property
    def administrative_background(self) -> str:
        """Returns the api value of the attr if found, empty str otherwise."""
        return self.get("administrativeBackground", "")

    @cached_property
    def arrangement(self) -> str:
        """Returns the api value of the attr if found, empty str otherwise."""
        return self.get("arrangement", "")

    @cached_property
    def publication_note(self) -> list[str]:
        """Returns the api value of the attr if found, empty list otherwise."""
        return self.get("publicationNote", [])

    @cached_property
    def related_materials(self) -> tuple[dict[str, Any], ...]:
        """Returns transformed data which is a tuple of dict if found, empty tuple otherwise."""
        inc_msg = f"related_materials:Record({self.iaid}):"
        return tuple(
            dict(
                description=item.get("description", ""),
                links=list(
                    format_link(val, inc_msg) for val in item.get("links", ())
                ),
            )
            for item in self.get("relatedMaterials", ())
        )

    @cached_property
    def clean_description(self) -> str:
        """Returns value for cleanDescription if found, empty str otherwise."""
        if clean_description := self.get("cleanDescription", ""):
            return clean_description

    @cached_property
    def short_description(self) -> str:
        """Returns the api value of the attr if found, empty str otherwise."""
        return self.get("description.short", "")

    @cached_property
    def description(self) -> str:
        """Returns the api value of the attr if found, empty str otherwise."""
        if description := self.raw_description:
            description = format_extref_links(description)
            description = apply_schema_xsl(description, self.description_schema)
            description = change_discovery_record_details_links(description)
            return description
        description = self.get("description.value", "")
        if series := self.hierarchy_series:
            description = apply_series_xsl(description, series.reference_number)
        description = format_extref_links(description)
        description = change_discovery_record_details_links(description)
        return description

    @cached_property
    def raw_description(self) -> str:
        """Returns the api value of the attr if found, empty str otherwise."""
        return self.get("description.raw", "")

    @cached_property
    def description_schema(self) -> str:
        if schema := self.get("description.schema", ""):
            colltype = etree.fromstring(schema)
            if colltype_id := colltype.get("id", ""):
                return colltype_id
        return ""

    @cached_property
    def separated_materials(self) -> tuple[dict[str, Any], ...]:
        """Returns transformed data which is a tuple of dict if found, empty tuple otherwise."""
        inc_msg = f"separated_materials:Record({self.iaid}):"
        return tuple(
            dict(
                description=item.get("description", ""),
                links=list(
                    format_link(val, inc_msg) for val in item.get("links", ())
                ),
            )
            for item in self.get("separatedMaterials", ())
        )

    @cached_property
    def unpublished_finding_aids(self) -> list[str]:
        """Returns the api value of the attr if found, empty list otherwise."""
        return self.get("unpublishedFindingAids", [])

    @cached_property
    def hierarchy(self) -> tuple[Record, ...]:
        """Returns tuple of records transformed from the values of the attr if found, empty tuple otherwise."""
        hierarchy_records = ()
        for hierarchy_item in self.get("@hierarchy", ()):
            if hierarchy_item.get("identifier"):
                # page_record_is_tna: carry status to hierarchy record
                hierarchy_record = Record(
                    hierarchy_item | {"page_record_is_tna": self.is_tna}
                )
                # skips current record from showing in hierarchy bar
                if self.iaid == hierarchy_record.iaid:
                    continue
                hierarchy_records += (hierarchy_record,)

        return hierarchy_records

    @cached_property
    def hierarchy_count(self) -> str:
        """Returns the formatted count usually found in record of the hierarchy
        records i.e. @hierarchy, default text otherwise.
        Usually expected to be present to show in the UI."""

        count = self.get("count", None)
        if not count:
            # Handles missing value by logging the issue and continuing without user-facing impact.
            message = "hierarchy_count missing for hierarchy record"
            logger.error(message)
            sentry_sdk.capture_message(message, level="error")
            # add context for debugging in Sentry
            sentry_sdk.set_context(
                "missing_info", {"hierarchy_record_id": {self.iaid}}
            )
            return MISSING_COUNT_TEXT
        return format_number(count)

    @cached_property
    def next(self) -> Record | None:
        """Returns a record transformed from the values of the attr if found, None otherwise."""
        if next := self.get("@next", None):
            # page_record_is_tna: carry status to next record
            return Record(next | {"page_record_is_tna": self.is_tna})
        return None

    @cached_property
    def previous(self) -> Record | None:
        """Returns a record transformed from the values of the attr if found, None otherwise."""
        if previous := self.get("@previous", None):
            # page_record_is_tna: carry status to previous record
            return Record(previous | {"page_record_is_tna": self.is_tna})
        return None

    @cached_property
    def parent(self) -> Record | None:
        """Returns a record transformed from the values of the attr if found, None otherwise."""
        if parent := self.get("parent", None):
            # page_record_is_tna: carry status to parent record
            return Record(parent | {"page_record_is_tna": self.is_tna})
        return None

    @cached_property
    def is_tna(self) -> bool:
        """Returns True if record belongs to TNA, False otherwise."""
        # checks if page attribute if present, so that same is_tna
        # is used for the created record
        if is_tna := self.get("page_record_is_tna", ""):
            return is_tna

        for item in self.get("groupArray", []):
            if item.get("value", "") == "tna":
                return True
        return False

    @cached_property
    def is_digitised(self) -> bool:
        """Returns True if digitised, False otherwise."""
        return self.get("digitised", False)

    @cached_property
    def url(self) -> str:
        """Returns record detail url for iaid, empty str otherwise."""
        if self.iaid:
            try:
                return reverse("records:details", kwargs={"id": self.iaid})
            except NoReverseMatch:
                pass
        return ""

    @cached_property
    def breadcrumb_items(self) -> list:
        """Returns breadcrumb items depending on position in hierarchy
        Update tna_breadcrumb_levels or oa_breadcrumb_levels to change the levels displayed
        """
        items = []
        tna_breadcrumb_levels = [1, 2, 3]
        oa_breadcrumb_levels = [1, 2, 5]

        for hierarchy_record in self.hierarchy:
            if hierarchy_record.level_code != self.level_code:
                if self.is_tna:
                    if hierarchy_record.level_code in tna_breadcrumb_levels:
                        items.append(hierarchy_record)
                else:
                    if hierarchy_record.level_code in oa_breadcrumb_levels:
                        items.append(hierarchy_record)
        items.append(self)

        if len(items) > 3:
            items = items[-3:]

        return items

    @cached_property
    def hierarchy_series(self) -> Record | None:
        """Returns series record from hierarchy if found, None otherwise"""
        for item in self.hierarchy:
            if item.level == "Series":
                return item
        return None

    @cached_property
    def subjects(self) -> list[str]:
        """Returns up to SUBJECTS_LIMIT items from the api value of the attr if found, empty list otherwise."""
        return self.get("subjects", [])[:SUBJECTS_LIMIT]

    # Add to your Record class in app/records/models.py
    @property
    def subjects_enrichment(self) -> dict:
        """Returns subjects enrichment data if available."""
        return getattr(self, "_subjects_enrichment", {})

    @property
    def has_subjects_enrichment(self) -> bool:
        """Check if this record has enrichment data available."""
        return bool(self.subjects_enrichment)
