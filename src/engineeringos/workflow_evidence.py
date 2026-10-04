from __future__ import annotations

from typing import Any


QUALIFICATION_STATES = {"NO_RUN", "RUNNING", "PASS", "FAIL"}


def classify_workflow_runs(
    runs: list[dict[str, Any]],
    *,
    workflow_name: str,
) -> dict[str, Any]:
    matches = [
        row
        for row in runs
        if row.get("workflowName") == workflow_name
    ]
    if not matches:
        return {
            "state": "NO_RUN",
            "workflow_name": workflow_name,
            "latest_run": None,
        }

    latest = sorted(
        matches,
        key=lambda row: (
            str(row.get("createdAt") or ""),
            int(row.get("databaseId") or 0),
        ),
        reverse=True,
    )[0]
    status = str(latest.get("status") or "").lower()
    conclusion = str(latest.get("conclusion") or "").lower()

    if status != "completed":
        state = "RUNNING"
    elif conclusion == "success":
        state = "PASS"
    else:
        state = "FAIL"

    return {
        "state": state,
        "workflow_name": workflow_name,
        "latest_run": latest,
        "status": status or None,
        "conclusion": conclusion or None,
        "url": latest.get("url"),
        "database_id": latest.get("databaseId"),
        "head_sha": latest.get("headSha"),
    }
