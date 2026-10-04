import json
import pathlib
import sys
import tempfile

sys.path.insert(0, "src/engineeringos")

from system_one_observations import append_once, make_observation, summarize

snapshot = {
    "content_sha256": "abc",
    "source_head": "deadbeef",
}
action = {
    "required_assurance": "A2",
    "automation": "REVIEW",
}
item = {
    "item_id": "w1",
    "kind": "REVIEW_OVERLAP",
    "scheduler_lane": "REASONING_REVIEW",
    "model_recommendation": "REASONING_REVIEW",
    "advisory_route": "REASONING_REVIEW",
    "answer_confidence": 0.7,
    "probabilities": {"REASONING_REVIEW": 0.7},
    "human_authority_decision": "NO_HUMAN_AUTHORITY",
    "human_authority_required": False,
    "human_authority_unresolved": False,
    "human_authority_source": "PROJECT_POLICY",
    "human_authority_rule": "kind:REVIEW_OVERLAP",
    "latency_ms": 9.0,
    "model": "typed-decisions",
}
row = make_observation(
    snapshot,
    action,
    item,
    "rev1",
    "processing-lane+authority-policy/v2",
)
assert row["agrees_with_scheduler"] is True
assert row["edb_gold"] is False
assert row["label_strength"] == "WEAK_SCHEDULER_REFERENCE"
assert row["human_authority_source"] == "PROJECT_POLICY"

row2 = make_observation(
    snapshot,
    action,
    item,
    "rev1",
    "processing-lane+authority-policy/v2",
)
assert row2["observation_id"] == row["observation_id"]

legacy = make_observation(
    snapshot,
    action,
    item,
    "rev1",
    "legacy-single-axis/v1",
)
assert legacy["observation_id"] != row["observation_id"]
assert row["routing_contract"] == "processing-lane+authority-policy/v2"

with tempfile.TemporaryDirectory() as td:
    p = pathlib.Path(td) / "obs.jsonl"
    assert append_once(p, row) is True
    assert append_once(p, row2) is False
    saved = [
        json.loads(x)
        for x in p.read_text().splitlines()
        if x.strip()
    ]
    assert len(saved) == 1

bad = dict(row)
bad["observation_id"] = "other"
bad["model_recommendation"] = "DETERMINISTIC_CANDIDATE"
bad["agrees_with_scheduler"] = False
bad["required_assurance"] = "A3"
bad["human_authority_required"] = True
bad["human_authority_decision"] = "HUMAN_AUTHORITY_REQUIRED"

unresolved = dict(row)
unresolved["observation_id"] = "unknown"
unresolved["human_authority_unresolved"] = True
unresolved["human_authority_decision"] = "AUTHORITY_POLICY_UNRESOLVED"

s = summarize([row, bad, unresolved])
assert s["observations"] == 3
assert s["comparable_observations"] == 3
assert abs(s["scheduler_agreement_rate"] - (2/3)) < 1e-9
assert s["high_assurance_disagreements"] == 1
assert s["human_authority_required_decisions"] == 1
assert s["human_authority_unresolved"] == 1
assert s["edb_gold_observations"] == 0

print("14 System-One authority-policy observation invariants passed")
