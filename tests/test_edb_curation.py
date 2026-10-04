import sys

sys.path.insert(0, "src/engineeringos")

from edb_curation import curate, summarize


def obs(
    oid,
    *,
    kind="RUN_TESTS",
    reason="run deterministic tests",
    assurance="A1",
    automation="DETERMINISTIC",
    scheduler="DETERMINISTIC_CANDIDATE",
    model="DETERMINISTIC_CANDIDATE",
    confidence=0.8,
    unresolved=False,
    contract="processing-lane+authority-policy/v2",
):
    return {
        "observation_id": oid,
        "observed_at": f"2026-10-04T00:00:0{oid[-1]}+00:00",
        "routing_contract": contract,
        "kind": kind,
        "reason": reason,
        "required_assurance": assurance,
        "automation": automation,
        "scheduler_lane": scheduler,
        "model_recommendation": model,
        "model_revision": "rev1",
        "answer_confidence": confidence,
        "probabilities": {model: confidence},
        "human_authority_decision": "NO_HUMAN_AUTHORITY",
        "human_authority_source": "PROJECT_POLICY",
        "human_authority_unresolved": unresolved,
        "comparable": scheduler is not None,
        "agrees_with_scheduler": (
            scheduler == model
            if scheduler is not None
            else None
        ),
        "edb_gold": False,
    }


rows = [
    obs("o1"),
    obs("o2"),
    obs(
        "o3",
        kind="COMMAND_RETRY",
        reason="at-most-once semantics",
        assurance="A3",
        automation="BLOCK_UNTIL_RESOLVED",
        scheduler="FORMAL_OR_HIGH_ASSURANCE",
        model="REASONING_REVIEW",
        confidence=0.41,
    ),
    obs(
        "o4",
        kind="NEW_KIND",
        reason="unknown policy kind",
        assurance="A2",
        automation="REVIEW",
        scheduler="REASONING_REVIEW",
        model="REASONING_REVIEW",
        unresolved=True,
    ),
    obs(
        "o5",
        kind="MISSING_CONTEXT",
        reason=None,
        assurance="A2",
        automation="REVIEW",
        scheduler="REASONING_REVIEW",
        model="REASONING_REVIEW",
    ),
    obs(
        "o6",
        contract="legacy-single-axis/v1",
    ),
]

candidates = curate(rows)
assert len(candidates) == 4

by_kind = {
    row["kind"]: row
    for row in candidates
}

routine = by_kind["RUN_TESTS"]
assert routine["observation_count"] == 2
assert routine["status"] == "PENDING_ADJUDICATION"
assert routine["edb_gold"] is False
assert routine["expected_lane"] is None
assert routine["label_source"] is None

disagreement = by_kind["COMMAND_RETRY"]
assert disagreement["priority"] == 0
assert disagreement["status"] == "PENDING_ADJUDICATION"
assert disagreement["scheduler_references"] == ["FORMAL_OR_HIGH_ASSURANCE"]
assert disagreement["model_recommendations"] == ["REASONING_REVIEW"]

unresolved = by_kind["NEW_KIND"]
assert unresolved["status"] == "BLOCKED_AUTHORITY_POLICY_UNRESOLVED"
assert unresolved["priority"] == 0

incomplete = by_kind["MISSING_CONTEXT"]
assert incomplete["status"] == "BLOCKED_INCOMPLETE_CONTEXT"

summary = summarize(rows, candidates)
assert summary["candidate_count"] == 4
assert summary["pending_adjudication"] == 2
assert summary["blocked_candidates"] == 2
assert summary["gold_candidates"] == 0
assert summary["auto_labeling"] is False
assert summary["authorization"] == "UNAVAILABLE"

print("17 EDB curation invariants passed")
