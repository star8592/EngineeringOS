import hashlib
import pathlib
import sys
import tempfile

sys.path.insert(0, "src/engineeringos")

from reconcile_queue_outcomes import (
    authoritative_ci_refs,
    deployment_identity_refs,
    live_production_refs,
    reconcile,
)


rich_ci = {
    "origin_main": "abc",
    "current_head_evidence": {
        "ci_evidence": {
            "state": "PASS",
            "latest_run": {
                "workflowName": "DevControl 3 CI",
                "headSha": "abc",
                "status": "completed",
                "conclusion": "success",
                "createdAt": "2026-10-04T00:00:00Z",
                "url": "https://example/run/1",
            },
        }
    },
}
refs = authoritative_ci_refs(rich_ci)
assert refs == [
    "github-actions:https://example/run/1",
    "source-sha:abc",
]

running_ci = {
    "origin_main": "abc",
    "current_head_evidence": {
        "ci_evidence": {
            "state": "RUNNING",
            "latest_run": {
                "headSha": "abc",
                "status": "in_progress",
            },
        }
    },
}
assert authoritative_ci_refs(running_ci) == []

wrong_head = {
    "origin_main": "abc",
    "current_head_evidence": {
        "ci_evidence": {
            "state": "PASS",
            "latest_run": {
                "headSha": "def",
                "status": "completed",
                "conclusion": "success",
                "url": "https://example/run/2",
            },
        }
    },
}
assert authoritative_ci_refs(wrong_head) == []

legacy = {
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
                "url": "https://example/run/legacy",
            }
        ],
    },
}
assert authoritative_ci_refs(legacy) == [
    "github-actions:https://example/run/legacy",
    "source-sha:abc",
]

with tempfile.TemporaryDirectory() as td:
    evidence_file = pathlib.Path(td) / "release.json"
    evidence_file.write_text(
        '{"release":"e3b88b47","qualified":true}\n'
    )
    digest = hashlib.sha256(
        evidence_file.read_bytes()
    ).hexdigest()

    evidence = {
        "interpretation": {
            "live_production_qualification": "PASS",
            "deployment_identity": "RESOLVED",
        },
        "live_release_evidence": {
            "release_evidence_file": str(evidence_file),
            "full_source_sha": (
                "e3b88b47ccce96409eb929fd56ff8ff6e4cc68de"
            ),
            "production": {
                "release_id": "e3b88b47",
            },
            "deployment_binding_sha256": "c" * 64,
            "deployment_observation": {
                "server": {
                    "tree_sha256": "a" * 64,
                },
                "agent": {
                    "tree_sha256": "b" * 64,
                },
            },
        },
        **rich_ci,
    }

    live_refs = live_production_refs(evidence)
    assert live_refs == [
        f"file:{evidence_file}#sha256:{digest}",
        "production-release:e3b88b47",
        (
            "source-sha:"
            "e3b88b47ccce96409eb929fd56ff8ff6e4cc68de"
        ),
    ]

    deployment_refs = deployment_identity_refs(evidence)
    assert deployment_refs == [
        "production-release:e3b88b47",
        (
            "source-sha:"
            "e3b88b47ccce96409eb929fd56ff8ff6e4cc68de"
        ),
        "deployment-binding-sha256:" + "c" * 64,
        "server-tree-sha256:" + "a" * 64,
        "agent-tree-sha256:" + "b" * 64,
    ]

    q = {
        "items": [
            {
                "id": "restore",
                "kind": "RESTORE_MAIN_QUALIFICATION",
                "state": "PENDING_RESOLUTION",
            },
            {
                "id": "live",
                "kind": "RESOLVE_LIVE_PRODUCTION_QUALIFICATION",
                "state": "PENDING_RESOLUTION",
            },
            {
                "id": "deploy",
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
            "id": "restore",
            "reason": "AUTHORITATIVE_CI_SUCCESS",
        },
        {
            "id": "live",
            "reason": "LIVE_PRODUCTION_QUALIFIED",
        },
        {
            "id": "deploy",
            "reason": "DEPLOYMENT_IDENTITY_RESOLVED",
        },
    ]

    by_id = {row["id"]: row for row in q["items"]}
    assert by_id["restore"]["state"] == "RESOLVED"
    assert (
        by_id["restore"]["resolved_by"]
        == "engineeringos-authoritative-evidence-reconciler"
    )
    assert (
        by_id["restore"]["closure_kind"]
        == "AUTHORITATIVE_CI_SUCCESS"
    )

    assert by_id["live"]["state"] == "RESOLVED"
    assert (
        by_id["live"]["resolution_evidence_refs"][0]
        == f"file:{evidence_file}#sha256:{digest}"
    )
    assert (
        by_id["live"]["closure_kind"]
        == "LIVE_PRODUCTION_QUALIFIED"
    )

    assert by_id["deploy"]["state"] == "RESOLVED"
    assert (
        by_id["deploy"]["closure_kind"]
        == "DEPLOYMENT_IDENTITY_RESOLVED"
    )
    assert any(
        ref.startswith("deployment-binding-sha256:")
        for ref in by_id["deploy"]["resolution_evidence_refs"]
    )

    # Artifact identity remains unresolved because deployment-byte identity
    # is not the same claim as build-artifact identity.
    assert by_id["artifact"]["state"] == "PENDING_RESOLUTION"

missing_file = {
    "interpretation": {
        "live_production_qualification": "PASS",
    },
    "live_release_evidence": {
        "release_evidence_file": "/missing/release.json",
        "full_source_sha": "abc",
        "production": {"release_id": "abc"},
    },
}
assert live_production_refs(missing_file) == []

partial_deploy = {
    "interpretation": {
        "deployment_identity": "PARTIAL",
    }
}
assert deployment_identity_refs(partial_deploy) == []

outcome_q = {
    "items": [
        {
            "id": "x",
            "kind": "OTHER",
            "state": "PENDING_RESOLUTION",
        }
    ]
}
outcomes = [
    {
        "item_id": "x",
        "label": "FALSE_POSITIVE",
        "evidence_refs": ["evidence:1"],
        "outcome_id": "o1",
    }
]
changed = reconcile(outcome_q, outcomes, {})
assert changed == [{"id": "x", "reason": "OUTCOME_LEDGER"}]
assert outcome_q["items"][0]["state"] == "RESOLVED"

print("27 authoritative-evidence queue reconciliation invariants passed")
