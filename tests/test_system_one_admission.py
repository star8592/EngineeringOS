import sys
sys.path.insert(0,"src/engineeringos")
from system_one_admission import evaluate_admission

down=evaluate_admission({"provider":"laya-local","provider_health":{"available":False}},None)
assert down["state"]=="UNAVAILABLE"

no_bench=evaluate_admission({"provider":"laya-local","provider_health":{"available":True}},None)
assert no_bench["state"]=="SHADOW_NO_BENCHMARK"

small=evaluate_admission({"provider":"laya-local","provider_health":{"available":True}},{"cases":12,"raw_accuracy":1.0,"high_risk_raw_miss_rate":0.0,"expected_calibration_error":0.02})
assert small["state"]=="SHADOW_INSUFFICIENT_EVIDENCE"
assert small["influence_routing"] is False

bad=evaluate_admission({"provider":"laya-local","provider_health":{"available":True}},{"cases":120,"raw_accuracy":0.80,"high_risk_raw_miss_rate":0.08,"expected_calibration_error":0.14})
assert bad["state"]=="SHADOW_UNQUALIFIED"
assert set(bad["failed_metrics"])=={"RAW_ACCURACY","HIGH_RISK_MISS","CALIBRATION"}

good=evaluate_admission({"provider":"laya-local","provider_health":{"available":True}},{"cases":150,"raw_accuracy":0.91,"high_risk_raw_miss_rate":0.02,"expected_calibration_error":0.06})
assert good["state"]=="QUALIFIED_ADVISORY"
assert good["authorization"]=="UNAVAILABLE"
assert good["influence_routing"] is False
print("11 System-One admission invariants passed")
