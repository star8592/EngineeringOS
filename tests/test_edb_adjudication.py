import sys

sys.path.insert(0, "src/engineeringos")

from edb_adjudication import adjudicate


candidate = {
    "candidate_id": "c1",
    "semantic_signature": "sig1",
    "routing_contract": "processing-lane+authority-policy/v2",
    "status": "PENDING_ADJUDICATION",
    "edb_gold": False,
    "kind": "COMMAND_RETRY",
    "reason": "at-most-once semantics",
    "required_assurance": "A3",
    "automation": "BLOCK_UNTIL_RESOLVED",
    "human_authority_decision": "NO_HUMAN_AUTHORITY",
    "source_observation_ids": ["o1", "o2"],
}
blocked = {
    **candidate,
    "candidate_id": "c2",
    "semantic_signature": "sig2",
    "status": "BLOCKED_INCOMPLETE_CONTEXT",
}

valid = {
    "schema_version": 1,
    "candidate_id": "c1",
    "semantic_signature": "sig1",
    "routing_contract": "processing-lane+authority-policy/v2",
    "decision": "ACCEPT_GOLD",
    "expected_lane": "FORMAL_OR_HIGH_ASSURANCE",
    "label_source": "HUMAN_EXPERT",
    "reviewer_ref": "reviewer:engineering",
    "reviewed_at": "2026-10-04T02:40:00+00:00",
    "rationale": "At-most-once semantics require high assurance.",
    "evidence_refs": ["test:command-retry", "adr:021"],
}

gold, summary = adjudicate([candidate, blocked], [valid])
assert len(gold) == 1
assert gold[0]["expected_lane"] == "FORMAL_OR_HIGH_ASSURANCE"
assert gold[0]["expected_human_authority"] == "NO_HUMAN_AUTHORITY"
assert gold[0]["high_risk"] is True
assert gold[0]["metadata"]["label_source"] == "HUMAN_EXPERT"
assert gold[0]["metadata"]["semantic_signature"] == "sig1"
assert summary["gold_count"] == 1
assert summary["pending_adjudication"] == 0
assert summary["blocked_candidates"] == 1
assert summary["auto_adjudication"] is False
assert summary["model_only_gold_allowed"] is False
assert summary["authorization"] == "UNAVAILABLE"

model_only = dict(valid)
model_only["label_source"] = "SYSTEM_ONE_MODEL"
gold2, summary2 = adjudicate([candidate], [model_only])
assert gold2 == []
assert summary2["invalid_count"] == 1
assert summary2["invalid_records"][0]["reason"] == "GOLD_SOURCE_FORBIDDEN"

mismatch = dict(valid)
mismatch["semantic_signature"] = "wrong"
gold3, summary3 = adjudicate([candidate], [mismatch])
assert gold3 == []
assert summary3["invalid_records"][0]["reason"] == "SEMANTIC_SIGNATURE_MISMATCH"

duplicate = [valid, dict(valid)]
gold4, summary4 = adjudicate([candidate], duplicate)
assert len(gold4) == 1
assert summary4["invalid_records"][0]["reason"] == "DUPLICATE_ADJUDICATION"

reject = dict(valid)
reject["decision"] = "REJECT_CANDIDATE"
reject["expected_lane"] = None
reject["label_source"] = None
gold5, summary5 = adjudicate([candidate], [reject])
assert gold5 == []
assert summary5["rejected_count"] == 1
assert summary5["pending_adjudication"] == 0

bad_reject = dict(reject)
bad_reject["expected_lane"] = "REASONING_REVIEW"
gold6, summary6 = adjudicate([candidate], [bad_reject])
assert gold6 == []
assert summary6["invalid_records"][0]["reason"] == "REJECT_MUST_NOT_LABEL"

missing_time = dict(valid)
missing_time["reviewed_at"] = ""
gold7, summary7 = adjudicate([candidate], [missing_time])
assert gold7 == []
assert summary7["invalid_records"][0]["reason"] == "REVIEWED_AT_REQUIRED"

blocked_record = dict(valid)
blocked_record["candidate_id"] = "c2"
blocked_record["semantic_signature"] = "sig2"
gold8, summary8 = adjudicate([candidate, blocked], [blocked_record])
assert gold8 == []
assert summary8["invalid_records"][0]["reason"] == "CANDIDATE_NOT_ADJUDICATABLE"

empty_gold, empty_summary = adjudicate([candidate], [])
assert empty_gold == []
assert empty_summary["gold_count"] == 0
assert empty_summary["pending_adjudication"] == 1

print("24 EDB adjudication invariants passed")
