#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import json
import os
import pathlib
import tempfile

from laya_provider import LayaLocalProvider
from state_paths import runtime
from system_one_contract import ROUTES, TypedQuestion, advisory_route, assert_not_authorization
from system_one_provider import SystemOneProviderError


STATE = runtime()
LANE_QUESTION = TypedQuestion(
    question_id="engineering_lane",
    kind="choice",
    instructions=(
        "Choose the safest EngineeringOS processing lane for this engineering work item. "
        "Use DETERMINISTIC_CANDIDATE only for low-risk mechanically checkable work; "
        "use FORMAL_OR_HIGH_ASSURANCE for authorization, concurrency, release, identity, "
        "security, at-most-once, or other safety-critical state-machine changes; "
        "use HUMAN_REVIEW when the decision requires product/business authority; "
        "otherwise use REASONING_REVIEW."
    ),
    options=tuple(sorted(ROUTES)),
)


def utcnow() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def atomic_json(path: pathlib.Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def classify_action(provider: LayaLocalProvider, action: dict) -> dict:
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
    high_risk = action.get("required_assurance") in {"A3", "A4", "A5"}
    result = provider.decide(state=state, question=LANE_QUESTION)
    routed = advisory_route(result.decision, high_risk=high_risk)
    assert_not_authorization(routed)
    return {
        "item_id": action.get("item_id"),
        "kind": action.get("kind"),
        "scheduler_lane": action.get("lane"),
        "model_recommendation": result.decision.recommended_route,
        "advisory_route": routed["recommended_route"],
        "answer_confidence": result.answer_confidence,
        "probabilities": result.probabilities,
        "model": result.model,
        "latency_ms": result.latency_ms,
        "policy_override": routed["reason"] != "SYSTEM_ONE_RECOMMENDATION",
        "advisory_only": True,
        "authorization": "UNAVAILABLE",
    }


def run() -> dict:
    provider = LayaLocalProvider()
    brief_path = STATE / "action-brief.json"
    projection_path = STATE / "system-one/projection.json"
    health = provider.health()
    out = {
        "schema_version": 1,
        "generated_at": utcnow(),
        "provider": provider.name,
        "mode": "SHADOW_ADVISORY",
        "provider_health": health,
        "advisory_only": True,
        "authorization": "UNAVAILABLE",
        "items": [],
    }
    if not brief_path.exists() or not health.get("available"):
        out["status"] = "UNAVAILABLE"
        atomic_json(projection_path, out)
        return out

    brief = json.loads(brief_path.read_text())
    errors = []
    for action in brief.get("actions", []):
        try:
            out["items"].append(classify_action(provider, action))
        except SystemOneProviderError as exc:
            errors.append({"item_id": action.get("item_id"), "error": str(exc)})
    out["errors"] = errors
    out["status"] = "ACTIVE" if out["items"] else "DEGRADED"
    atomic_json(projection_path, out)
    return out


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))
