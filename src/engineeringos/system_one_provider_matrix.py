#!/usr/bin/env python3
from __future__ import annotations

import json
import statistics

from state_paths import runtime
from system_one_observations import atomic_json


STATE = runtime()


def _median_latency(projection: dict) -> float | None:
    values = [
        float(row["latency_ms"])
        for row in projection.get("items", [])
        if row.get("latency_ms") is not None
    ]
    return statistics.median(values) if values else None


def compare(primary: dict, candidate: dict) -> dict:
    p = {row.get("item_id"): row for row in primary.get("items", [])}
    c = {row.get("item_id"): row for row in candidate.get("items", [])}
    common = sorted(set(p) & set(c))
    agreements = [
        item_id
        for item_id in common
        if p[item_id].get("processing_lane_recommendation")
        == c[item_id].get("processing_lane_recommendation")
    ]
    disagreements = [
        {
            "item_id": item_id,
            "kind": p[item_id].get("kind") or c[item_id].get("kind"),
            "primary": p[item_id].get("processing_lane_recommendation"),
            "candidate": c[item_id].get("processing_lane_recommendation"),
        }
        for item_id in common
        if item_id not in agreements
    ]
    return {
        "schema_version": 1,
        "primary_provider": primary.get("provider"),
        "candidate_id": candidate.get("candidate_id"),
        "candidate_provider": candidate.get("provider"),
        "primary_status": primary.get("status"),
        "candidate_status": candidate.get("status"),
        "items_compared": len(common),
        "provider_agreement_rate": (
            len(agreements) / len(common)
            if common
            else None
        ),
        "disagreements": disagreements,
        "primary_median_latency_ms": _median_latency(primary),
        "candidate_median_latency_ms": _median_latency(candidate),
        "candidate_influence_routing": False,
        "authorization": "UNAVAILABLE",
    }


def run() -> dict:
    primary_path = STATE / "system-one/projection.json"
    candidate_path = STATE / "system-one/candidates/decis-kev-0.8b.json"
    output = STATE / "system-one/provider-matrix.json"

    if not primary_path.exists() or not candidate_path.exists():
        result = {
            "schema_version": 1,
            "items_compared": 0,
            "provider_agreement_rate": None,
            "candidate_influence_routing": False,
            "authorization": "UNAVAILABLE",
        }
    else:
        result = compare(
            json.loads(primary_path.read_text()),
            json.loads(candidate_path.read_text()),
        )
    atomic_json(output, result)
    return result


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))
