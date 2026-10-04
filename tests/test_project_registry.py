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
print("6 project-registry invariants passed")
