import sys,tempfile,pathlib,subprocess
sys.path.insert(0,'src/engineeringos')
from conversation_ingest import ingest
from durable_supervisor_runtime import recover,admit_work_contract,resume_once
from contract_planner import PlanningPool,ContractCandidate
from coding_agent_provider import AgentCandidate
class Planner:
 name="fixture-planner"
 def plan(self,**k):return ContractCandidate(self.name,"fixture",("status.txt",),("python3","-c","assert 'recent' in open('status.txt').read()"))
class Coder:
 name="fixture-coder"
 def propose(self,*,task,files):return AgentCandidate(self.name,"fixture",{"status.txt":"status\nrecent\n"},"add recent",1)
def run(*a,cwd=None):return subprocess.check_output(a,cwd=cwd,text=True).strip()
with tempfile.TemporaryDirectory() as td:
 root=pathlib.Path(td);repo=root/"repo";repo.mkdir();run("git","init","-q",cwd=repo);run("git","config","user.email","t@example.com",cwd=repo);run("git","config","user.name","T",cwd=repo);(repo/"status.txt").write_text("status\n");run("git","add","status.txt",cwd=repo);run("git","commit","-qm","base",cwd=repo)
 rr=root/"runtime";s=ingest(rr,project="P",command_id="u1",conversation_id="chat",kind="DESIRE",text="给状态页加最近完成",intent_id="status",required_capabilities=["recent completion"])
 w=next(x for x in s["work_items"].values() if x["kind"]=="CAPABILITY_PLANNING")
 contract,e=PlanningPool([Planner()]).plan(repo=str(repo),work=w,project_context={});admit_work_contract(rr,"P",w["id"],contract,planner_evidence="fixture-planner")
 # bind source SHA only after durable planning, before mutation execution
 from project_journal import append
 from durable_supervisor_runtime import journal_path
 append(journal_path(rr,"P"),project="P",typ="WORK_CONTRACT_ADMITTED",key=w["id"],generation=1,payload={"source_sha":run("git","rev-parse","HEAD",cwd=repo)})
 out=resume_once(str(repo),rr,"P",[Coder()],workspace_root=str(root/"ws"));final=recover(rr,"P");fw=final["work_items"][w["id"]]
 assert "recent" in (repo/"status.txt").read_text() and fw["state"]=="RESOLVED" and fw["commit_receipt"]["result_sha"]==run("git","rev-parse","HEAD",cwd=repo)
 s2=ingest(rr,project="P",command_id="u2",conversation_id="chat",kind="CORRECTION",text="最近完成只显示一项",intent_id="status")
 new=[x for x in s2["work_items"].values() if x.get("intent_generation")==2 and x["kind"]=="CAPABILITY_PLANNING"];assert len(new)==1
 assert s2["intents"]["status"]["generation"]==2
 print("10 conversation-to-commit acceptance invariants passed")
