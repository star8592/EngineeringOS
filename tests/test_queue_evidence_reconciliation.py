import sys

sys.path.insert(0, "src/engineeringos")

from reconcile_queue_outcomes import (
    authoritative_ci_refs,
    deployment_identity_refs,
    live_production_refs,
    reconcile,
)


evidence = {
    "origin_main": "abc",
    "current_head_evidence": {
        "ci": "SUCCESS",
        "runs": [
            {
                "workflowName": "DevControl 3 CI",
                "headSha": "abc",
                "status": "completed",
                "conclusion": "success",
                "createdAt": "2026-10-04T00:00:00Z",
                "url": "https://example/run/1",
            }
        ],
    },
    "interpretation": {
        "live_production_qualification": "PASS",
        "deployment_identity": "RESOLVED",
    },
    "live_release_evidence": {
        "qualification_state": "RESOLVED",
        "source_identity_state": "RESOLVED",
        "release_evidence_file": "/evidence/e3b88b47.json",
        "full_source_sha": "e3b88b47full",
        "deployment_binding_sha256": "c" * 64,
        "production": {
            "release_id": "e3b88b47",
        },
        "deployment_observation": {
            "deployment_identity_state": "RESOLVED",
            "server": {
                "state": "RESOLVED",
                "tree_sha256": "a" * 64,
            },
            "agent": {
                "state": "RESOLVED",
                "tree_sha256": "b" * 64,
            },
        },
    },
}

ci_refs = authoritative_ci_refs(evidence)
assert ci_refs == [
    "github-actions:https://example/run/1",
    "source-sha:abc",
]

live_refs = live_production_refs(evidence)
assert live_refs == [
    "release-evidence-file:/evidence/e3b88b47.json",
    "production-release:e3b88b47",
    "source-sha:e3b88b47full",
    f"deployment-binding:sha256:{'c' * 64}",
]

deployment_refs = deployment_identity_refs(evidence)
assert deployment_refs == [
    "production-release:e3b88b47",
    "source-sha:e3b88b47full",
    f"deployment-binding:sha256:{'c' * 64}",
    f"server-tree:sha256:{'a' * 64}",
    f"agent-tree:sha256:{'b' * 64}",
]

q = {
    "items": [
        {
            "id": "main-unknown",
            "kind": "RESOLVE_MAIN_QUALIFICATION",
            "state": "PENDING_RESOLUTION",
        },
        {
            "id": "main-failed",
            "kind": "RESTORE_MAIN_QUALIFICATION",
            "state": "PENDING_RESOLUTION",
        },
        {
            "id": "live",
            "kind": "RESOLVE_LIVE_PRODUCTION_QUALIFICATION",
            "state": "PENDING_RESOLUTION",
        },
        {
            "id": "deployment",
            "kind": "CLOSE_DEPLOYMENT_IDENTITY_GAP",
            "state": "PENDING_RESOLUTION",
        },
        {
            "id": "artifact",
            "kind": "CLOSE_ARTIFACT_IDENTITY_GAP",
            "state": "PENDING_RESOLUTION",
        },
    ]
}

changed = reconcile(q, [], evidence)
assert changed == [
    {
        "id": "main-unknown",
        "reason": "AUTHORITATIVE_CI_SUCCESS",
    },
    {
        "id": "main-failed",
        "reason": "AUTHORITATIVE_CI_SUCCESS",
    },
    {
        "id": "live",
        "reason": "LIVE_PRODUCTION_QUALIFIED",
    },
    {
        "id": "deployment",
        "reason": "DEPLOYMENT_IDENTITY_RESOLVED",
    },
]

by_id = {
    row["id"]: row
    for row in q["items"]
}
for key in ("main-unknown", "main-failed", "live", "deployment"):
    assert by_id[key]["state"] == "RESOLVED"
    assert by_id[key]["resolved_by"] == (
        "engineeringos-authoritative-evidence-reconciler"
    )
    assert by_id[key]["resolution_evidence_refs"]

assert by_id["main-unknown"]["closure_kind"] == "AUTHORITATIVE_CI_SUCCESS"
assert by_id["main-failed"]["closure_kind"] == "AUTHORITATIVE_CI_SUCCESS"
assert by_id["live"]["closure_kind"] == "LIVE_PRODUCTION_QUALIFIED"
assert by_id["deployment"]["closure_kind"] == "DEPLOYMENT_IDENTITY_RESOLVED"
assert by_id["artifact"]["state"] == "PENDING_RESOLUTION"

no_ci = {
    **evidence,
    "current_head_evidence": {
        "ci": "IN_PROGRESS",
        "runs": [],
    },
}
assert authoritative_ci_refs(no_ci) == []

broken_live = {
    **evidence,
    "live_release_evidence": {
        **evidence["live_release_evidence"],
        "release_evidence_file": None,
    },
}
assert live_production_refs(broken_live) == []

broken_deployment = {
    **evidence,
    "live_release_evidence": {
        **evidence["live_release_evidence"],
        "deployment_observation": {
            **evidence["live_release_evidence"]["deployment_observation"],
            "server": {
                "state": "RESOLVED",
                "tree_sha256": None,
            },
        },
    },
}
assert deployment_identity_refs(broken_deployment) == []

q2 = {
    "items": [
        {
            "id": "deployment",
            "kind": "CLOSE_DEPLOYMENT_IDENTITY_GAP",
            "state": "PENDING_RESOLUTION",
        }
    ]
}
assert reconcile(q2, [], broken_deployment) == []
assert q2["items"][0]["state"] == "PENDING_RESOLUTION"

print("22 authoritative-evidence queue reconciliation invariants passed")
