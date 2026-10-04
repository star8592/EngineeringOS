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
 return body
