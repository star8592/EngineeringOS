import sys

sys.path.insert(0, "src/engineeringos")

from action_details import build_action_details


brief = {
    "project": "DevControl",
    "snapshot_content_sha256": "abc",
    "actions": [
        {
            "item_id": "w1",
            "kind": "RESOLVE_MAIN_QUALIFICATION",
            "priority": 1,
        }
    ],
}
plane = {
    "origin_main": "b07fb9e7",
    "workflow_query": {
        "state": "OK",
        "returncode": 0,
    },
    "current_head_evidence": {
        "ci_evidence": {
            "state": "NO_RUN",
            "workflow_name": "DevControl 3 CI",
            "latest_run": None,
        }
    },
    "interpretation": {
        "qualification": "UNKNOWN",
        "qualification_evidence_state": "NO_RUN",
        "qualification_reason": "NO_CI_RUN",
    },
}
out = build_action_details(
    brief,
    {"dimensions": {}},
    {},
    plane,
)
item = out["items"][0]
assert item["evidence_count"] == 1
assert item["evidence"][0]["origin_main"] == "b07fb9e7"
assert (
    item["evidence"][0]["qualification_evidence_state"]
    == "NO_RUN"
)
assert (
    item["evidence"][0]["workflow_query"]["state"]
    == "OK"
)
assert "canonical DevControl 3 CI" in item["suggested_resolution"][0]
assert "ancestor commit" in item["suggested_resolution"][1]
assert item["target_mutation_authorized"] is False

running_plane = {
    **plane,
    "current_head_evidence": {
        "ci_evidence": {
            "state": "RUNNING",
            "workflow_name": "DevControl 3 CI",
            "status": "in_progress",
        }
    },
    "interpretation": {
        "qualification": "UNKNOWN",
        "qualification_evidence_state": "RUNNING",
        "qualification_reason": "CI_RUNNING",
    },
}
running = build_action_details(
    brief,
    {"dimensions": {}},
    {},
    running_plane,
)["items"][0]
assert "await the existing" in running["suggested_resolution"][0]
assert "do not start a duplicate" in running["suggested_resolution"][1]

print("11 qualification action-detail invariants passed")
