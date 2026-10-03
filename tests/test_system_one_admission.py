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

down = evaluate_admission(provider_down, None)
assert down["state"] == "UNAVAILABLE"

no_bench = evaluate_admission(provider_up, None)
assert no_bench["state"] == "SHADOW_NO_BENCHMARK"

stale = evaluate_admission(
    provider_up,
    {
        "schema_version": 1,
        "cases": 120,
        "raw_accuracy": 0.99,
    },
)
assert (
    stale["state"]
    == "SHADOW_BENCHMARK_SCHEMA_STALE"
)

small = evaluate_admission(
    provider_up,
    {
        "schema_version": 2,
        "cases": 12,
        "lane_accuracy": 1.0,
        "human_authority_accuracy": 1.0,
        "high_risk_lane_miss_rate": 0.0,
        "human_authority_miss_rate": 0.0,
        "lane_expected_calibration_error": 0.02,
        "human_authority_expected_calibration_error": 0.03,
    },
)
assert (
    small["state"]
    == "SHADOW_INSUFFICIENT_EVIDENCE"
)
assert small["influence_routing"] is False

bad = evaluate_admission(
    provider_up,
    {
        "schema_version": 2,
        "cases": 120,
        "lane_accuracy": 0.80,
        "human_authority_accuracy": 0.82,
        "high_risk_lane_miss_rate": 0.08,
        "human_authority_miss_rate": 0.10,
        "lane_expected_calibration_error": 0.14,
        "human_authority_expected_calibration_error": 0.18,
    },
)
assert bad["state"] == "SHADOW_UNQUALIFIED"
assert set(bad["failed_metrics"]) == {
    "LANE_ACCURACY",
    "HUMAN_AUTHORITY_ACCURACY",
    "HIGH_RISK_LANE_MISS",
    "HUMAN_AUTHORITY_MISS",
    "LANE_CALIBRATION",
    "HUMAN_AUTHORITY_CALIBRATION",
}

good = evaluate_admission(
    provider_up,
    {
        "schema_version": 2,
        "cases": 150,
        "lane_accuracy": 0.91,
        "human_authority_accuracy": 0.94,
        "high_risk_lane_miss_rate": 0.02,
        "human_authority_miss_rate": 0.03,
        "lane_expected_calibration_error": 0.06,
        "human_authority_expected_calibration_error": 0.07,
    },
)
assert good["state"] == "QUALIFIED_ADVISORY"
assert good["authorization"] == "UNAVAILABLE"
assert good["influence_routing"] is False

print("14 System-One two-axis admission invariants passed")
