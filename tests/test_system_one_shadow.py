import sys

sys.path.insert(0, "src/engineeringos")

from system_one_provider import BatchProviderResult, ChoiceResult
from system_one_shadow import classify_action


class FakeProvider:
    name = "laya-local"

    def decide_many(self, *, state, questions):
        assert len(questions) == 2
        return BatchProviderResult(
            answers={
                "engineering_lane": ChoiceResult(
                    question_id="engineering_lane",
                    choice="DETERMINISTIC_CANDIDATE",
                    answer_confidence=0.93,
                    probabilities={
                        "DETERMINISTIC_CANDIDATE": 0.93,
                        "REASONING_REVIEW": 0.04,
                        "FORMAL_OR_HIGH_ASSURANCE": 0.03,
                    },
                    raw_answer={
                        "choice": "DETERMINISTIC_CANDIDATE"
                    },
                ),
                "human_authority": ChoiceResult(
                    question_id="human_authority",
                    choice="HUMAN_AUTHORITY_REQUIRED",
                    answer_confidence=0.81,
                    probabilities={
                        "HUMAN_AUTHORITY_REQUIRED": 0.81,
                        "NO_HUMAN_AUTHORITY": 0.19,
                    },
                    raw_answer={
                        "choice": "HUMAN_AUTHORITY_REQUIRED"
                    },
                ),
            },
            model="typed-decisions",
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
assert low["human_authority_required"] is True
assert low["human_authority_confidence"] == 0.81
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
assert high["human_authority_required"] is True
assert high["authorization"] == "UNAVAILABLE"

print("10 Laya two-axis shadow-routing invariants passed")
