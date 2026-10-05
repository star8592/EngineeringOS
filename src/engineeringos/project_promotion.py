from __future__ import annotations
import datetime as dt
import json
import pathlib
from project_registry import load

ALLOWED_TARGETS={"CONNECTED_READ_ONLY","A2_MANAGED"}

class PromotionPolicyError(ValueError):
    pass

def assess(cfg:dict,baseline:dict|None)->dict:
    name=cfg.get("name")
    target=cfg.get("management_target","CONNECTED_READ_ONLY")
    if target not in ALLOWED_TARGETS:
        raise PromotionPolicyError("UNKNOWN_MANAGEMENT_TARGET")
    out={"schema_version":1,"project":name,"display_name":cfg.get("display_name") or name,"target":target,"observed_at":dt.datetime.now(dt.timezone.utc).isoformat(),"eligible":False}
    if target!="A2_MANAGED":
        return {**out,"state":"NOT_REQUESTED","reason":"TARGET_CONNECTED_READ_ONLY"}
    if not baseline:
        return {**out,"state":"BLOCKED","reason":"BASELINE_MISSING"}
    if baseline.get("state")!="CLEAN_CONNECTED":
        return {**out,"state":"BLOCKED","reason":baseline.get("state","BASELINE_INVALID")}
    expected_origin=cfg.get("expected_origin")
    if expected_origin and baseline.get("origin")!=expected_origin:
        return {**out,"state":"BLOCKED","reason":"ORIGIN_DRIFT"}
    managed_branch=cfg.get("managed_branch","main")
    if baseline.get("branch")!=managed_branch:
        return {**out,"state":"BLOCKED","reason":"BRANCH_DRIFT"}
    if baseline.get("upstream") and baseline.get("upstream")!=f"origin/{managed_branch}":
        return {**out,"state":"BLOCKED","reason":"UPSTREAM_DRIFT"}
    if baseline.get("ahead") not in (None,0) or baseline.get("behind") not in (None,0):
        return {**out,"state":"BLOCKED","reason":"UPSTREAM_DIVERGENCE"}
    verification=cfg.get("a2_verification_entrypoint")
    if not verification:
        return {**out,"state":"BLOCKED","reason":"A2_VERIFICATION_ENTRYPOINT_REQUIRED"}
    if verification not in set(baseline.get("verification_entrypoints") or []):
        return {**out,"state":"BLOCKED","reason":"A2_VERIFICATION_ENTRYPOINT_DRIFT"}
    if cfg.get("max_assurance") not in ("A1","A2"):
        return {**out,"state":"BLOCKED","reason":"SAFE_ASSURANCE_CEILING_REQUIRED"}
    if not cfg.get("workspace_root"):
        return {**out,"state":"BLOCKED","reason":"WORKSPACE_ROOT_REQUIRED"}
    return {**out,"state":"ELIGIBLE_FOR_A2","reason":"ALL_PROMOTION_GATES_PASS","eligible":True,"baseline_head":baseline.get("head"),"verification_entrypoint":verification}

def assess_registered(registry_path,runtime_root)->dict:
    registry=load(registry_path)
    rows=[]
    for cfg in registry.get("projects",[]):
        bp=pathlib.Path(runtime_root)/"projects"/cfg["name"]/"baseline.json"
        baseline=json.loads(bp.read_text()) if bp.exists() else None
        rows.append(assess(cfg,baseline))
    return {"schema_version":1,"observed_at":dt.datetime.now(dt.timezone.utc).isoformat(),"projects":rows}
