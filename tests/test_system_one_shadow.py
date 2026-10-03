import sys

sys.path.insert(0, "src/engineeringos")

from system_one_contract import AdvisoryDecision
from system_one_provider import ProviderResult
from system_one_shadow import classify_action


class FakeProvider:
    def decide(self, *, state, question):
        decision = AdvisoryDecision(
            source="laya-local",
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
                "FORMAL_OR_HIGH_ASSURANCE": 0.02,
                "HUMAN_REVIEW": 0.01,
            },
            latency_ms=11.0,
            raw={},
        )


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
)
assert low["advisory_route"] == "DETERMINISTIC_CANDIDATE"
assert low["authorization"] == "UNAVAILABLE"
assert low["advisory_only"] is True

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
)
assert high["model_recommendation"] == "DETERMINISTIC_CANDIDATE"
assert high["advisory_route"] == "FORMAL_OR_HIGH_ASSURANCE"
assert high["policy_override"] is True
assert high["authorization"] == "UNAVAILABLE"

print("8 Laya shadow-routing invariants passed")
