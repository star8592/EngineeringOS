import sys

sys.path.insert(0, "src/engineeringos")

from qualification_resolution import qualification_work_item


assert qualification_work_item({
    "qualification": "PASS",
    "qualification_evidence_state": "PASS",
    "qualification_reason": "CI_PASS",
}) is None

no_run = qualification_work_item({
    "qualification": "UNKNOWN",
    "qualification_evidence_state": "NO_RUN",
    "qualification_reason": "NO_CI_RUN",
})
assert no_run["kind"] == "RESOLVE_MAIN_QUALIFICATION"
assert no_run["priority"] == 1
assert no_run["automation"] == "REVIEW"
assert no_run["evidence_state"] == "NO_RUN"
assert "no DevControl 3 CI run" in no_run["reason"]

running = qualification_work_item({
    "qualification": "UNKNOWN",
    "qualification_evidence_state": "RUNNING",
    "qualification_reason": "CI_RUNNING",
})
assert running["kind"] == "RESOLVE_MAIN_QUALIFICATION"
assert running["evidence_state"] == "RUNNING"
assert "still running" in running["reason"]

query_error = qualification_work_item({
    "qualification": "UNKNOWN",
    "qualification_evidence_state": "QUERY_ERROR",
    "qualification_reason": "WORKFLOW_QUERY_ERROR",
})
assert query_error["kind"] == "RESOLVE_MAIN_QUALIFICATION"
assert "query failed" in query_error["reason"]

failed = qualification_work_item({
    "qualification": "FAIL",
    "qualification_evidence_state": "FAIL",
    "qualification_reason": "CI_COMPLETED_NON_SUCCESS:CANCELLED",
})
assert failed["kind"] == "RESTORE_MAIN_QUALIFICATION"
assert failed["priority"] == 0
assert failed["automation"] == "BLOCK_UNTIL_RESOLVED"
assert "CANCELLED" in failed["reason"]

print("12 qualification-resolution invariants passed")
