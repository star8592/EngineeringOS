import sys,tempfile,pathlib,subprocess,json
sys.path.insert(0,'src/engineeringos')
from registered_autopilot_runner import *
from conversation_ingest import ingest
from contract_planner import ContractCandidate
from coding_agent_provider import AgentCandidate
from durable_supervisor_runtime import recover
class Planner:
 name="planner"
 def plan(self,**k):return ContractCandidate("planner","fixture",("x.txt",),("python3","-c","assert open('x.txt').read()=='new'"))
class Coder:
 name="coder"
 def propose(self,**k):return AgentCandidate("coder","fixture",{"x.txt":"new"},"ok",1)
def run(*a,cwd=None):return subprocess.check_output(a,cwd=cwd,text=True).strip()
with tempfile.TemporaryDirectory() as td:
 root=pathlib.Path(td);repo=root/"repo";repo.mkdir();run("git","init","-q",cwd=repo);run("git","config","user.email","t@example.com",cwd=repo);run("git","config","user.name","T",cwd=repo);(repo/"x.txt").write_text("old");run("git","add","x.txt",cwd=repo);run("git","commit","-qm","base",cwd=repo)
 rr=root/"rt";ingest(rr,project="P",command_id="u1",conversation_id="c",kind="DESIRE",text="make x new",intent_id="x",required_capabilities=["x"])
 reg=root/"reg.json";reg.write_text(json.dumps({"schema_version":1,"projects":[{"name":"P","repo":str(repo),"autopilot_enabled":True,"workspace_root":str(root/"ws"),"max_assurance":"A2"}]}))
 a=run_registered_once(reg,rr,planner_factory=lambda c:[Planner()],provider_factory=lambda c:[Coder()],now=100);assert a[0]["action"]=="PLAN"
 st=recover(rr,"P");w=next(iter(st["work_items"].values()));assert w["allowed_paths"]==["x.txt"] and (repo/"x.txt").read_text()=="old"
 assert w["source_sha"]==run("git","rev-parse","HEAD",cwd=repo)
 b=run_registered_once(reg,rr,planner_factory=lambda c:[Planner()],provider_factory=lambda c:[Coder()],now=101);assert b[0]["action"]=="ADVANCE" and b[0]["result"]["results"][0]["state"]=="COMMITTED"
 assert (repo/"x.txt").read_text()=="new";final=recover(rr,"P");assert next(iter(final["work_items"].values()))["state"]=="RESOLVED"
 c=run_registered_once(reg,rr,planner_factory=lambda c:[Planner()],provider_factory=lambda c:[Coder()],now=102);assert c[0]["action"] in ("OBSERVE","SLEEP")
 # A plan admitted against an old HEAD is invalidated and returns to planning rather than retrying stale execution forever.
 ingest(rr,project="P",command_id="u2",conversation_id="c",kind="CORRECTION",text="make x newer",intent_id="x")
 p1=run_registered_once(reg,rr,planner_factory=lambda c:[Planner()],provider_factory=lambda c:[Coder()],now=200);assert p1[0]["action"]=="PLAN"
 (repo/"other").write_text("z");run("git","add","other",cwd=repo);run("git","commit","-qm","external advance",cwd=repo)
 p2=run_registered_once(reg,rr,planner_factory=lambda c:[Planner()],provider_factory=lambda c:[Coder()],now=201);assert p2[0]["result"]["results"][0]["reason"]=="SOURCE_SHA_DRIFT"
 stale=[x for x in recover(rr,"P")["work_items"].values() if x.get("intent_generation")==2][0];assert "allowed_paths" not in stale and stale["replan_required"]
 p3=run_registered_once(reg,rr,planner_factory=lambda c:[Planner()],provider_factory=lambda c:[Coder()],now=231);assert p3[0]["action"]=="PLAN"
 print("12 registered planning-execution invariants passed")
