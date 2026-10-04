import sys

sys.path.insert(0, "src/engineeringos")

from workflow_evidence import classify_workflow_runs


assert classify_workflow_runs(
    [],
    workflow_name="DevControl 3 CI",
)["state"] == "NO_RUN"

running = classify_workflow_runs(
    [
        {
            "workflowName": "DevControl 3 CI",
            "databaseId": 1,
            "headSha": "abc",
            "status": "in_progress",
            "conclusion": "",
            "createdAt": "2026-10-04T00:00:00Z",
            "url": "https://example/runs/1",
        }
    ],
    workflow_name="DevControl 3 CI",
)
assert running["state"] == "RUNNING"
assert running["database_id"] == 1

passed = classify_workflow_runs(
    [
        {
            "workflowName": "DevControl 3 CI",
            "databaseId": 2,
            "headSha": "abc",
            "status": "completed",
            "conclusion": "success",
            "createdAt": "2026-10-04T00:01:00Z",
            "url": "https://example/runs/2",
        }
    ],
    workflow_name="DevControl 3 CI",
)
assert passed["state"] == "PASS"
assert passed["conclusion"] == "success"

failed = classify_workflow_runs(
    [
        {
            "workflowName": "DevControl 3 CI",
            "databaseId": 3,
            "headSha": "abc",
            "status": "completed",
            "conclusion": "failure",
            "createdAt": "2026-10-04T00:02:00Z",
            "url": "https://example/runs/3",
        }
    ],
    workflow_name="DevControl 3 CI",
)
assert failed["state"] == "FAIL"

cancelled = classify_workflow_runs(
    [
        {
            "workflowName": "DevControl 3 CI",
            "databaseId": 4,
            "headSha": "abc",
            "status": "completed",
            "conclusion": "cancelled",
            "createdAt": "2026-10-04T00:03:00Z",
            "url": "https://example/runs/4",
        }
    ],
    workflow_name="DevControl 3 CI",
)
assert cancelled["state"] == "FAIL"
assert cancelled["conclusion"] == "cancelled"

latest = classify_workflow_runs(
    [
        {
            "workflowName": "Other",
            "databaseId": 99,
            "headSha": "abc",
            "status": "completed",
            "conclusion": "success",
            "createdAt": "2026-10-04T00:10:00Z",
            "url": "https://example/other",
        },
        {
            "workflowName": "DevControl 3 CI",
            "databaseId": 5,
            "headSha": "abc",
            "status": "completed",
            "conclusion": "failure",
            "createdAt": "2026-10-04T00:04:00Z",
            "url": "https://example/runs/5",
        },
        {
            "workflowName": "DevControl 3 CI",
            "databaseId": 6,
            "headSha": "abc",
            "status": "completed",
            "conclusion": "success",
            "createdAt": "2026-10-04T00:05:00Z",
            "url": "https://example/runs/6",
        },
    ],
    workflow_name="DevControl 3 CI",
)
assert latest["state"] == "PASS"
assert latest["database_id"] == 6

print("12 workflow-evidence invariants passed")
