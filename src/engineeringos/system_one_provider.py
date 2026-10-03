from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from system_one_contract import AdvisoryDecision, TypedQuestion


class SystemOneProviderError(RuntimeError):
    pass


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

    def decide(self, *, state: Any, question: TypedQuestion) -> ProviderResult:
        ...
