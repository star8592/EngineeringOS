import sys,tempfile,pathlib,subprocess
sys.path.insert(0,'src/engineeringos')
from coding_agent_provider import *
from coding_agent_executor import propose_and_verify
class Agent:
 name="fake"
 def propose(self,*,task,files): return AgentCandidate("fake","fixture",{"x.txt":files["x.txt"].replace("old","new")},"replace requested text",.9)
def run(*a,cwd=None):return subprocess.check_output(a,cwd=cwd,text=True).strip()
with tempfile.TemporaryDirectory() as td:
 r=pathlib.Path(td)/"r";r.mkdir();run("git","init","-q",cwd=r);run("git","config","user.email","t@example.com",cwd=r);run("git","config","user.name","T",cwd=r);(r/"x.txt").write_text("old");run("git","add","x.txt",cwd=r);run("git","commit","-qm","b",cwd=r);sha=run("git","rev-parse","HEAD",cwd=r)
 task=TaskEnvelope("P","i",sha,"change old to new",("x.txt",),(sys.executable,"-c","assert open('x.txt').read()=='new'"),{})
 out=propose_and_verify(str(r),task,Agent(),workspace_root=str(pathlib.Path(td)/"ws"))
 assert out["authority"]=="CANDIDATE_ONLY_NO_EXECUTION_AUTHORITY"
 assert out["verification_result"]["state"]=="READY_FOR_CONVERGENCE"
 assert (r/"x.txt").read_text()=="old"
 try: validate_candidate(task,AgentCandidate("fake","fixture",{"y.txt":"x"}));raise AssertionError()
 except CodingAgentError as e: assert str(e)=="AGENT_MUTATION_SURFACE_DRIFT"
print("5 coding-agent executor invariants passed")
