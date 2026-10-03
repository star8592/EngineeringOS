#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import json
import os
import pathlib
import tempfile

from laya_provider import LayaLocalProvider
from state_paths import runtime
from system_one_contract import (
    AUTHORITY_CHOICES,
    PROCESSING_LANES,
    AdvisoryDecision,
    TypedQuestion,
    advisory_route,
    assert_not_authorization,
)
from system_one_provider import SystemOneProviderError


STATE = runtime()

LANE_QUESTION = TypedQuestion(
    question_id="engineering_lane",
    kind="choice",
    instructions=(
        "Choose the safest EngineeringOS processing lane for this engineering work item. "
        "Use DETERMINISTIC_CANDIDATE only for low-risk mechanically checkable work; "
        "use FORMAL_OR_HIGH_ASSURANCE for concurrency, release, identity, security, "
        "at-most-once, authorization-state-machine, or other safety-critical semantics; "
        "otherwise use REASONING_REVIEW. Human decision authority is asked separately."
    ),
    options=tuple(sorted(PROCESSING_LANES)),
)

AUTHORITY_QUESTION = TypedQuestion(
    question_id="human_authority",
    kind="choice",
    instructions=(
        "Does completing this work require a human to make the final product, business, "
        "permission, or governance decision rather than merely reviewing engineering evidence?"
    ),
    options=tuple(sorted(AUTHORITY_CHOICES)),
)


def utcnow() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def atomic_json(path: pathlib.Path, obj: dict) -> None:
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


def classify_action(
    provider: LayaLocalProvider,
    action: dict,
) -> dict:
    state = {
        "project": "DevControl",
        "work_kind": action.get("kind"),
        "reason": action.get("reason"),
        "required_assurance": action.get(
            "required_assurance"
        ),
        "automation": action.get("automation"),
        "scheduler_lane": action.get("lane"),
        "schedule_state": action.get(
            "schedule_state"
        ),
        "target_mutation_authorized": False,
    }
    high_risk = action.get(
        "required_assurance"
    ) in {"A3", "A4", "A5"}

    batch = provider.decide_many(
        state=state,
        questions=(
            LANE_QUESTION,
            AUTHORITY_QUESTION,
        ),
    )
    lane = batch.answers[LANE_QUESTION.question_id]
    authority = batch.answers[
        AUTHORITY_QUESTION.question_id
    ]

    lane_decision = AdvisoryDecision(
        source=provider.name,
        question_id=LANE_QUESTION.question_id,
        recommended_route=lane.choice,
        confidence=lane.answer_confidence,
        raw_answer=lane.raw_answer,
    )
    routed = advisory_route(
        lane_decision,
        high_risk=high_risk,
    )
    assert_not_authorization(routed)

    human_required = (
        authority.choice
        == "HUMAN_AUTHORITY_REQUIRED"
    )

    return {
        "item_id": action.get("item_id"),
        "kind": action.get("kind"),
        "scheduler_lane": action.get("lane"),
        "model_recommendation": lane.choice,
        "processing_lane_recommendation": lane.choice,
        "advisory_route": routed[
            "recommended_route"
        ],
        "answer_confidence": lane.answer_confidence,
        "processing_lane_confidence": (
            lane.answer_confidence
        ),
        "probabilities": lane.probabilities,
        "processing_lane_probabilities": (
            lane.probabilities
        ),
        "human_authority_recommendation": (
            authority.choice
        ),
        "human_authority_required": human_required,
        "human_authority_confidence": (
            authority.answer_confidence
        ),
        "human_authority_probabilities": (
            authority.probabilities
        ),
        "model": batch.model,
        "latency_ms": batch.latency_ms,
        "policy_override": (
            routed["reason"]
            != "SYSTEM_ONE_RECOMMENDATION"
        ),
        "advisory_only": True,
        "authorization": "UNAVAILABLE",
    }


def run() -> dict:
    provider = LayaLocalProvider()
    brief_path = STATE / "action-brief.json"
    projection_path = (
        STATE / "system-one/projection.json"
    )
    health = provider.health()
    out = {
        "schema_version": 2,
        "generated_at": utcnow(),
        "provider": provider.name,
        "mode": "SHADOW_ADVISORY",
        "provider_health": health,
        "routing_axes": [
            "PROCESSING_LANE",
            "HUMAN_AUTHORITY",
        ],
        "advisory_only": True,
        "authorization": "UNAVAILABLE",
        "items": [],
    }
    if (
        not brief_path.exists()
        or not health.get("available")
    ):
        out["status"] = "UNAVAILABLE"
        atomic_json(projection_path, out)
        return out

    brief = json.loads(brief_path.read_text())
    errors = []
    for action in brief.get("actions", []):
        try:
            out["items"].append(
                classify_action(
                    provider,
                    action,
                )
            )
        except SystemOneProviderError as exc:
            errors.append(
                {
                    "item_id": action.get("item_id"),
                    "error": str(exc),
                }
            )
    out["errors"] = errors
    out["status"] = (
        "ACTIVE"
        if out["items"]
        else "DEGRADED"
    )
    atomic_json(projection_path, out)
    return out


if __name__ == "__main__":
    print(
        json.dumps(
            run(),
            indent=2,
            ensure_ascii=False,
        )
    )
