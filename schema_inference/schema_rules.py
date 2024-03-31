from __future__ import annotations

from typing import Counter as counter



aggregation_mapping = {
    "type": lambda x: max([elem for elem in x if elem]),
    "domain": lambda x: list(set().union(*[elem for elem in x if elem]))
}


def aggregate_presence_min_fraction(c: int | None, min_size: int) -> float:
    return 1.0 if c and c >= min_size else None


def aggregate_presence_min_count(c: int | None, min_size: int) -> int:
    return 1 if c and c >= min_size else 0


def aggregate(attr: str, count: counter, min_size: int) -> str | list | None:
    agg = None
    size = 0
    most_common = count.most_common()

    while size < min_size and most_common:
        val, c = most_common.pop(0)
        agg = aggregation_mapping[attr]([agg, val])
        size += c

    return agg
