from dataclasses import dataclass, field
from enum import Enum, StrEnum

from django.contrib.humanize.templatetags.humanize import intcomma

from .constants import FieldsConstant


class MultiValueForAggregation(Enum):
    def __new__(cls, field_name: str, api_aggs: tuple[str, str]):
        """Allows each enum member to have multiple values.
        field_name: name of the field in Form
        api_aggs: tuple of (aggs, long_aggs)
        aggs: value used to request aggregation from API
        long_aggs: value used to request extended aggregation from API"""

        obj = object.__new__(cls)
        obj._value_ = field_name  # Primary value used by Enum
        obj.field_name = field_name
        obj.aggs = api_aggs[0]
        obj.long_aggs = api_aggs[1]
        return obj


class Aggregation(MultiValueForAggregation):
    """Aggregated counts to include with response.
    Enum value format tuple of (field_name, (api aggs, api long_aggs))
    When long_aggs is empty string, long aggregation is not supported.

    Supported by /search endpoint.

    Example:
        HELD_BY = ("held_by", ("heldBy", "longHeldBy"))
        means HELD_BY aggregation uses "held_by" as forms field name,
        "heldBy" as aggs value, "longHeldBy" as long_aggs value.

    Note: Keep Aggregation members name in sync with FieldsConstant
          names (HELD_BY member uses FieldsConstant.HELD_BY as forms
          field name).
    """

    LEVEL = (FieldsConstant.LEVEL, ("level", ""))
    COLLECTION = (FieldsConstant.COLLECTION, ("collection", "longCollection"))
    HELD_BY = (FieldsConstant.HELD_BY, ("heldBy", "longHeldBy"))
    CLOSURE = (FieldsConstant.CLOSURE, ("closure", ""))
    SUBJECT = (FieldsConstant.SUBJECT, ("subject", "longSubject"))

    def as_input_choices() -> list[tuple[str, str]]:
        """Returns list of (long_aggs, forms field_name) tuples for all enum members
        that support long aggregation.
        Example:
            [("longHeldBy", "held_by"),...]
        """

        long_aggs_list = [("", "No filter")]  # Default no filter choice
        for agg in Aggregation:
            if agg.long_aggs:
                long_aggs_list.append((agg.long_aggs, agg.field_name))
        return long_aggs_list


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
    NON_TNA = "nonTna"


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
                Aggregation.LEVEL.aggs,
                Aggregation.COLLECTION.aggs,
                Aggregation.CLOSURE.aggs,
                Aggregation.SUBJECT.aggs,
            ],
        ),
        Bucket(
            key=BucketKeys.NON_TNA.value,
            label="Records at other UK archives",
            description="Results for records held at other archives in the UK (and not at The National Archives) that match your search term.",
            aggregations=[
                Aggregation.HELD_BY.aggs,
            ],
        ),
    ]
)
