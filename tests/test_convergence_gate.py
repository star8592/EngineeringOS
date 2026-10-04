import sys,tempfile,pathlib,subprocess
sys.path.insert(0,'src/engineeringos')
from mutation_proposal import execute_proposal
from convergence_gate import *
def run(*a,cwd=None): return subprocess.check_output(a,cwd=cwd,text=True).strip()
with tempfile.TemporaryDirectory() as td:
 repo=pathlib.Path(td)/"r";repo.mkdir();run("git","init","-q",cwd=repo);run("git","config","user.email","t@example.com",cwd=repo);run("git","config","user.name","T",cwd=repo);(repo/"x").write_text("a");run("git","add","x",cwd=repo);run("git","commit","-qm","b",cwd=repo);sha=run("git","rev-parse","HEAD",cwd=repo)
 p={"schema_version":1,"project":"P","item_id":"i","source_sha":sha,"allowed_paths":["x"],"changes":{"x":"b"},"verification_argv":[sys.executable,"-c","assert open('x').read()=='b'"]}
 r=execute_proposal(str(repo),p,workspace_root=str(pathlib.Path(td)/"ws"),keep_workspace=True);assert assess(str(repo),p,r)["decision"]=="ALLOW"
 c=converge(str(repo),p,r);assert c["applied"] and (repo/"x").read_text()=="b";assert run("git","diff","--cached","--name-only",cwd=repo)=="x"
print("3 convergence-gate invariants passed")
