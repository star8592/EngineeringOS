#!/usr/bin/env python3
from __future__ import annotations

import json

from state_paths import runtime
from system_one_observations import (
    append_once,
    atomic_json,
    make_observation,
    read_jsonl,
    summarize,
)


STATE = runtime()
CANDIDATE_ID = "decis-kev-0.8b"


def run() -> dict:
    projection_path = STATE / "system-one/candidates/decis-kev-0.8b.json"
    brief_path = STATE / "action-brief.json"
    snapshot_path = STATE / "shadow/latest.json"
    ledger = STATE / "system-one/candidates/decis-kev-0.8b-observations.jsonl"
    summary_path = STATE / "system-one/candidates/decis-kev-0.8b-summary.json"

    if not (
        projection_path.exists()
        and brief_path.exists()
        and snapshot_path.exists()
    ):
        summary = summarize(read_jsonl(ledger))
        summary.update(
            {
                "candidate_id": CANDIDATE_ID,
                "provider": "decis-kev-candidate",
                "appended_this_cycle": 0,
            }
        )
        atomic_json(summary_path, summary)
        return summary

    projection = json.loads(projection_path.read_text())
    brief = json.loads(brief_path.read_text())
    snapshot = json.loads(snapshot_path.read_text())
    by_action = {
        row.get("item_id"): row
        for row in brief.get("actions", [])
    }
    routing_contract = projection.get(
        "routing_contract",
        "processing-lane+authority-policy/v2",
    )

    appended = 0
    for item in projection.get("items", []):
        action = by_action.get(item.get("item_id"), {})
        model_identity = str(
            item.get("model")
            or projection.get("candidate_id")
            or CANDIDATE_ID
        )
        if append_once(
            ledger,
            make_observation(
                snapshot,
                action,
                item,
                model_identity,
                routing_contract,
            ),
        ):
            appended += 1

    rows = read_jsonl(ledger)
    summary = summarize(rows)
    summary.update(
        {
            "candidate_id": CANDIDATE_ID,
            "provider": projection.get("provider"),
            "candidate_status": projection.get("status"),
            "model_identity": (
                projection.get("items", [{}])[0].get("model")
                if projection.get("items")
                else None
            ),
            "appended_this_cycle": appended,
            "routing_contract": routing_contract,
        }
    )
    atomic_json(summary_path, summary)
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))
