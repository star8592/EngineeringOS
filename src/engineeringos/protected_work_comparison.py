from __future__ import annotations

def compare(baseline:dict,dirty:dict)->dict:
    if not baseline or not dirty:
        return {"state":"INCOMPLETE_EVIDENCE","dirty_verified":False,"dirty_regression_proven":False}
    if not baseline.get("source_unchanged") or not dirty.get("source_unchanged"):
        return {"state":"SOURCE_CHANGED_DURING_COMPARISON","dirty_verified":False,"dirty_regression_proven":False}
    if baseline.get("source_head")!=dirty.get("source_head"):
        return {"state":"SOURCE_SHA_MISMATCH","dirty_verified":False,"dirty_regression_proven":False}
    bp=baseline.get("state")=="PASS";dp=dirty.get("state")=="PASS"
    if bp and dp:
        state="DIRTY_VERIFIED"
    elif bp and not dp:
        state="DIRTY_REGRESSION"
    elif not bp and dp:
        state="DIRTY_IMPROVES_BASELINE"
    else:
        bs=baseline.get("diagnostic_signature") or {}
        ds=dirty.get("diagnostic_signature") or {}
        same=bool(bs.get("sha256") and bs.get("sha256")==ds.get("sha256"))
        state="BASELINE_RED_SAME_FAILURE" if same else "INCONCLUSIVE_DIFFERENT_FAILURE"
    return {
        "schema_version":1,
        "state":state,
        "source_head":baseline.get("source_head"),
        "baseline_state":baseline.get("state"),
        "dirty_state":dirty.get("state"),
        "baseline_failure_stage":(baseline.get("diagnostic_signature") or {}).get("failure_stage"),
        "dirty_failure_stage":(dirty.get("diagnostic_signature") or {}).get("failure_stage"),
        "same_failure_signature":bool((baseline.get("diagnostic_signature") or {}).get("sha256") and (baseline.get("diagnostic_signature") or {}).get("sha256")==((dirty.get("diagnostic_signature") or {}).get("sha256"))),
        "dirty_verified":state=="DIRTY_VERIFIED",
        "dirty_regression_proven":state=="DIRTY_REGRESSION",
        "authority":"DIFFERENTIAL_ISOLATED_VERIFICATION",
    }
