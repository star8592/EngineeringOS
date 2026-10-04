import sys

sys.path.insert(0, "src/engineeringos")

from system_one_admission import evaluate_admission

provider_up = {
    "provider": "laya-local",
    "provider_health": {"available": True},
}
provider_down = {
    "provider": "laya-local",
    "provider_health": {"available": False},
}

assert evaluate_admission(provider_down, None)["state"] == "UNAVAILABLE"
assert evaluate_admission(provider_up, None)["state"] == "SHADOW_NO_BENCHMARK"

stale = evaluate_admission(
    provider_up,
    {"schema_version": 1, "cases": 120, "raw_accuracy": 0.99},
)
assert stale["state"] == "SHADOW_BENCHMARK_SCHEMA_STALE"

wrong_contract = evaluate_admission(
    provider_up,
    {
        "schema_version": 2,
        "routing_contract": "processing-lane+human-authority/v2",
        "cases": 120,
    },
)
assert wrong_contract["state"] == "SHADOW_BENCHMARK_SCHEMA_STALE"

small = evaluate_admission(
    provider_up,
    {
        "schema_version": 2,
        "routing_contract": "processing-lane+authority-policy/v2",
        "cases": 12,
        "lane_accuracy": 1.0,
        "high_risk_lane_miss_rate": 0.0,
        "lane_expected_calibration_error": 0.02,
        "authority_policy_accuracy": 1.0,
        "authority_policy_unresolved": 0,
        "authority_policy_mismatches": 0,
    },
)
assert small["state"] == "SHADOW_INSUFFICIENT_EVIDENCE"
assert small["influence_routing"] is False

bad = evaluate_admission(
    provider_up,
    {
        "schema_version": 2,
        "routing_contract": "processing-lane+authority-policy/v2",
        "cases": 120,
        "lane_accuracy": 0.80,
        "high_risk_lane_miss_rate": 0.08,
        "lane_expected_calibration_error": 0.14,
        "authority_policy_accuracy": 0.98,
        "authority_policy_unresolved": 1,
        "authority_policy_mismatches": 2,
    },
)
assert bad["state"] == "SHADOW_UNQUALIFIED"
assert set(bad["failed_metrics"]) == {
    "LANE_ACCURACY",
    "HIGH_RISK_LANE_MISS",
    "LANE_CALIBRATION",
    "AUTHORITY_POLICY_UNRESOLVED",
    "AUTHORITY_POLICY_MISMATCH",
}

good = evaluate_admission(
    provider_up,
    {
        "schema_version": 2,
        "routing_contract": "processing-lane+authority-policy/v2",
        "cases": 150,
        "lane_accuracy": 0.91,
        "high_risk_lane_miss_rate": 0.02,
        "lane_expected_calibration_error": 0.06,
        "authority_policy_accuracy": 1.0,
        "authority_policy_unresolved": 0,
        "authority_policy_mismatches": 0,
    },
)
assert good["state"] == "QUALIFIED_ADVISORY"
assert good["authorization"] == "UNAVAILABLE"
assert good["influence_routing"] is False

print("12 System-One admission invariants passed")
