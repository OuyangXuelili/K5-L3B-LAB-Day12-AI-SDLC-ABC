"""Độ tươi nội bộ dùng số hữu tỉ để xét ngưỡng và chốt giá chính xác."""
from fractions import Fraction
import math

from ..ids import sort_by_id


def load_individuals(items):
    return [{"id": item["id"], "kind": item["kind"], "fresh": Fraction(str(item["fresh"]))}
            for item in items]


def tick_decay(config, phase, tick_hz):
    return Fraction(str(config[f"{phase}_decay_per_s"])) / tick_hz


def age_items(items, decay, cutoff, location, events):
    crossed = []
    for item in items:
        previous = item["fresh"]
        if previous > 0:
            item["fresh"] = max(0, previous - decay)
            if item["fresh"] < cutoff <= previous:
                crossed.append(item)
    for item in sort_by_id(crossed):
        events.append(("spoiled", {"item_id": item["id"], "kind": item["kind"], "location": location}))
    return {item["id"] for item in crossed}


def export_items(items, cutoff):
    output = []
    for item in items:
        exact = item["fresh"]
        fresh = float(exact)
        if exact < cutoff <= fresh:
            fresh = math.nextafter(fresh, -math.inf)
        output.append({"id": item["id"], "kind": item["kind"], "fresh": fresh})
    return output
