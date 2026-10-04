from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import pathlib
import tempfile
from collections import defaultdict
from typing import Any

from state_paths import runtime

STATE = runtime()
ACTIVE_ROUTING_CONTRACT = "processing-lane+authority-policy/v2"


def utcnow() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def read_jsonl(path: pathlib.Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text().splitlines()
        if line.strip()
    ]


def atomic_json(path: pathlib.Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (
        json.dumps(
            obj,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
        + "\n"
    ).encode()
    fd, tmp = tempfile.mkstemp(
        prefix=path.name + ".",
        suffix=".tmp",
        dir=path.parent,
    )
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def atomic_jsonl(
    path: pathlib.Path,
    rows: list[dict[str, Any]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = "".join(
        json.dumps(
            row,
            sort_keys=True,
            ensure_ascii=False,
        )
        + "\n"
        for row in rows
    ).encode()
    fd, tmp = tempfile.mkstemp(
        prefix=path.name + ".",
        suffix=".tmp",
        dir=path.parent,
    )
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def semantic_signature(row: dict[str, Any]) -> str:
    payload = {
        "routing_contract": row.get("routing_contract"),
        "kind": row.get("kind"),
        "reason": row.get("reason"),
        "required_assurance": row.get("required_assurance"),
        "automation": row.get("automation"),
    }
    raw = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(raw.encode()).hexdigest()


def priority_for(rows: list[dict[str, Any]]) -> int:
    if any(
        row.get("human_authority_unresolved") is True
        for row in rows
    ):
        return 0
    if any(
        row.get("comparable")
        and row.get("agrees_with_scheduler") is False
        for row in rows
    ):
        return 0
    if any(
        row.get("required_assurance") in {"A3", "A4", "A5"}
        for row in rows
    ):
        return 1
    confidences = [
        float(row["answer_confidence"])
        for row in rows
        if row.get("answer_confidence") is not None
    ]
    if confidences and min(confidences) < 0.60:
        return 2
    return 3


def build_candidate(
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    ordered = sorted(
        rows,
        key=lambda row: (
            str(row.get("observed_at") or ""),
            str(row.get("observation_id") or ""),
        ),
    )
    first = ordered[0]
    latest = ordered[-1]
    signature = semantic_signature(latest)
    candidate_id = hashlib.sha256(
        ("edb-candidate|" + signature).encode()
    ).hexdigest()[:24]

    context_complete = all(
        latest.get(key) not in (None, "")
        for key in (
            "kind",
            "reason",
            "required_assurance",
            "automation",
        )
    )
    authority_unresolved = any(
        row.get("human_authority_unresolved") is True
        for row in ordered
    )

    if authority_unresolved:
        status = "BLOCKED_AUTHORITY_POLICY_UNRESOLVED"
    elif not context_complete:
        status = "BLOCKED_INCOMPLETE_CONTEXT"
    else:
        status = "PENDING_ADJUDICATION"

    model_recommendations = sorted(
        {
            str(row.get("model_recommendation"))
            for row in ordered
            if row.get("model_recommendation")
        }
    )
    scheduler_references = sorted(
        {
            str(row.get("scheduler_lane"))
            for row in ordered
            if row.get("scheduler_lane")
        }
    )
    model_revisions = sorted(
        {
            str(row.get("model_revision"))
            for row in ordered
            if row.get("model_revision")
        }
    )

    return {
        "schema_version": 1,
        "candidate_id": candidate_id,
        "semantic_signature": signature,
        "routing_contract": latest.get("routing_contract"),
        "status": status,
        "priority": priority_for(ordered),
        "kind": latest.get("kind"),
        "reason": latest.get("reason"),
        "required_assurance": latest.get("required_assurance"),
        "automation": latest.get("automation"),
        "human_authority_decision": latest.get(
            "human_authority_decision"
        ),
        "human_authority_source": latest.get(
            "human_authority_source"
        ),
        "scheduler_references": scheduler_references,
        "model_recommendations": model_recommendations,
        "model_revisions": model_revisions,
        "latest_probabilities": latest.get("probabilities"),
        "latest_answer_confidence": latest.get(
            "answer_confidence"
        ),
        "observation_count": len(ordered),
        "first_observed_at": first.get("observed_at"),
        "last_observed_at": latest.get("observed_at"),
        "source_observation_ids": [
            row.get("observation_id")
            for row in ordered
            if row.get("observation_id")
        ],
        "reference_strength": "WEAK_SCHEDULER_REFERENCE",
        "expected_lane": None,
        "label_source": None,
        "adjudicated_at": None,
        "edb_gold": False,
        "authorization": "UNAVAILABLE",
    }


def curate(
    observations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    eligible = [
        row
        for row in observations
        if row.get("routing_contract")
        == ACTIVE_ROUTING_CONTRACT
        and row.get("edb_gold") is False
    ]
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in eligible:
        grouped[semantic_signature(row)].append(row)

    candidates = [
        build_candidate(rows)
        for rows in grouped.values()
    ]
    candidates.sort(
        key=lambda row: (
            row["priority"],
            row["status"],
            str(row.get("kind") or ""),
            row["candidate_id"],
        )
    )
    return candidates


def summarize(
    observations: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
) -> dict[str, Any]:
    pending = [
        row
        for row in candidates
        if row["status"] == "PENDING_ADJUDICATION"
    ]
    blocked = [
        row
        for row in candidates
        if row["status"] != "PENDING_ADJUDICATION"
    ]
    return {
        "schema_version": 1,
        "generated_at": utcnow(),
        "routing_contract": ACTIVE_ROUTING_CONTRACT,
        "source_observations": len(observations),
        "candidate_count": len(candidates),
        "pending_adjudication": len(pending),
        "blocked_candidates": len(blocked),
        "gold_candidates": 0,
        "auto_labeling": False,
        "authorization": "UNAVAILABLE",
        "top_candidates": candidates[:10],
    }


def run() -> dict[str, Any]:
    observations = read_jsonl(
        STATE / "system-one/observations.jsonl"
    )
    candidates = curate(observations)
    summary = summarize(
        observations,
        candidates,
    )
    atomic_jsonl(
        STATE / "system-one/edb-candidates.jsonl",
        candidates,
    )
    atomic_json(
        STATE / "system-one/edb-curation-summary.json",
        summary,
    )
    return summary


if __name__ == "__main__":
    print(
        json.dumps(
            run(),
            indent=2,
            ensure_ascii=False,
        )
    )
