#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
from typing import Any

from outcome_ledger import read_outcomes
from queue_model import resolve
from state_paths import OUTCOME_LEDGER, runtime


Q = runtime("work-queue.json")
L = OUTCOME_LEDGER
E = pathlib.Path("artifacts/evidence-plane.json")


def authoritative_ci_refs(evidence: dict[str, Any]) -> list[str]:
    current = (evidence or {}).get("current_head_evidence") or {}
    if current.get("ci") != "SUCCESS":
        return []

    origin = evidence.get("origin_main")
    runs = current.get("runs") or []
    success = [
        row
        for row in runs
        if row.get("workflowName") == "DevControl 3 CI"
        and row.get("headSha") == origin
        and row.get("status") == "completed"
        and row.get("conclusion") == "success"
        and row.get("url")
    ]
    if not success or not origin:
        return []

    latest = sorted(
        success,
        key=lambda row: row.get("createdAt", ""),
        reverse=True,
    )[0]
    return [
        f"github-actions:{latest['url']}",
        f"source-sha:{origin}",
    ]


def live_production_refs(
    evidence: dict[str, Any],
) -> list[str]:
    interpretation = (evidence or {}).get("interpretation") or {}
    if interpretation.get("live_production_qualification") != "PASS":
        return []

    release = evidence.get("live_release_evidence") or {}
    if (
        release.get("qualification_state") != "RESOLVED"
        or release.get("source_identity_state") != "RESOLVED"
    ):
        return []

    production = release.get("production") or {}
    release_id = production.get("release_id")
    full_source_sha = release.get("full_source_sha")
    evidence_file = release.get("release_evidence_file")
    if not (release_id and full_source_sha and evidence_file):
        return []

    refs = [
        f"release-evidence-file:{evidence_file}",
        f"production-release:{release_id}",
        f"source-sha:{full_source_sha}",
    ]
    binding = release.get("deployment_binding_sha256")
    if binding:
        refs.append(
            f"deployment-binding:sha256:{binding}"
        )
    return refs


def deployment_identity_refs(
    evidence: dict[str, Any],
) -> list[str]:
    interpretation = (evidence or {}).get("interpretation") or {}
    if interpretation.get("deployment_identity") != "RESOLVED":
        return []

    release = evidence.get("live_release_evidence") or {}
    observation = release.get("deployment_observation") or {}
    server = observation.get("server") or {}
    agent = observation.get("agent") or {}
    production = release.get("production") or {}

    release_id = production.get("release_id")
    source_sha = release.get("full_source_sha")
    binding = release.get("deployment_binding_sha256")
    server_tree = server.get("tree_sha256")
    agent_tree = agent.get("tree_sha256")

    if not all(
        [
            release_id,
            source_sha,
            binding,
            server_tree,
            agent_tree,
        ]
    ):
        return []

    if (
        observation.get("deployment_identity_state")
        != "RESOLVED"
        or server.get("state") != "RESOLVED"
        or agent.get("state") != "RESOLVED"
    ):
        return []

    return [
        f"production-release:{release_id}",
        f"source-sha:{source_sha}",
        f"deployment-binding:sha256:{binding}",
        f"server-tree:sha256:{server_tree}",
        f"agent-tree:sha256:{agent_tree}",
    ]


def _evidence_closure(
    item: dict[str, Any],
    *,
    ci_refs: list[str],
    live_refs: list[str],
    deployment_refs: list[str],
) -> tuple[str, list[str]] | None:
    kind = item.get("kind")
    if kind in {
        "RESOLVE_MAIN_QUALIFICATION",
        "RESTORE_MAIN_QUALIFICATION",
    } and ci_refs:
        return "AUTHORITATIVE_CI_SUCCESS", ci_refs

    if (
        kind == "RESOLVE_LIVE_PRODUCTION_QUALIFICATION"
        and live_refs
    ):
        return "LIVE_PRODUCTION_QUALIFIED", live_refs

    if (
        kind == "CLOSE_DEPLOYMENT_IDENTITY_GAP"
        and deployment_refs
    ):
        return "DEPLOYMENT_IDENTITY_RESOLVED", deployment_refs

    return None


def reconcile(
    q: dict[str, Any],
    outcomes: list[dict[str, Any]],
    evidence: dict[str, Any],
) -> list[dict[str, str]]:
    by_outcome = {
        row["item_id"]: row
        for row in outcomes
    }
    changed: list[dict[str, str]] = []

    ci_refs = authoritative_ci_refs(evidence)
    live_refs = live_production_refs(evidence)
    deployment_refs = deployment_identity_refs(evidence)

    for item in q["items"]:
        if item.get("state") != "PENDING_RESOLUTION":
            continue

        outcome = by_outcome.get(item["id"])
        if (
            outcome
            and outcome["label"]
            in {"FALSE_POSITIVE", "SEMANTIC_CORRECTION"}
        ):
            resolve(
                item,
                "engineeringos-outcome-reconciler",
                outcome["evidence_refs"]
                + [f"outcome:{outcome['outcome_id']}"],
            )
            item["outcome_label"] = outcome["label"]
            changed.append(
                {
                    "id": item["id"],
                    "reason": "OUTCOME_LEDGER",
                }
            )
            continue

        closure = _evidence_closure(
            item,
            ci_refs=ci_refs,
            live_refs=live_refs,
            deployment_refs=deployment_refs,
        )
        if closure is None:
            continue

        closure_kind, refs = closure
        resolve(
            item,
            "engineeringos-authoritative-evidence-reconciler",
            refs,
        )
        item["closure_kind"] = closure_kind
        changed.append(
            {
                "id": item["id"],
                "reason": closure_kind,
            }
        )

    return changed


def main() -> int:
    q = json.loads(Q.read_text())
    outcomes = read_outcomes(L)
    evidence = (
        json.loads(E.read_text())
        if E.exists()
        else {}
    )
    changed = reconcile(
        q,
        outcomes,
        evidence,
    )
    Q.write_text(
        json.dumps(
            q,
            indent=2,
            ensure_ascii=False,
        )
        + "\n"
    )
    print(
        json.dumps(
            {"resolved": changed},
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
