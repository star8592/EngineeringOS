from __future__ import annotations

def assess(evidence:dict|None,*,require_host_acceptance:bool=False)->dict:
    if not evidence:
        return {"decision":"DENY","reason":"BACKEND_SURFACE_EVIDENCE_MISSING"}
    if evidence.get("state")!="OBSERVED_MATCH":
        return {"decision":"DENY","reason":"TOOL_SURFACE_DRIFT"}
    if evidence.get("source_live_check")!="PASS":
        return {"decision":"DENY","reason":"SOURCE_LIVE_SURFACE_NOT_VERIFIED"}
    if evidence.get("host_observable_contract_check")!="PASS":
        return {"decision":"DENY","reason":"HOST_OBSERVABLE_SURFACE_NOT_VERIFIED"}
    if require_host_acceptance and evidence.get("host_acceptance")!="ACCEPTED":
        return {"decision":"DENY","reason":"HOST_ACCEPTANCE_REQUIRED"}
    return {"decision":"ALLOW","reason":"BACKEND_SURFACE_CONVERGED","host_acceptance":evidence.get("host_acceptance")}
