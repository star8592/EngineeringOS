import sys

sys.path.insert(0, "src/engineeringos")

from production_evidence_semantics import interpret


passed = interpret(
    source_ci="SUCCESS",
    source_head_smoke="UNKNOWN",
    source_ci_evidence={
        "state": "PASS",
        "conclusion": "success",
    },
    release_evidence={
        "qualification_state": "RESOLVED",
        "source_identity_state": "RESOLVED",
        "deployment_identity_state": "RESOLVED",
        "artifact_identity_state": "PARTIAL",
    },
)
assert passed["qualification"] == "PASS"
assert passed["qualification_evidence_state"] == "PASS"
assert passed["qualification_reason"] == "CI_PASS"
assert passed["source_head_production_verification"] == "UNKNOWN"
assert passed["live_production_qualification"] == "PASS"
assert passed["deployment_identity"] == "RESOLVED"
assert passed["artifact_identity"] == "PARTIAL"

no_run = interpret(
    source_ci="UNKNOWN",
    source_head_smoke="UNKNOWN",
    source_ci_evidence={"state": "NO_RUN"},
    release_evidence={},
)
assert no_run["qualification"] == "UNKNOWN"
assert no_run["qualification_evidence_state"] == "NO_RUN"
assert no_run["qualification_reason"] == "NO_CI_RUN"

running = interpret(
    source_ci="IN_PROGRESS",
    source_head_smoke="UNKNOWN",
    source_ci_evidence={"state": "RUNNING"},
    release_evidence={},
)
assert running["qualification"] == "UNKNOWN"
assert running["qualification_evidence_state"] == "RUNNING"
assert running["qualification_reason"] == "CI_RUNNING"

failed = interpret(
    source_ci="CANCELLED",
    source_head_smoke="SUCCESS",
    source_ci_evidence={
        "state": "FAIL",
        "conclusion": "cancelled",
    },
    release_evidence={},
)
assert failed["qualification"] == "FAIL"
assert failed["qualification_evidence_state"] == "FAIL"
assert (
    failed["qualification_reason"]
    == "CI_COMPLETED_NON_SUCCESS:CANCELLED"
)
assert failed["live_production_qualification"] == "UNKNOWN"
assert failed["deployment_identity"] == "UNKNOWN"
assert failed["artifact_identity"] == "UNKNOWN"

legacy = interpret(
    source_ci="FAILURE",
    source_head_smoke="UNKNOWN",
    release_evidence={},
)
assert legacy["qualification"] == "FAIL"
assert legacy["qualification_evidence_state"] == "FAIL"

print("18 production-evidence semantic invariants passed")
