import sys

sys.path.insert(0, "src/engineeringos")

from authority_policy import AuthorityPolicyError, decide_authority, validate_policy

policy = {
    "schema_version": 1,
    "project": "Example",
    "default": "AUTHORITY_POLICY_UNRESOLVED",
    "rules": {
        "RUN_TESTS": "NO_HUMAN_AUTHORITY",
        "PRODUCT_SCOPE": "HUMAN_AUTHORITY_REQUIRED",
    },
}
validate_policy(policy)

technical = decide_authority(policy, {"kind": "RUN_TESTS"})
assert technical.decision == "NO_HUMAN_AUTHORITY"
assert technical.source == "PROJECT_POLICY"

product = decide_authority(policy, {"kind": "PRODUCT_SCOPE"})
assert product.decision == "HUMAN_AUTHORITY_REQUIRED"

unknown = decide_authority(policy, {"kind": "NEW_KIND"})
assert unknown.decision == "AUTHORITY_POLICY_UNRESOLVED"

bad = dict(policy)
bad["rules"] = {"X": "ALLOW"}
try:
    validate_policy(bad)
    raise AssertionError("invalid authority policy was accepted")
except AuthorityPolicyError as exc:
    assert str(exc) == "UNKNOWN_AUTHORITY_RULE:X"

print("8 deterministic authority-policy invariants passed")
