from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Optional

@dataclass(frozen=True)
class Fact:
    subject: str
    predicate: str
    value: Any
    scope: str
    observed_at: str
    source_type: str
    source_identity: str
    authority: str
    confidence: float = 1.0
    evidence_ref: Optional[str] = None
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None

    def to_dict(self):
        return asdict(self)

@dataclass(frozen=True)
class Contradiction:
    kind: str
    left: Fact
    right: Fact
    reason: str

    def to_dict(self):
        return {"kind": self.kind, "left": self.left.to_dict(), "right": self.right.to_dict(), "reason": self.reason}

def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()

def compatible(a: Fact, b: Fact) -> bool:
    """Only comparable facts may contradict each other."""
    return a.subject == b.subject and a.predicate == b.predicate and a.scope == b.scope

def contradictions(facts: list[Fact]) -> list[Contradiction]:
    out=[]
    for i,a in enumerate(facts):
        for b in facts[i+1:]:
            if compatible(a,b) and a.value != b.value:
                out.append(Contradiction("VALUE_CONTRADICTION",a,b,"same subject/predicate/scope, different values"))
    return out
