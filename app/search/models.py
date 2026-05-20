from __future__ import annotations

from typing import Any

from django.utils.functional import cached_property

from app.records.models import APIResponse, Record


class APISearchResponse(APIResponse):
    @cached_property
    def records(self) -> list[Record]:
        records = []
        if "data" in self._raw:
            records = [
                Record(record["@template"]["details"])
                for record in self._raw["data"]
                if "@template" in record and "details" in record["@template"]
            ]
        return records

    @cached_property
    def buckets(self) -> dict:
        """
        Returns buckets with record counts {value:count,} Ex: {"tna":26008838,}
        """
        bucket_counts_by_key = {}
        if "buckets" in self._raw:
            bucket_counts = []
            for bucket in self._raw["buckets"]:
                if bucket.get("name", "") == "group":
                    for entry in bucket.get("entries", []):
                        bucket_counts.append(entry)
            # set bucket count with value as key for each bucket
            bucket_counts_by_key = {
                entries["value"]: entries["count"] for entries in bucket_counts
            }

        return bucket_counts_by_key

    @cached_property
    def aggregations(self) -> list[dict[str, Any]]:
        if "aggregations" in self._raw:
            return self._raw["aggregations"]
        return []

    @cached_property
    def stats_total(self) -> int:
        return int(self.get("stats.total", "0"))

    @cached_property
    def stats_results(self) -> int:
        return int(self.get("stats.results", "0"))
