import sys,tempfile,pathlib,json
sys.path.insert(0,'src/engineeringos')
from project_registry import *
with tempfile.TemporaryDirectory() as td:
 p=pathlib.Path(td)/"r.json";assert load(p)["projects"]==[]
 p.write_text(json.dumps({"schema_version":1,"projects":[{"name":"EngineeringOS","repo":"/r","autopilot_enabled":True,"workspace_root":"/w","max_assurance":"A2"}]}));assert load(p)["projects"][0]["autopilot_enabled"]
 p.write_text(json.dumps({"schema_version":1,"projects":[{"name":"P","repo":"/r","autopilot_enabled":True,"max_assurance":"A2"}]}))
 try:load(p);raise AssertionError()
 except RegistryError as e:assert str(e)=="WORKSPACE_ROOT_REQUIRED"
 p.write_text(json.dumps({"schema_version":1,"projects":[{"name":"P","repo":"/r","autopilot_enabled":True,"workspace_root":"/w","max_assurance":"A3"}]}))
 try:load(p);raise AssertionError()
 except RegistryError as e:assert str(e)=="SAFE_AUTOPILOT_ASSURANCE_REQUIRED"
 p.write_text(json.dumps({"schema_version":1,"projects":[{"name":"P","repo":"/r","autopilot_enabled":True,"workspace_root":"/w","max_assurance":"A2","provider_timeout":30}]}))
 try:load(p);raise AssertionError()
 except RegistryError as e:assert str(e)=="LEGACY_SHARED_PROVIDER_TIMEOUT_FORBIDDEN"
 p.write_text(json.dumps({"schema_version":1,"projects":[{"name":"P","repo":"/r","autopilot_enabled":True,"workspace_root":"/w","max_assurance":"A2","provider_timeouts":{"codex-cli-readonly":240}}]}))
 assert load(p)["projects"][0]["provider_timeouts"]["codex-cli-readonly"]==240
 p.write_text(json.dumps({"schema_version":1,"projects":[{"name":"P","display_name":"袋鼠数学","repo":"/r","autopilot_enabled":False}]}));assert load(p)["projects"][0]["display_name"]=="袋鼠数学"
 p.write_text(json.dumps({"schema_version":1,"projects":[{"name":"P","display_name":"","repo":"/r","autopilot_enabled":False}]}))
 try:load(p);raise AssertionError()
 except RegistryError as e:assert str(e)=="INVALID_DISPLAY_NAME"
 p.write_text(json.dumps({"schema_version":1,"projects":[{"name":"P","repo":"/r","autopilot_enabled":False,"require_clean_baseline":"yes"}]}))
 try:load(p);raise AssertionError()
 except RegistryError as e:assert str(e)=="INVALID_BASELINE_POLICY"
 p.write_text(json.dumps({"schema_version":1,"projects":[{"name":"P","repo":"/r","autopilot_enabled":True,"workspace_root":"/w","max_assurance":"A2","provider_timeouts":{"unknown":1}}]}))
 try:load(p);raise AssertionError()
 except RegistryError as e:assert str(e)=="UNKNOWN_PROVIDER_TIMEOUT"
print("13 project-registry invariants passed")
