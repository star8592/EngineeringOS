from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from system_one_contract import AdvisoryDecision, TypedQuestion


class SystemOneProviderError(RuntimeError):
    pass


@dataclass(frozen=True)
class ChoiceResult:
    question_id: str
    choice: str
    answer_confidence: float
    probabilities: dict[str, float]
    raw_answer: dict[str, Any]


@dataclass(frozen=True)
class BatchProviderResult:
    answers: dict[str, ChoiceResult]
    model: str
    latency_ms: float | None
    raw: dict[str, Any]


@dataclass(frozen=True)
class ProviderResult:
    decision: AdvisoryDecision
    model: str
    answer_confidence: float
    probabilities: dict[str, float]
    latency_ms: float | None
    raw: dict[str, Any]


class SystemOneProvider(Protocol):
    name: str

    def health(self) -> dict[str, Any]:
        ...

    def decide_many(self, *, state: Any, questions: tuple[TypedQuestion, ...]) -> BatchProviderResult:
        ...

    def decide(self, *, state: Any, question: TypedQuestion) -> ProviderResult:
        ...
