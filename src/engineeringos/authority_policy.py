from __future__ import annotations

from dataclasses import dataclass
from typing import Any


AUTHORITY_DECISIONS = {
    "NO_HUMAN_AUTHORITY",
    "HUMAN_AUTHORITY_REQUIRED",
    "AUTHORITY_POLICY_UNRESOLVED",
}


class AuthorityPolicyError(ValueError):
    pass


@dataclass(frozen=True)
class AuthorityDecision:
    decision: str
    rule: str
    source: str = "PROJECT_POLICY"

    def validate(self) -> None:
        if self.decision not in AUTHORITY_DECISIONS:
            raise AuthorityPolicyError("UNKNOWN_AUTHORITY_DECISION")
        if not self.rule:
            raise AuthorityPolicyError("AUTHORITY_RULE_REQUIRED")
        if self.source != "PROJECT_POLICY":
            raise AuthorityPolicyError("AUTHORITY_SOURCE_MUST_BE_PROJECT_POLICY")


def decide_authority(policy: dict[str, Any], state: dict[str, Any]) -> AuthorityDecision:
    kind = str(state.get("kind") or state.get("work_kind") or "").strip()
    rules = policy.get("rules") or {}
    if not isinstance(rules, dict):
        raise AuthorityPolicyError("AUTHORITY_RULES_MUST_BE_OBJECT")

    raw = rules.get(kind)
    if raw is None:
        raw = policy.get("default", "AUTHORITY_POLICY_UNRESOLVED")
        rule = f"default:{raw}"
    else:
        rule = f"kind:{kind}"

    decision = AuthorityDecision(
        decision=str(raw),
        rule=rule,
    )
    decision.validate()
    return decision


def validate_policy(policy: dict[str, Any]) -> None:
    if int(policy.get("schema_version", 0)) != 1:
        raise AuthorityPolicyError("UNSUPPORTED_AUTHORITY_POLICY_SCHEMA")
    if not str(policy.get("project") or "").strip():
        raise AuthorityPolicyError("AUTHORITY_POLICY_PROJECT_REQUIRED")

    default = str(policy.get("default", "AUTHORITY_POLICY_UNRESOLVED"))
    if default not in AUTHORITY_DECISIONS:
        raise AuthorityPolicyError("UNKNOWN_AUTHORITY_DEFAULT")

    rules = policy.get("rules") or {}
    if not isinstance(rules, dict):
        raise AuthorityPolicyError("AUTHORITY_RULES_MUST_BE_OBJECT")
    for kind, value in rules.items():
        if not str(kind).strip():
            raise AuthorityPolicyError("AUTHORITY_RULE_KIND_REQUIRED")
        if str(value) not in AUTHORITY_DECISIONS:
            raise AuthorityPolicyError(
                f"UNKNOWN_AUTHORITY_RULE:{kind}"
            )
