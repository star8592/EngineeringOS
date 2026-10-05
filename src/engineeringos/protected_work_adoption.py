from __future__ import annotations
import hashlib,json

def inventory_identity(inv:dict)->str:
 rows=[{"path":x.get("path"),"status":x.get("status"),"fingerprint":x.get("fingerprint"),"size":x.get("size"),"sensitive":x.get("sensitive")} for x in inv.get("paths",[])]
 raw=json.dumps({"head":inv.get("head"),"paths":rows},sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()
 return hashlib.sha256(raw).hexdigest()

def assess(cfg:dict,baseline:dict|None,inventory:dict|None,deferred:dict|None,repair:dict|None,activity:dict|None,plan:dict|None)->dict:
 name=cfg.get("name")
 out={"schema_version":1,"project":name,"eligible":False,"state":"BLOCKED","authority":"ADOPTION_GATE_ONLY_NO_MUTATION"}
 if cfg.get("protected_work_policy")!="ADOPT_VERIFIED_QUIET":
  return {**out,"reason":"PROTECTED_WORK_ADOPTION_NOT_AUTHORIZED"}
 if cfg.get("management_target")!="A2_MANAGED":
  return {**out,"reason":"A2_MANAGEMENT_TARGET_REQUIRED"}
 if not baseline or baseline.get("state")!="PROTECTED_EXISTING_WORK":
  return {**out,"reason":"PROTECTED_BASELINE_REQUIRED"}
 if cfg.get("expected_origin") and baseline.get("origin")!=cfg.get("expected_origin"):
  return {**out,"reason":"ORIGIN_DRIFT"}
 branch=cfg.get("managed_branch","main")
 if baseline.get("branch")!=branch:return {**out,"reason":"BRANCH_DRIFT"}
 if baseline.get("upstream") not in (None,f"origin/{branch}"):return {**out,"reason":"UPSTREAM_DRIFT"}
 if baseline.get("ahead") not in (None,0) or baseline.get("behind") not in (None,0):
  return {**out,"reason":"UPSTREAM_DIVERGENCE"}
 if not inventory or inventory.get("state")!="PROTECTED_EXISTING_WORK" or inventory.get("head")!=baseline.get("head"):
  return {**out,"reason":"PROTECTED_INVENTORY_INVALID"}
 if not inventory.get("paths"):return {**out,"reason":"EMPTY_PROTECTED_INVENTORY"}
 if any(x.get("sensitive") for x in inventory.get("paths",[])):
  return {**out,"reason":"SENSITIVE_PROTECTED_PATH_PRESENT"}
 groups=inventory.get("candidate_packages") or []
 if not groups or any(x.get("state")!="QUIET" for x in groups):
  return {**out,"reason":"PROTECTED_WORK_NOT_QUIET"}
 if not activity or activity.get("state")!="QUIET" or int(activity.get("active_reference_count",0))!=0:
  return {**out,"reason":"ACTIVE_SOURCE_REFERENCE_PRESENT"}
 if not plan or plan.get("schema_version")!=1 or plan.get("project")!=name:
  return {**out,"reason":"ADOPTION_PLAN_REQUIRED"}
 source=baseline.get("head")
 if plan.get("source_sha")!=source:return {**out,"reason":"ADOPTION_PLAN_SOURCE_DRIFT"}
 inv_id=inventory_identity(inventory)
 if plan.get("inventory_identity")!=inv_id:return {**out,"reason":"ADOPTION_PLAN_INVENTORY_DRIFT"}
 if not deferred or deferred.get("state")!="VERIFIED_DEFERRED_CANDIDATE" or deferred.get("source_sha")!=source:
  return {**out,"reason":"VERIFIED_DEFERRED_CANDIDATE_REQUIRED"}
 if deferred.get("convergence_authorized") is not False:return {**out,"reason":"DEFERRED_CANDIDATE_AUTHORITY_INVALID"}
 if plan.get("deferred_item_id")!=deferred.get("item_id") or plan.get("deferred_diff_sha256")!=deferred.get("diff_sha256"):
  return {**out,"reason":"DEFERRED_CANDIDATE_PLAN_MISMATCH"}
 if not repair or repair.get("state")!="VERIFIED_PROTECTED_REPAIR_CANDIDATE" or repair.get("source_sha")!=source:
  return {**out,"reason":"VERIFIED_PROTECTED_REPAIR_REQUIRED"}
 if repair.get("convergence_authorized") is not False:return {**out,"reason":"REPAIR_CANDIDATE_AUTHORITY_INVALID"}
 cv=repair.get("composed_verification") or {}
 if cv.get("state")!="PASS" or not cv.get("source_unchanged") or cv.get("exit_code")!=0:
  return {**out,"reason":"COMPOSED_VERIFICATION_REQUIRED"}
 expected_argv=["npm","run",cfg.get("a2_verification_entrypoint")] if cfg.get("a2_verification_entrypoint") else None
 if expected_argv and list(repair.get("verification_argv") or [])!=expected_argv:
  return {**out,"reason":"VERIFICATION_ENTRYPOINT_MISMATCH"}
 if plan.get("repair_item_id")!=repair.get("item_id") or plan.get("repair_changes_sha256")!=repair.get("changes_sha256"):
  return {**out,"reason":"REPAIR_CANDIDATE_PLAN_MISMATCH"}
 protected={x.get("path") for x in inventory.get("paths",[]) if x.get("path")}
 deferred_paths=set(deferred.get("changed_paths") or [])
 repair_paths=set(repair.get("combined_repair_paths") or repair.get("allowed_paths") or [])
 if deferred_paths & protected:return {**out,"reason":"DEFERRED_PROTECTED_PATH_OVERLAP"}
 if not repair_paths.issubset(protected):return {**out,"reason":"REPAIR_OUTSIDE_PROTECTED_SURFACE"}
 adopted=sorted(protected|deferred_paths)
 return {**out,"state":"ADOPTABLE","reason":"ALL_ADOPTION_GATES_PASS","eligible":True,"source_sha":source,"inventory_identity":inv_id,
         "adopted_paths":adopted,"adopted_path_count":len(adopted),"protected_path_count":len(protected),
         "deferred_paths":sorted(deferred_paths),"repair_paths":sorted(repair_paths)}
