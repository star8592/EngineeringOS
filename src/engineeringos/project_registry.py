from __future__ import annotations
import json,pathlib
class RegistryError(ValueError):pass
def load(path):
 p=pathlib.Path(path)
 if not p.exists():return {"schema_version":1,"projects":[]}
 body=json.loads(p.read_text())
 if body.get("schema_version")!=1:raise RegistryError("UNSUPPORTED_REGISTRY_SCHEMA")
 seen=set()
 for x in body.get("projects",[]):
  if not x.get("name") or not x.get("repo"):raise RegistryError("PROJECT_IDENTITY_REQUIRED")
  if x["name"] in seen:raise RegistryError("DUPLICATE_PROJECT")
  seen.add(x["name"])
  if x.get("autopilot_enabled") and not x.get("workspace_root"):raise RegistryError("WORKSPACE_ROOT_REQUIRED")
  if x.get("autopilot_enabled") and x.get("max_assurance") not in ("A1","A2"):raise RegistryError("SAFE_AUTOPILOT_ASSURANCE_REQUIRED")
  if "provider_timeout" in x:raise RegistryError("LEGACY_SHARED_PROVIDER_TIMEOUT_FORBIDDEN")
  pts=x.get("provider_timeouts",{})
  if not isinstance(pts,dict):raise RegistryError("PROVIDER_TIMEOUTS_MUST_BE_OBJECT")
  allowed={"codex-cli-readonly","claude-cli-readonly"}
  if set(pts)-allowed:raise RegistryError("UNKNOWN_PROVIDER_TIMEOUT")
  if any(not isinstance(v,int) or isinstance(v,bool) or v<1 for v in pts.values()):raise RegistryError("INVALID_PROVIDER_TIMEOUT")
 return body
