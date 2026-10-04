#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import pathlib

from outcome_ledger import read_outcomes
from queue_model import resolve
from state_paths import OUTCOME_LEDGER, runtime


Q = runtime("work-queue.json")
L = OUTCOME_LEDGER
E = pathlib.Path("artifacts/evidence-plane.json")


def file_sha256_ref(path: str | None) -> str | None:
    if not path:
        return None
    p = pathlib.Path(path)
    if not p.is_file():
        return None
    digest = hashlib.sha256(p.read_bytes()).hexdigest()
    return f"file:{p}#sha256:{digest}"


def authoritative_ci_refs(evidence: dict) -> list[str]:
    if not evidence:
        return []
    head = evidence.get("current_head_evidence") or {}
    ci = head.get("ci_evidence") or {}
    if ci:
        if ci.get("state") != "PASS":
            return []
        latest = ci.get("latest_run") or {}
        origin = evidence.get("origin_main")
        if (
            latest.get("headSha") != origin
            or latest.get("status") != "completed"
            or latest.get("conclusion") != "success"
            or not latest.get("url")
        ):
            return []
        return [
            f"github-actions:{latest['url']}",
            f"source-sha:{origin}",
        ]

    # Backward-compatible legacy evidence.
    if head.get("ci") != "SUCCESS":
        return []
    origin = evidence.get("origin_main")
    runs = head.get("runs") or []
    success = [
        row
        for row in runs
        if row.get("workflowName") == "DevControl 3 CI"
        and row.get("headSha") == origin
        and row.get("status") == "completed"
        and row.get("conclusion") == "success"
    ]
    if not success:
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


def live_production_refs(evidence: dict) -> list[str]:
    interpretation = evidence.get("interpretation") or {}
    if (
        interpretation.get("live_production_qualification")
        != "PASS"
    ):
        return []

    release = evidence.get("live_release_evidence") or {}
    production = release.get("production") or {}
    release_id = production.get("release_id")
    source_sha = release.get("full_source_sha")
    evidence_ref = file_sha256_ref(
        release.get("release_evidence_file")
    )
    if not (release_id and source_sha and evidence_ref):
        return []

    return [
        evidence_ref,
        f"production-release:{release_id}",
        f"source-sha:{source_sha}",
    ]


def deployment_identity_refs(evidence: dict) -> list[str]:
    interpretation = evidence.get("interpretation") or {}
    if interpretation.get("deployment_identity") != "RESOLVED":
        return []

    release = evidence.get("live_release_evidence") or {}
    deployment = release.get("deployment_observation") or {}
    production = release.get("production") or {}
    server = deployment.get("server") or {}
    agent = deployment.get("agent") or {}

    release_id = production.get("release_id")
    source_sha = release.get("full_source_sha")
    binding = release.get("deployment_binding_sha256")
    server_digest = server.get("tree_sha256")
    agent_digest = agent.get("tree_sha256")

    if not all(
        [
            release_id,
            source_sha,
            binding,
            server_digest,
            agent_digest,
        ]
    ):
        return []

    return [
        f"production-release:{release_id}",
        f"source-sha:{source_sha}",
        f"deployment-binding-sha256:{binding}",
        f"server-tree-sha256:{server_digest}",
        f"agent-tree-sha256:{agent_digest}",
    ]


def evidence_closure(
    item: dict,
    evidence: dict,
) -> tuple[str, list[str]] | None:
    kind = item.get("kind")
    if kind in {
        "RESOLVE_MAIN_QUALIFICATION",
        "RESTORE_MAIN_QUALIFICATION",
    }:
        refs = authoritative_ci_refs(evidence)
        if refs:
            return "AUTHORITATIVE_CI_SUCCESS", refs

    if kind == "RESOLVE_LIVE_PRODUCTION_QUALIFICATION":
        refs = live_production_refs(evidence)
        if refs:
            return "LIVE_PRODUCTION_QUALIFIED", refs

    if kind == "CLOSE_DEPLOYMENT_IDENTITY_GAP":
        refs = deployment_identity_refs(evidence)
        if refs:
            return "DEPLOYMENT_IDENTITY_RESOLVED", refs

    return None


def reconcile(
    q: dict,
    outcomes: list[dict],
    evidence: dict,
) -> list[dict]:
    by_outcome = {
        row["item_id"]: row
        for row in outcomes
    }
    changed = []

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

        closure = evidence_closure(item, evidence)
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
    changed = reconcile(q, outcomes, evidence)
    Q.write_text(
        json.dumps(q, indent=2, ensure_ascii=False) + "\n"
    )
    print(json.dumps({"resolved": changed}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
