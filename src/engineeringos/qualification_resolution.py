from __future__ import annotations

from typing import Any


def qualification_work_item(
    interpretation: dict[str, Any],
) -> dict[str, Any] | None:
    qualification = interpretation.get("qualification")
    evidence_state = interpretation.get(
        "qualification_evidence_state",
        "NO_RUN",
    )
    reason_code = interpretation.get(
        "qualification_reason",
        "NO_CI_RUN",
    )

    if qualification == "PASS":
        return None

    if qualification == "FAIL":
        return {
            "priority": 0,
            "kind": "RESTORE_MAIN_QUALIFICATION",
            "reason": (
                "current authoritative source head did not qualify: "
                + reason_code
            ),
            "required_assurance": "A2",
            "automation": "BLOCK_UNTIL_RESOLVED",
            "evidence_state": evidence_state,
            "reason_code": reason_code,
        }

    if evidence_state == "RUNNING":
        reason = (
            "current authoritative source head CI is still running"
        )
    elif evidence_state == "QUERY_ERROR":
        reason = (
            "current authoritative source-head workflow evidence "
            "query failed"
        )
    elif evidence_state == "NO_RUN":
        reason = (
            "current authoritative source head has no DevControl 3 CI run"
        )
    else:
        reason = (
            "current authoritative source-head qualification evidence "
            f"is unresolved ({evidence_state})"
        )

    return {
        "priority": 1,
        "kind": "RESOLVE_MAIN_QUALIFICATION",
        "reason": reason,
        "required_assurance": "A2",
        "automation": "REVIEW",
        "evidence_state": evidence_state,
        "reason_code": reason_code,
    }
