import sys

sys.path.insert(0, "src/engineeringos")

from system_one_contract import (
    PROCESSING_LANES,
    ROUTES,
    AdvisoryDecision,
    SystemOneContractError,
    TypedQuestion,
    advisory_route,
    assert_not_authorization,
    build_jev_request,
)

q = TypedQuestion(
    question_id="engineering_lane",
    kind="choice",
    instructions="Which processing lane is appropriate?",
    options=tuple(sorted(PROCESSING_LANES)),
    criteria=(
        ("DETERMINISTIC_CANDIDATE", "mechanically checkable"),
        ("REASONING_REVIEW", "ambiguous engineering judgment"),
        ("FORMAL_OR_HIGH_ASSURANCE", "safety-critical invariants"),
    ),
)
payload = build_jev_request(
    state={"kind": "example"},
    model="local-open-system-one",
    questions=(q,),
)
assert payload["questions"]["engineering_lane"]["type"] == "choice"
assert set(payload["questions"]["engineering_lane"]["criteria"]) == PROCESSING_LANES
assert "HUMAN_REVIEW" not in PROCESSING_LANES
assert "HUMAN_REVIEW" in ROUTES

high_conf = AdvisoryDecision(
    source="laya-local",
    question_id="engineering_lane",
    recommended_route="DETERMINISTIC_CANDIDATE",
    confidence=0.94,
    raw_answer="DETERMINISTIC_CANDIDATE",
)
r = advisory_route(high_conf)
assert r["recommended_route"] == "DETERMINISTIC_CANDIDATE"
assert r["authorization"] == "UNAVAILABLE"
assert_not_authorization(r)

low_conf = AdvisoryDecision(
    source="laya-local",
    question_id="engineering_lane",
    recommended_route="DETERMINISTIC_CANDIDATE",
    confidence=0.51,
    raw_answer="DETERMINISTIC_CANDIDATE",
)
assert advisory_route(low_conf)["recommended_route"] == "REASONING_REVIEW"
assert advisory_route(high_conf, high_risk=True)["recommended_route"] == "FORMAL_OR_HIGH_ASSURANCE"

bad = TypedQuestion(
    question_id="bad",
    kind="choice",
    instructions="bad criteria",
    options=("A", "B"),
    criteria=(("A", "only A"),),
)
try:
    bad.validate()
    raise AssertionError("mismatched criteria were accepted")
except SystemOneContractError as exc:
    assert str(exc) == "CHOICE_CRITERIA_KEYS_MUST_MATCH_OPTIONS"

try:
    assert_not_authorization({"authorization": "ALLOW", "advisory_only": False})
    raise AssertionError("authorization drift was not rejected")
except SystemOneContractError as exc:
    assert str(exc) == "SYSTEM_ONE_MUST_NOT_AUTHORIZE"

print("11 System-One processing-lane contract invariants passed")
