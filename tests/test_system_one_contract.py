import sys

sys.path.insert(0, "src/engineeringos")

from system_one_contract import (
    AdvisoryDecision,
    SystemOneContractError,
    TypedQuestion,
    advisory_route,
    assert_not_authorization,
    build_jev_request,
)

q = TypedQuestion(
    question_id="lane",
    kind="choice",
    instructions="Which assurance lane is appropriate?",
    options=(
        "DETERMINISTIC_CANDIDATE",
        "REASONING_REVIEW",
        "FORMAL_OR_HIGH_ASSURANCE",
        "HUMAN_REVIEW",
    ),
)
payload = build_jev_request(state={"kind": "example"}, model="typesafe/jev-1.13", questions=(q,))
assert payload["questions"]["lane"]["type"] == "choice"
assert len(payload["questions"]["lane"]["options"]) == 4

high_conf = AdvisoryDecision(
    source="jev",
    question_id="lane",
    recommended_route="DETERMINISTIC_CANDIDATE",
    confidence=0.94,
    raw_answer="DETERMINISTIC_CANDIDATE",
)
r = advisory_route(high_conf)
assert r["recommended_route"] == "DETERMINISTIC_CANDIDATE"
assert r["authorization"] == "UNAVAILABLE"
assert_not_authorization(r)

low_conf = AdvisoryDecision(
    source="jev",
    question_id="lane",
    recommended_route="DETERMINISTIC_CANDIDATE",
    confidence=0.51,
    raw_answer="DETERMINISTIC_CANDIDATE",
)
assert advisory_route(low_conf)["recommended_route"] == "REASONING_REVIEW"
assert advisory_route(high_conf, high_risk=True)["recommended_route"] == "FORMAL_OR_HIGH_ASSURANCE"

try:
    assert_not_authorization({"authorization": "ALLOW", "advisory_only": False})
    raise AssertionError("authorization drift was not rejected")
except SystemOneContractError as exc:
    assert str(exc) == "SYSTEM_ONE_MUST_NOT_AUTHORIZE"

print("7 System-One/Jev advisory contract invariants passed")
