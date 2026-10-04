from __future__ import annotations

import datetime as dt
import json
import os
import pathlib
import tempfile
from typing import Any

from state_paths import runtime
from system_one_contract import PROCESSING_LANES

ROOT = pathlib.Path(__file__).resolve().parents[2]
STATE = runtime()
ADJUDICATIONS_PATH = ROOT / "benchmarks/edb/adjudications.jsonl"

VALID_DECISIONS = {
    "ACCEPT_GOLD",
    "REJECT_CANDIDATE",
}
VALID_GOLD_SOURCES = {
    "HUMAN_EXPERT",
    "FORMAL_EVIDENCE",
    "REVIEWED_CONSENSUS",
}
FORBIDDEN_GOLD_SOURCES = {
    "SYSTEM_ONE_MODEL",
    "MODEL_ONLY",
    "WEAK_SCHEDULER_REFERENCE",
    "SCHEDULER_ONLY",
}


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


def validate_record_shape(record: dict[str, Any]) -> str | None:
    if int(record.get("schema_version", 0)) != 1:
        return "UNSUPPORTED_SCHEMA"
    if record.get("decision") not in VALID_DECISIONS:
        return "INVALID_DECISION"
    if not str(record.get("candidate_id") or "").strip():
        return "CANDIDATE_ID_REQUIRED"
    if not str(record.get("semantic_signature") or "").strip():
        return "SEMANTIC_SIGNATURE_REQUIRED"
    if not str(record.get("routing_contract") or "").strip():
        return "ROUTING_CONTRACT_REQUIRED"
    if not str(record.get("reviewer_ref") or "").strip():
        return "REVIEWER_REF_REQUIRED"
    if not str(record.get("rationale") or "").strip():
        return "RATIONALE_REQUIRED"
    if not str(record.get("reviewed_at") or "").strip():
        return "REVIEWED_AT_REQUIRED"
    evidence_refs = record.get("evidence_refs")
    if not isinstance(evidence_refs, list) or not evidence_refs:
        return "EVIDENCE_REFS_REQUIRED"

    if record["decision"] == "ACCEPT_GOLD":
        if record.get("expected_lane") not in PROCESSING_LANES:
            return "EXPECTED_LANE_INVALID"
        source = str(record.get("label_source") or "")
        if source in FORBIDDEN_GOLD_SOURCES:
            return "GOLD_SOURCE_FORBIDDEN"
        if source not in VALID_GOLD_SOURCES:
            return "GOLD_SOURCE_INVALID"
    else:
        if record.get("expected_lane") is not None:
            return "REJECT_MUST_NOT_LABEL"
    return None


def validate_binding(
    candidate: dict[str, Any],
    record: dict[str, Any],
) -> str | None:
    if candidate.get("status") != "PENDING_ADJUDICATION":
        return "CANDIDATE_NOT_ADJUDICATABLE"
    if candidate.get("edb_gold") is not False:
        return "CANDIDATE_ALREADY_GOLD"
    if (
        record.get("semantic_signature")
        != candidate.get("semantic_signature")
    ):
        return "SEMANTIC_SIGNATURE_MISMATCH"
    if (
        record.get("routing_contract")
        != candidate.get("routing_contract")
    ):
        return "ROUTING_CONTRACT_MISMATCH"
    return None


def gold_row(
    candidate: dict[str, Any],
    record: dict[str, Any],
) -> dict[str, Any]:
    assurance = candidate.get("required_assurance")
    return {
        "id": candidate["candidate_id"],
        "state": {
            "kind": candidate.get("kind"),
            "reason": candidate.get("reason"),
            "required_assurance": assurance,
            "automation": candidate.get("automation"),
        },
        "expected_lane": record["expected_lane"],
        "expected_human_authority": candidate.get(
            "human_authority_decision"
        ),
        "high_risk": assurance in {"A3", "A4", "A5"},
        "metadata": {
            "schema_version": 1,
            "candidate_id": candidate["candidate_id"],
            "semantic_signature": candidate["semantic_signature"],
            "routing_contract": candidate["routing_contract"],
            "label_source": record["label_source"],
            "reviewer_ref": record["reviewer_ref"],
            "reviewed_at": record.get("reviewed_at"),
            "rationale": record["rationale"],
            "evidence_refs": record["evidence_refs"],
            "derived_from_shadow_observations": (
                candidate.get("source_observation_ids") or []
            ),
        },
    }


def adjudicate(
    candidates: list[dict[str, Any]],
    records: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    by_candidate = {
        row["candidate_id"]: row
        for row in candidates
    }
    seen_records: set[str] = set()
    gold: list[dict[str, Any]] = []
    rejected = 0
    invalid: list[dict[str, Any]] = []
    decided_candidates: set[str] = set()

    for index, record in enumerate(records):
        candidate_id = str(
            record.get("candidate_id") or ""
        )
        if candidate_id in seen_records:
            invalid.append(
                {
                    "record_index": index,
                    "candidate_id": candidate_id,
                    "reason": "DUPLICATE_ADJUDICATION",
                }
            )
            continue
        seen_records.add(candidate_id)

        error = validate_record_shape(record)
        candidate = by_candidate.get(candidate_id)
        if error is None and candidate is None:
            error = "CANDIDATE_NOT_FOUND"
        if (
            error is None
            and candidate is not None
        ):
            error = validate_binding(
                candidate,
                record,
            )

        if error is not None:
            invalid.append(
                {
                    "record_index": index,
                    "candidate_id": candidate_id,
                    "reason": error,
                }
            )
            continue

        decided_candidates.add(candidate_id)
        if record["decision"] == "REJECT_CANDIDATE":
            rejected += 1
            continue

        gold.append(
            gold_row(
                candidate,
                record,
            )
        )

    pending = sum(
        1
        for row in candidates
        if row.get("status") == "PENDING_ADJUDICATION"
        and row.get("candidate_id") not in decided_candidates
    )
    blocked = sum(
        1
        for row in candidates
        if row.get("status") != "PENDING_ADJUDICATION"
    )
    summary = {
        "schema_version": 1,
        "generated_at": utcnow(),
        "candidate_count": len(candidates),
        "adjudication_records": len(records),
        "gold_count": len(gold),
        "rejected_count": rejected,
        "invalid_count": len(invalid),
        "pending_adjudication": pending,
        "blocked_candidates": blocked,
        "auto_adjudication": False,
        "model_only_gold_allowed": False,
        "authorization": "UNAVAILABLE",
        "invalid_records": invalid,
    }
    return gold, summary


def run() -> dict[str, Any]:
    candidates = read_jsonl(
        STATE / "system-one/edb-candidates.jsonl"
    )
    records = read_jsonl(ADJUDICATIONS_PATH)
    gold, summary = adjudicate(
        candidates,
        records,
    )
    atomic_jsonl(
        STATE / "system-one/edb-gold.jsonl",
        gold,
    )
    atomic_json(
        STATE / "system-one/edb-adjudication-summary.json",
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
