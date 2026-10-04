import json
import pathlib

root = pathlib.Path(".")
laya = json.loads((root / "benchmarks/results/system-one-laya-typed-decisions.json").read_text())
kev = json.loads((root / "benchmarks/results/system-one-decis-kev-0.8b.json").read_text())

for result in (laya, kev):
    assert result["routing_contract"] == "processing-lane+authority-policy/v2"
    assert result["authorization"] == "UNAVAILABLE"
    assert result["influence_routing"] is False
    assert result["authority_policy_accuracy"] == 1.0
    assert result["authority_policy_unresolved"] == 0
    assert result["authority_policy_mismatches"] == 0
    assert result["admission"]["qualified"] is False

assert kev["lane_accuracy"] > laya["lane_accuracy"]
assert kev["high_risk_lane_miss_rate"] < laya["high_risk_lane_miss_rate"]
assert kev["lane_expected_calibration_error"] > 0.10
assert kev["cases"] < 100
assert laya["median_latency_ms"] < kev["median_latency_ms"]

print("13 open System-One backend-matrix invariants passed")
