import sys,tempfile,pathlib,subprocess,json
sys.path.insert(0,'src/engineeringos')
from durable_supervisor_runtime import *
from coding_agent_provider import AgentCandidate
from commit_receipt import commit_converged,commit_recovery_token
class Good:
 name="good"
 def propose(self,*,task,files):return AgentCandidate("good","fixture",{"x.txt":"new"},"ok",1)
def run(*a,cwd=None):return subprocess.check_output(a,cwd=cwd,text=True).strip()
with tempfile.TemporaryDirectory() as td:
 root=pathlib.Path(td);repo=root/"repo";repo.mkdir();run("git","init","-q",cwd=repo);run("git","config","user.email","t@example.com",cwd=repo);run("git","config","user.name","T",cwd=repo);(repo/"x.txt").write_text("old");run("git","add","x.txt",cwd=repo);run("git","commit","-qm","base",cwd=repo);sha=run("git","rev-parse","HEAD",cwd=repo)
 rr=root/"runtime";record_intent(rr,"P",intent_id="i",generation=1,statement="make x new",required_capabilities=["x"])
 item={"id":"gap-x","project":"P","kind":"CAPABILITY_GAP","intent_id":"i","intent_generation":1,"requirement":"x","expected_outcome":"make x new","state":"DISCOVERED","automation":"REVIEW","required_assurance":"A2","source_sha":sha,"allowed_paths":["x.txt"],"verification_argv":[sys.executable,"-c","assert open('x.txt').read()=='new'"],"completion_predicate":{"type":"CAPABILITY_EVIDENCE","requirement":"x","accepted_states":["VERIFIED"]}}
 discover_work(rr,"P",item)
 cold=recover(rr,"P");assert cold["intents"]["i"]["statement"]=="make x new" and cold["work_items"]["gap-x"]["state"]=="DISCOVERED"
 out=resume_once(str(repo),rr,"P",[Good()],workspace_root=str(root/"ws"));assert out["execution"]["results"][0]["state"]=="COMMITTED";result_sha=run("git","rev-parse","HEAD",cwd=repo)
 restarted=recover(rr,"P");w=restarted["work_items"]["gap-x"];assert w["state"]=="RESOLVED";assert w["commit_receipt"]["source_sha"]==sha and w["commit_receipt"]["result_sha"]==result_sha;assert w["resolution_evidence_refs"]
 out2=resume_once(str(repo),rr,"P",[Good()],workspace_root=str(root/"ws2"));assert out2["execution"]["results"]==[]
 # Higher-assurance work may be committed locally but cannot be auto-resolved by A2 evidence.
 (repo/"y.txt").write_text("old");run("git","add","y.txt",cwd=repo);run("git","commit","-qm","add y",cwd=repo);sha2=run("git","rev-parse","HEAD",cwd=repo)
 high={**item,"id":"gap-y","requirement":"y","required_assurance":"A3","source_sha":sha2,"allowed_paths":["y.txt"],"verification_argv":[sys.executable,"-c","assert open('y.txt').read()=='new'"]}
 discover_work(rr,"P",high)
 class GoodY:
  name="good-y"
  def propose(self,*,task,files):return AgentCandidate("good-y","fixture",{"y.txt":"new"},"ok",1)
 highout=resume_once(str(repo),rr,"P",[GoodY()],workspace_root=str(root/"ws3"));assert highout["after"]["work_items"]["gap-y"]["state"]=="COMMITTED"

# Simulate the critical crash window: Git commit succeeds but WORK_COMMITTED never reaches the journal.
with tempfile.TemporaryDirectory() as td:
 root=pathlib.Path(td);repo=root/"repo";repo.mkdir();run("git","init","-q",cwd=repo);run("git","config","user.email","t@example.com",cwd=repo);run("git","config","user.name","T",cwd=repo)
 (repo/"x.txt").write_text("old");run("git","add","x.txt",cwd=repo);run("git","commit","-qm","base",cwd=repo);sha=run("git","rev-parse","HEAD",cwd=repo)
 rr=root/"runtime";record_intent(rr,"Crash",intent_id="i",generation=1,statement="make x new",required_capabilities=["x"])
 item={"id":"gap-crash","project":"Crash","kind":"CAPABILITY_GAP","intent_id":"i","intent_generation":1,"requirement":"x","expected_outcome":"make x new","state":"DISCOVERED","automation":"REVIEW","required_assurance":"A2","source_sha":sha,"allowed_paths":["x.txt"],"verification_argv":[sys.executable,"-c","assert open('x.txt').read()=='new'"],"completion_predicate":{"type":"CAPABILITY_EVIDENCE","requirement":"x","accepted_states":["VERIFIED"]}}
 discover_work(rr,"Crash",item)
 (repo/"x.txt").write_text("new");run("git","add","x.txt",cwd=repo)
 token=commit_recovery_token(project=item["project"],item_id=item["id"],generation=item["intent_generation"],source_sha=sha,allowed_paths=item["allowed_paths"],verification_argv=item["verification_argv"])
 committed=commit_converged(str(repo),item_id=item["id"],source_sha=sha,changed_paths=["x.txt"],message="autopilot: gap-crash",recovery_token=token)
 class MustNotRun:
  name="must-not-run"
  def propose(self,**kwargs):raise AssertionError("provider invoked after recoverable commit")
 recovered=resume_once(str(repo),rr,"Crash",[MustNotRun()],workspace_root=str(root/"ws"))
 assert recovered["recovered_commits"]==[{"item_id":"gap-crash","result_sha":committed["result_sha"],"recovered":True}]
 assert recovered["execution"]["results"]==[]
 rw=recovered["after"]["work_items"]["gap-crash"];assert rw["state"]=="RESOLVED" and rw["commit_receipt"]["recovered"] is True
 again=resume_once(str(repo),rr,"Crash",[MustNotRun()],workspace_root=str(root/"ws2"));assert again["recovered_commits"]==[] and again["execution"]["results"]==[]
print("22 durable-supervisor restart invariants passed")
