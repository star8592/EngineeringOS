from __future__ import annotations

from dataclasses import dataclass
from typing import Any


QUESTION_TYPES = {"choice", "score", "noul"}
PROCESSING_LANES = {
    "DETERMINISTIC_CANDIDATE",
    "REASONING_REVIEW",
    "FORMAL_OR_HIGH_ASSURANCE",
}
# Backward-compatible legacy route domain for persisted evidence/readers.
ROUTES = PROCESSING_LANES | {"HUMAN_REVIEW"}


class SystemOneContractError(ValueError):
    pass


@dataclass(frozen=True)
class TypedQuestion:
    question_id: str
    kind: str
    instructions: str
    options: tuple[str, ...] = ()
    criteria: tuple[tuple[str, str], ...] = ()

    def validate(self) -> None:
        if not self.question_id:
            raise SystemOneContractError("QUESTION_ID_REQUIRED")
        if self.kind not in QUESTION_TYPES:
            raise SystemOneContractError("UNKNOWN_QUESTION_TYPE")
        if not self.instructions.strip():
            raise SystemOneContractError("QUESTION_INSTRUCTIONS_REQUIRED")
        if self.kind == "choice" and len(self.options) < 2:
            raise SystemOneContractError("CHOICE_OPTIONS_REQUIRED")
        if self.criteria:
            criteria = dict(self.criteria)
            if set(criteria) != set(self.options):
                raise SystemOneContractError("CHOICE_CRITERIA_KEYS_MUST_MATCH_OPTIONS")
            if any(not str(value).strip() for value in criteria.values()):
                raise SystemOneContractError("CHOICE_CRITERIA_REQUIRED")


@dataclass(frozen=True)
class AdvisoryDecision:
    source: str
    question_id: str
    recommended_route: str
    confidence: float
    raw_answer: Any

    def validate(self) -> None:
        if self.recommended_route not in ROUTES:
            raise SystemOneContractError("UNKNOWN_ROUTE")
        if not 0.0 <= self.confidence <= 1.0:
            raise SystemOneContractError("INVALID_CONFIDENCE")


def build_jev_request(*, state: Any, model: str, questions: tuple[TypedQuestion, ...]) -> dict:
    if not model:
        raise SystemOneContractError("MODEL_REQUIRED")
    payload_questions: dict[str, dict[str, Any]] = {}
    for q in questions:
        q.validate()
        body: dict[str, Any] = {"type": q.kind, "instructions": q.instructions}
        if q.kind == "choice":
            if q.criteria:
                body["criteria"] = dict(q.criteria)
            else:
                body["options"] = list(q.options)
        payload_questions[q.question_id] = body
    return {"state": state, "model": model, "questions": payload_questions}


def advisory_route(
    decision: AdvisoryDecision,
    *,
    min_confidence: float = 0.85,
    high_risk: bool = False,
) -> dict:
    """Convert a typed System-One result into advisory routing evidence only."""
    decision.validate()
    if high_risk:
        route = "FORMAL_OR_HIGH_ASSURANCE"
        reason = "HIGH_RISK_ESCALATION"
    elif decision.confidence < min_confidence:
        route = "REASONING_REVIEW"
        reason = "LOW_CONFIDENCE_ESCALATION"
    else:
        route = decision.recommended_route
        reason = "SYSTEM_ONE_RECOMMENDATION"
    return {
        "source": decision.source,
        "question_id": decision.question_id,
        "recommended_route": route,
        "confidence": decision.confidence,
        "reason": reason,
        "authorization": "UNAVAILABLE",
        "advisory_only": True,
    }


def assert_not_authorization(result: dict) -> None:
    if result.get("authorization") != "UNAVAILABLE" or result.get("advisory_only") is not True:
        raise SystemOneContractError("SYSTEM_ONE_MUST_NOT_AUTHORIZE")
