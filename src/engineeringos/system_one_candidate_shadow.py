#!/usr/bin/env python3
from __future__ import annotations

import json
from typing import Any

from decis_provider import DecisProvider
from state_paths import runtime
from system_one_provider import SystemOneProvider, SystemOneProviderError
from system_one_shadow import (
    atomic_json,
    classify_action,
    load_authority_policy,
    utcnow,
)


STATE = runtime()
CANDIDATE_ID = "decis-kev-0.8b"
PROJECTION = STATE / "system-one/candidates/decis-kev-0.8b.json"


def build_projection(
    provider: SystemOneProvider,
    brief: dict[str, Any],
    authority_policy: dict[str, Any],
) -> dict[str, Any]:
    health = provider.health()
    out: dict[str, Any] = {
        "schema_version": 1,
        "generated_at": utcnow(),
        "candidate_id": CANDIDATE_ID,
        "role": "PARALLEL_SHADOW_CANDIDATE",
        "provider": provider.name,
        "mode": "SHADOW_ADVISORY",
        "provider_health": health,
        "routing_contract": "processing-lane+authority-policy/v2",
        "advisory_only": True,
        "authorization": "UNAVAILABLE",
        "influence_routing": False,
        "items": [],
        "errors": [],
    }
    if not health.get("available"):
        out["status"] = "UNAVAILABLE"
        return out

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
            out["errors"].append(
                {
                    "item_id": action.get("item_id"),
                    "error": str(exc),
                }
            )
    out["status"] = "ACTIVE" if out["items"] else "DEGRADED"
    return out


def error_projection(exc: Exception) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "generated_at": utcnow(),
        "candidate_id": CANDIDATE_ID,
        "role": "PARALLEL_SHADOW_CANDIDATE",
        "provider": "decis",
        "mode": "SHADOW_ADVISORY",
        "status": "ERROR",
        "advisory_only": True,
        "authorization": "UNAVAILABLE",
        "influence_routing": False,
        "items": [],
        "errors": [
            {
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
        ],
    }


def run() -> dict[str, Any]:
    brief_path = STATE / "action-brief.json"
    if not brief_path.exists():
        out = {
            **error_projection(FileNotFoundError(str(brief_path))),
            "status": "NO_ACTION_BRIEF",
        }
        atomic_json(PROJECTION, out)
        return out

    provider = DecisProvider(timeout_seconds=5.0, name="decis-kev-candidate")
    try:
        brief = json.loads(brief_path.read_text())
        out = build_projection(
            provider,
            brief,
            load_authority_policy(),
        )
    except Exception as exc:
        out = error_projection(exc)
    atomic_json(PROJECTION, out)
    return out


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))
