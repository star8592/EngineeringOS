#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import json
import os
import pathlib
import tempfile

from authority_policy import decide_authority, validate_policy
from laya_provider import LayaLocalProvider
from state_paths import runtime
from system_one_contract import (
    PROCESSING_LANES,
    TypedQuestion,
    advisory_route,
    assert_not_authorization,
)
from system_one_provider import SystemOneProvider, SystemOneProviderError


ROOT = pathlib.Path(__file__).resolve().parents[2]
STATE = runtime()
AUTHORITY_POLICY_PATH = (
    ROOT
    / "project_profiles/devcontrol/system-one-authority-policy.json"
)

LANE_QUESTION = TypedQuestion(
    question_id="engineering_lane",
    kind="choice",
    instructions=(
        "Choose the safest EngineeringOS processing lane for this engineering work item. "
        "Human authority and approval are determined separately by deterministic project policy."
    ),
    options=tuple(sorted(PROCESSING_LANES)),
    criteria=(
        (
            "DETERMINISTIC_CANDIDATE",
            "Low-risk, mechanically checkable work where deterministic tests, formatting, read-only inspection, or a fixed procedure can establish the result without ambiguous engineering judgment.",
        ),
        (
            "REASONING_REVIEW",
            "Engineering work that requires interpretation, architectural judgment, ambiguity resolution, or semantic review, but not formal methods or high-assurance state-machine reasoning.",
        ),
        (
            "FORMAL_OR_HIGH_ASSURANCE",
            "Safety-critical engineering involving authorization semantics, concurrency, leases, at-most-once execution, release or rollback state machines, security, identity, provenance, or invariants that deserve model checking or formal proof.",
        ),
    ),
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


def load_authority_policy(path: pathlib.Path = AUTHORITY_POLICY_PATH) -> dict:
    policy = json.loads(path.read_text())
    validate_policy(policy)
    return policy


def classify_action(
    provider: SystemOneProvider,
    action: dict,
    *,
    authority_policy: dict | None = None,
) -> dict:
    state = {
        "project": "DevControl",
        "work_kind": action.get("kind"),
        "reason": action.get("reason"),
        "required_assurance": action.get("required_assurance"),
        "automation": action.get("automation"),
        "scheduler_lane": action.get("lane"),
        "schedule_state": action.get("schedule_state"),
        "target_mutation_authorized": False,
    }
    high_risk = action.get(
        "required_assurance"
    ) in {"A3", "A4", "A5"}

    result = provider.decide(
        state=state,
        question=LANE_QUESTION,
    )
    routed = advisory_route(
        result.decision,
        high_risk=high_risk,
    )
    assert_not_authorization(routed)

    policy = (
        authority_policy
        if authority_policy is not None
        else load_authority_policy()
    )
    authority = decide_authority(
        policy,
        {"kind": action.get("kind")},
    )
    human_required = (
        authority.decision
        == "HUMAN_AUTHORITY_REQUIRED"
    )
    authority_unresolved = (
        authority.decision
        == "AUTHORITY_POLICY_UNRESOLVED"
    )

    return {
        "item_id": action.get("item_id"),
        "kind": action.get("kind"),
        "scheduler_lane": action.get("lane"),
        "model_recommendation": (
            result.decision.recommended_route
        ),
        "processing_lane_recommendation": (
            result.decision.recommended_route
        ),
        "advisory_route": routed["recommended_route"],
        "answer_confidence": result.answer_confidence,
        "processing_lane_confidence": (
            result.answer_confidence
        ),
        "probabilities": result.probabilities,
        "processing_lane_probabilities": (
            result.probabilities
        ),
        "human_authority_decision": authority.decision,
        "human_authority_required": human_required,
        "human_authority_unresolved": authority_unresolved,
        "human_authority_source": authority.source,
        "human_authority_rule": authority.rule,
        "model": result.model,
        "latency_ms": result.latency_ms,
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
    authority_policy = load_authority_policy()
    out = {
        "schema_version": 2,
        "generated_at": utcnow(),
        "provider": provider.name,
        "mode": "SHADOW_ADVISORY",
        "provider_health": health,
        "routing_contract": (
            "processing-lane+authority-policy/v2"
        ),
        "routing_axes": {
            "processing_lane": "SYSTEM_ONE_ADVISORY",
            "human_authority": "PROJECT_POLICY",
        },
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
                    authority_policy=authority_policy,
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
