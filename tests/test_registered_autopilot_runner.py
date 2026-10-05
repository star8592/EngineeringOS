import sys,tempfile,pathlib,json
sys.path.insert(0,'src/engineeringos')
from registered_autopilot_runner import *
from durable_supervisor_runtime import record_intent,discover_work
from coding_agent_provider import CodingAgentError
class Bad:
 name="bad"
 def propose(self,**k):raise CodingAgentError("offline")
with tempfile.TemporaryDirectory() as td:
 root=pathlib.Path(td);reg=root/"reg.json";repo=root/"repo";repo.mkdir();import subprocess
 def run(*a,cwd=None):return subprocess.check_output(a,cwd=cwd,text=True).strip()
 run("git","init","-q",cwd=repo);run("git","config","user.email","t@example.com",cwd=repo);run("git","config","user.name","T",cwd=repo);(repo/"x").write_text("a");run("git","add","x",cwd=repo);run("git","commit","-qm","b",cwd=repo);sha=run("git","rev-parse","HEAD",cwd=repo)
 rr=root/"runtime";record_intent(rr,"P",intent_id="i",generation=1,statement="x",required_capabilities=["x"]);discover_work(rr,"P",{"id":"w","project":"P","state":"DISCOVERED","kind":"CAPABILITY_GAP","automation":"REVIEW","required_assurance":"A2","source_sha":sha,"allowed_paths":["x"],"verification_argv":[sys.executable,"-c","assert True"]})
 reg.write_text(json.dumps({"schema_version":1,"projects":[{"name":"P","repo":str(repo),"autopilot_enabled":True,"workspace_root":str(root/"ws"),"max_assurance":"A2"}]}))
 a=run_registered_once(reg,rr,provider_factory=lambda c:[Bad()],now=100);assert a[0]["action"]=="ADVANCE"
 b=run_registered_once(reg,rr,provider_factory=lambda c:[Bad()],now=101);assert b[0]["action"]=="BACKOFF_WAIT"
 c=run_registered_once(reg,rr,provider_factory=lambda c:[Bad()],now=131);assert c[0]["action"]=="ADVANCE"
 # A protected external baseline blocks planning/coding even if config is accidentally enabled.
 bp=rr/"projects"/"P"/"baseline.json";bp.write_text(json.dumps({"schema_version":1,"project":"P","state":"PROTECTED_EXISTING_WORK"}))
 reg.write_text(json.dumps({"schema_version":1,"projects":[{"name":"P","repo":str(repo),"autopilot_enabled":True,"require_clean_baseline":True,"management_target":"A2_MANAGED","expected_origin":"https://example/P.git","managed_branch":"main","a2_verification_entrypoint":"verify:public","workspace_root":str(root/"ws"),"max_assurance":"A2"}]}))
 d=run_registered_once(reg,rr,provider_factory=lambda c:[Bad()],now=1000);assert d[0]["action"]=="PROMOTION_BLOCKED" and d[0]["reason"]=="PROTECTED_EXISTING_WORK" and d[0]["should_notify"] is False
print("8 registered-autopilot-runner invariants passed")
