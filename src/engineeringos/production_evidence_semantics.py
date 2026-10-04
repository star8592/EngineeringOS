from __future__ import annotations


def _legacy_ci_evidence(source_ci: str) -> dict:
    if source_ci == "SUCCESS":
        return {"state": "PASS", "legacy_state": source_ci}
    if source_ci in {
        "FAILURE",
        "CANCELLED",
        "TIMED_OUT",
        "ACTION_REQUIRED",
        "STARTUP_FAILURE",
    }:
        return {
            "state": "FAIL",
            "legacy_state": source_ci,
            "conclusion": source_ci.lower(),
        }
    if source_ci in {"QUEUED", "IN_PROGRESS", "PENDING"}:
        return {"state": "RUNNING", "legacy_state": source_ci}
    return {"state": "NO_RUN", "legacy_state": source_ci}


def interpret(
    *,
    source_ci: str,
    source_head_smoke: str,
    release_evidence: dict | None,
    source_ci_evidence: dict | None = None,
) -> dict:
    live_qualified = (
        (release_evidence or {}).get("qualification_state")
        == "RESOLVED"
    )
    source_resolved = (
        (release_evidence or {}).get("source_identity_state")
        == "RESOLVED"
    )

    ci = source_ci_evidence or _legacy_ci_evidence(source_ci)
    ci_state = ci.get("state", "NO_RUN")
    if ci_state == "PASS":
        qualification = "PASS"
        qualification_reason = "CI_PASS"
    elif ci_state == "FAIL":
        qualification = "FAIL"
        conclusion = (
            ci.get("conclusion")
            or ci.get("legacy_state")
            or "non-success"
        )
        qualification_reason = (
            f"CI_COMPLETED_NON_SUCCESS:{str(conclusion).upper()}"
        )
    elif ci_state == "RUNNING":
        qualification = "UNKNOWN"
        qualification_reason = "CI_RUNNING"
    else:
        qualification = "UNKNOWN"
        qualification_reason = "NO_CI_RUN"

    return {
        "qualification": qualification,
        "qualification_evidence_state": ci_state,
        "qualification_reason": qualification_reason,
        "source_head_production_verification": (
            "PASS"
            if source_head_smoke == "SUCCESS"
            else "UNKNOWN"
        ),
        "live_production_qualification": (
            "PASS"
            if live_qualified and source_resolved
            else "UNKNOWN"
        ),
        "deployment_identity": (
            release_evidence or {}
        ).get("deployment_identity_state", "UNKNOWN"),
        "artifact_identity": (
            release_evidence or {}
        ).get("artifact_identity_state", "UNKNOWN"),
    }
