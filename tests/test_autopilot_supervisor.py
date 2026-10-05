import sys,tempfile,pathlib,subprocess
sys.path.insert(0,'src/engineeringos')
from autopilot_supervisor import *
from coding_agent_provider import AgentCandidate,CodingAgentError
from scheduler import schedule
class Good:
 name="good"
 def propose(self,*,task,files): return AgentCandidate("good","fixture",{"x.txt":"new"},"bounded",1)
class Bad:
 name="bad"
 def propose(self,**k): raise CodingAgentError("offline")
def run(*a,cwd=None):return subprocess.check_output(a,cwd=cwd,text=True).strip()
with tempfile.TemporaryDirectory() as td:
 repo=pathlib.Path(td)/"r";repo.mkdir();run("git","init","-q",cwd=repo);run("git","config","user.email","t@example.com",cwd=repo);run("git","config","user.name","T",cwd=repo);(repo/"x.txt").write_text("old");run("git","add","x.txt",cwd=repo);run("git","commit","-qm","b",cwd=repo);sha=run("git","rev-parse","HEAD",cwd=repo)
 base={"id":"w","project":"P","expected_outcome":"make x new","state":"DISCOVERED","automation":"REVIEW","required_assurance":"A2"}
 waiting=supervisor_tick(str(repo),[base],schedule([base]),[Good()],workspace_root=str(pathlib.Path(td)/"ws"));assert waiting["results"][0]["state"]=="WAITING_CONTRACT" and not waiting["needs_intent"]
 item={**base,"source_sha":sha,"allowed_paths":["x.txt"],"verification_argv":[sys.executable,"-c","assert open('x.txt').read()=='new'"]}
 fail=supervisor_tick(str(repo),[item],schedule([item]),[Bad()],workspace_root=str(pathlib.Path(td)/"ws2"));assert fail["results"][0]["state"]=="REOPENED" and fail["results"][0]["reason"]=="WAITING_PROVIDER" and not fail["needs_intent"]
 invalid={**item,"verification_argv":[sys.executable,"-c","import sys;print('Ran 0 tests');print('NO TESTS RAN',file=sys.stderr);sys.exit(5)"]}
 badverify=supervisor_tick(str(repo),[invalid],schedule([invalid]),[Good()],workspace_root=str(pathlib.Path(td)/"ws-invalid"));assert badverify["results"][0]["reason"]=="CONTRACT_VERIFICATION_INVALID";assert (repo/"x.txt").read_text()=="old"
 ok=supervisor_tick(str(repo),[item],schedule([item]),[Bad(),Good()],workspace_root=str(pathlib.Path(td)/"ws3"));assert ok["results"][0]["state"]=="COMMITTED";assert (repo/"x.txt").read_text()=="new";assert run("git","diff","--cached","--name-only",cwd=repo)=="";assert ok["results"][0]["commit_receipt"]["source_sha"]==sha;assert ok["results"][0]["commit_receipt"]["result_sha"]==run("git","rev-parse","HEAD",cwd=repo);assert not ok["needs_intent"]
print("14 autopilot-supervisor invariants passed")
