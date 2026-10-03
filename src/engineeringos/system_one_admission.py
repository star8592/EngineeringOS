from __future__ import annotations

import datetime as dt
import json
import os
import pathlib
import tempfile

from state_paths import runtime

STATE = runtime()

DEFAULT_MIN_CASES = 100
DEFAULT_MIN_RAW_ACCURACY = 0.85
DEFAULT_MAX_HIGH_RISK_MISS = 0.05
DEFAULT_MAX_ECE = 0.10

def utcnow() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()

def atomic_json(path: pathlib.Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw=(json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False)+"\n").encode()
    fd,tmp=tempfile.mkstemp(prefix=path.name+".",suffix=".tmp",dir=path.parent)
    try:
        with os.fdopen(fd,"wb") as handle:
            handle.write(raw); handle.flush(); os.fsync(handle.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def evaluate_admission(provider_projection: dict | None, edb_report: dict | None) -> dict:
    health=(provider_projection or {}).get("provider_health") or {}
    base={
        "schema_version": 1,
        "generated_at": utcnow(),
        "provider": (provider_projection or {}).get("provider","laya-local"),
        "advisory_only": True,
        "authorization": "UNAVAILABLE",
        "influence_routing": False,
        "thresholds": {
            "min_cases": DEFAULT_MIN_CASES,
            "min_raw_accuracy": DEFAULT_MIN_RAW_ACCURACY,
            "max_high_risk_raw_miss_rate": DEFAULT_MAX_HIGH_RISK_MISS,
            "max_ece": DEFAULT_MAX_ECE,
        },
    }
    if not health.get("available"):
        return {**base,"state":"UNAVAILABLE","reason":"PROVIDER_UNAVAILABLE"}
    if not edb_report:
        return {**base,"state":"SHADOW_NO_BENCHMARK","reason":"EDB_MISSING"}

    cases=int(edb_report.get("cases",0))
    raw=float(edb_report.get("raw_accuracy",0.0))
    miss=float(edb_report.get("high_risk_raw_miss_rate",1.0))
    ece=float(edb_report.get("expected_calibration_error",1.0))
    metrics={"cases":cases,"raw_accuracy":raw,"high_risk_raw_miss_rate":miss,"expected_calibration_error":ece}
    if cases < DEFAULT_MIN_CASES:
        return {**base,"state":"SHADOW_INSUFFICIENT_EVIDENCE","reason":"EDB_CASE_COUNT_BELOW_THRESHOLD","metrics":metrics}
    failures=[]
    if raw < DEFAULT_MIN_RAW_ACCURACY: failures.append("RAW_ACCURACY")
    if miss > DEFAULT_MAX_HIGH_RISK_MISS: failures.append("HIGH_RISK_MISS")
    if ece > DEFAULT_MAX_ECE: failures.append("CALIBRATION")
    if failures:
        return {**base,"state":"SHADOW_UNQUALIFIED","reason":"EDB_THRESHOLD_FAILURE","failed_metrics":failures,"metrics":metrics}
    return {**base,"state":"QUALIFIED_ADVISORY","reason":"EDB_THRESHOLDS_PASS","metrics":metrics}

def run() -> dict:
    projection_path=STATE/"system-one/projection.json"
    edb_path=STATE/"system-one/edb-latest.json"
    provider=json.loads(projection_path.read_text()) if projection_path.exists() else None
    edb=json.loads(edb_path.read_text()) if edb_path.exists() else None
    result=evaluate_admission(provider,edb)
    atomic_json(STATE/"system-one/admission.json",result)
    return result

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
