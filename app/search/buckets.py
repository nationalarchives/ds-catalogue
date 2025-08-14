import copy
from dataclasses import dataclass, field
from enum import StrEnum

from django.contrib.humanize.templatetags.humanize import intcomma


class Aggregation(StrEnum):
    """Aggregated counts to include with response.

    Supported by /search endpoint.
    """

    LEVEL = "level"
    COLLECTION = "collection"


@dataclass
class Bucket:
    """
    A structured model that holds information that is made available in the templates
    for the user to explore.
    Ex TNA-Records at the National Archives
    """

    key: str
    label: str
    description: str
    href: str = "#"
    record_count: int = 0
    is_current: bool = False

    aggregations: list[str] = field(default_factory=lambda: [])

    @property
    def label_with_count(self) -> str:
        if self.record_count is None:
            return self.label
        return self.label + f" ({intcomma(self.record_count)})"

    @property
    def item(self) -> dict[str, str | bool]:
        """
        Returns data formatted for front-end component Ex: tnaSecondaryNavigation()
        """
        return {
            "name": self.label_with_count,
            "href": self.href,
            "current": self.is_current,
        }


class BucketKeys(StrEnum):
    """
    Keys which represent API data that can be queried.
    """

    TNA = "tna"
    DIGITISED = "digitised"
    NONTNA = "nonTna"


@dataclass
class BucketList:
    buckets: list[Bucket]

    def __iter__(self):
        yield from self.buckets

    def get_bucket(self, key):
        for bucket in self.buckets:
            if bucket.key == key:
                return bucket
        raise KeyError(f"Bucket matching the key '{key}' could not be found")

    def update_buckets_for_display(
        self, query: str | None, buckets: dict, current_bucket_key: str | None
    ):
        """update buckets data used by bucket.item for the FE component"""

        for bucket in self.buckets:
            bucket.record_count = buckets.get(bucket.key, 0)
            bucket.is_current = bucket.key == current_bucket_key
            bucket.href = f"?group={bucket.key}"
            if query:
                bucket.href += f"&q={query}"

    def as_choices(self) -> list[tuple[str, str]]:
        return [(bucket.key, bucket.label) for bucket in self.buckets]

    @property
    def items(self):
        """Returns list of bucket items t to be used by
        front-end component Ex: tnaSecondaryNavigation()"""

        return [bucket.item for bucket in self.buckets]


# Configure list of buckets to show in template, these values rarely change
CATALOGUE_BUCKETS = BucketList(
    [
        Bucket(
            key=BucketKeys.TNA.value,
            label="Records at the National Archives",
            description="Results for records held at The National Archives that match your search term.",
            aggregations=[
                Aggregation.LEVEL.value,
                Aggregation.COLLECTION.value,
            ],
        ),
        Bucket(
            key=BucketKeys.NONTNA.value,
            label="Records at other UK archives",
            description="Results for records held at other archives in the UK (and not at The National Archives) that match your search term.",
        ),
    ]
)
