from __future__ import annotations
import json,pathlib

def assess(candidate:dict,baseline:dict|None)->dict:
    item_id=candidate.get("item_id")
    out={"item_id":item_id,"candidate_state":candidate.get("state"),"source_sha":candidate.get("source_sha"),"state":"NOT_VERIFIED"}
    if candidate.get("state")!="VERIFIED_DEFERRED_CANDIDATE":
        return out
    if not baseline:
        return {**out,"state":"BASELINE_MISSING"}
    if baseline.get("state")=="PROTECTED_EXISTING_WORK":
        return {**out,"state":"WAITING_PROTECTED_WORK"}
    if baseline.get("state")!="CLEAN_CONNECTED":
        return {**out,"state":"BASELINE_NOT_CLEAN"}
    if baseline.get("head")!=candidate.get("source_sha"):
        return {**out,"state":"STALE_SOURCE_REPLAN_REQUIRED","current_head":baseline.get("head")}
    return {**out,"state":"READY_FOR_REVALIDATION"}

def summarize(project_root:str|pathlib.Path)->dict:
    root=pathlib.Path(project_root)
    baseline_path=root/"baseline.json"
    baseline=json.loads(baseline_path.read_text()) if baseline_path.exists() else None
    directory=root/"deferred-candidates"
    items=[]
    if directory.exists():
        for p in sorted(directory.glob("*.json")):
            try:body=json.loads(p.read_text())
            except Exception:continue
            row=assess(body,baseline);row["file"]=p.name;items.append(row)
    counts={}
    for row in items:counts[row["state"]]=counts.get(row["state"],0)+1
    return {"schema_version":1,"items":items,"counts":counts,"verified_candidates":sum(x.get("candidate_state")=="VERIFIED_DEFERRED_CANDIDATE" for x in items)}
