from __future__ import annotations

from typing import Counter as counter


aggregation_mapping = {
    "type": lambda x: min(x),
    "presence_min_fraction": lambda x: ...,
    "presence_min_count": lambda x: ...,
    "domain": lambda x: set().union(*x)
}


def aggregate(attr: str, count: counter, min_size: int) -> str | None:
    agg = None
    size = 0
    most_common = count.most_common()

    while size < min_size:
        val, c = most_common.pop(0)
        agg = aggregation_mapping[attr](agg, val)
        size += c

    return agg