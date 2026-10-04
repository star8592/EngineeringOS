import sys

sys.path.insert(0, "src/engineeringos")

from system_one_contract import AdvisoryDecision
from system_one_provider import ProviderResult
from system_one_shadow import classify_action


class FakeProvider:
    name = "laya-local"

    def decide(self, *, state, question):
        decision = AdvisoryDecision(
            source=self.name,
            question_id=question.question_id,
            recommended_route="DETERMINISTIC_CANDIDATE",
            confidence=0.93,
            raw_answer={"choice": "DETERMINISTIC_CANDIDATE"},
        )
        return ProviderResult(
            decision=decision,
            model="typed-decisions",
            answer_confidence=0.93,
            probabilities={
                "DETERMINISTIC_CANDIDATE": 0.93,
                "REASONING_REVIEW": 0.04,
                "FORMAL_OR_HIGH_ASSURANCE": 0.03,
            },
            latency_ms=11.0,
            raw={},
        )


policy = {
    "schema_version": 1,
    "project": "DevControl",
    "default": "AUTHORITY_POLICY_UNRESOLVED",
    "rules": {
        "RUN_TESTS": "NO_HUMAN_AUTHORITY",
        "AUTH_POLICY": "HUMAN_AUTHORITY_REQUIRED",
        "APPROVAL_SEMANTICS": "NO_HUMAN_AUTHORITY",
    },
}

low = classify_action(
    FakeProvider(),
    {
        "item_id": "w1",
        "kind": "RUN_TESTS",
        "reason": "deterministic",
        "required_assurance": "A1",
        "automation": "DETERMINISTIC",
        "lane": "DETERMINISTIC",
        "schedule_state": "DISPATCHABLE",
    },
    authority_policy=policy,
)
assert low["advisory_route"] == "DETERMINISTIC_CANDIDATE"
assert low["human_authority_required"] is False
assert low["human_authority_source"] == "PROJECT_POLICY"
assert low["authorization"] == "UNAVAILABLE"

high = classify_action(
    FakeProvider(),
    {
        "item_id": "w2",
        "kind": "APPROVAL_SEMANTICS",
        "reason": "authorization state machine",
        "required_assurance": "A3",
        "automation": "BLOCK_UNTIL_RESOLVED",
        "lane": "FORMAL_OR_HIGH_ASSURANCE",
        "schedule_state": "DISPATCHABLE",
    },
    authority_policy=policy,
)
assert high["model_recommendation"] == "DETERMINISTIC_CANDIDATE"
assert high["advisory_route"] == "FORMAL_OR_HIGH_ASSURANCE"
assert high["policy_override"] is True
assert high["human_authority_required"] is False

auth = classify_action(
    FakeProvider(),
    {
        "item_id": "w3",
        "kind": "AUTH_POLICY",
        "reason": "grant privilege",
        "required_assurance": "A5",
        "automation": "BLOCK_UNTIL_RESOLVED",
        "lane": "FORMAL_OR_HIGH_ASSURANCE",
        "schedule_state": "BLOCKED",
    },
    authority_policy=policy,
)
assert auth["advisory_route"] == "FORMAL_OR_HIGH_ASSURANCE"
assert auth["human_authority_required"] is True
assert auth["human_authority_rule"] == "kind:AUTH_POLICY"
assert auth["authorization"] == "UNAVAILABLE"

unknown = classify_action(
    FakeProvider(),
    {
        "item_id": "w4",
        "kind": "UNKNOWN_KIND",
        "reason": "new work type",
        "required_assurance": "A2",
        "automation": "REVIEW",
        "lane": "REASONING_REVIEW",
        "schedule_state": "BLOCKED",
    },
    authority_policy=policy,
)
assert unknown["human_authority_unresolved"] is True
assert unknown["human_authority_decision"] == "AUTHORITY_POLICY_UNRESOLVED"

print("15 Laya lane + deterministic authority invariants passed")
