from __future__ import annotations
import json,pathlib
class RegistryError(ValueError):pass

def management_requested(cfg):
 return bool(cfg.get("autopilot_enabled")) or cfg.get("management_target")=="A2_MANAGED"

def effective_autopilot(cfg,promotion=None):
 if cfg.get("management_target")=="A2_MANAGED":
  return bool(promotion and promotion.get("eligible"))
 return bool(cfg.get("autopilot_enabled"))
def load(path):
 p=pathlib.Path(path)
 if not p.exists():return {"schema_version":1,"projects":[]}
 body=json.loads(p.read_text())
 if body.get("schema_version")!=1:raise RegistryError("UNSUPPORTED_REGISTRY_SCHEMA")
 seen=set();routing_terms={}
 for x in body.get("projects",[]):
  if not x.get("name") or not x.get("repo"):raise RegistryError("PROJECT_IDENTITY_REQUIRED")
  if "display_name" in x and (not isinstance(x["display_name"],str) or not x["display_name"].strip()):raise RegistryError("INVALID_DISPLAY_NAME")
  if "require_clean_baseline" in x and not isinstance(x["require_clean_baseline"],bool):raise RegistryError("INVALID_BASELINE_POLICY")
  if "management_target" in x and x["management_target"] not in ("CONNECTED_READ_ONLY","A2_MANAGED"):raise RegistryError("INVALID_MANAGEMENT_TARGET")
  if "protected_work_policy" in x and x["protected_work_policy"] not in ("PROTECT_ONLY","ADOPT_VERIFIED_QUIET"):raise RegistryError("INVALID_PROTECTED_WORK_POLICY")
  for field in ("expected_origin","managed_branch","a2_verification_entrypoint"):
   if field in x and (not isinstance(x[field],str) or not x[field].strip()):raise RegistryError("INVALID_MANAGEMENT_POLICY")
  aliases=x.get("aliases",[])
  if not isinstance(aliases,list) or any(not isinstance(a,str) or not a.strip() for a in aliases):raise RegistryError("INVALID_PROJECT_ALIASES")
  for term in [x["name"],x.get("display_name"),*aliases]:
   if not isinstance(term,str) or not term.strip():continue
   norm="".join(term.split()).casefold()
   owner=routing_terms.get(norm)
   if owner and owner!=x["name"]:raise RegistryError("PROJECT_ALIAS_COLLISION")
   routing_terms[norm]=x["name"]
  if x["name"] in seen:raise RegistryError("DUPLICATE_PROJECT")
  seen.add(x["name"])
  if management_requested(x) and not x.get("workspace_root"):raise RegistryError("WORKSPACE_ROOT_REQUIRED")
  if management_requested(x) and x.get("max_assurance") not in ("A1","A2"):raise RegistryError("SAFE_AUTOPILOT_ASSURANCE_REQUIRED")
  if "provider_timeout" in x:raise RegistryError("LEGACY_SHARED_PROVIDER_TIMEOUT_FORBIDDEN")
  pts=x.get("provider_timeouts",{})
  if not isinstance(pts,dict):raise RegistryError("PROVIDER_TIMEOUTS_MUST_BE_OBJECT")
  allowed={"codex-cli-readonly","claude-cli-readonly"}
  if set(pts)-allowed:raise RegistryError("UNKNOWN_PROVIDER_TIMEOUT")
  if any(not isinstance(v,int) or isinstance(v,bool) or v<1 for v in pts.values()):raise RegistryError("INVALID_PROVIDER_TIMEOUT")
 return body
