import sys,tempfile,pathlib,subprocess
sys.path.insert(0,'src/engineeringos')
from mutation_proposal import *
def run(*a,cwd=None): return subprocess.check_output(a,cwd=cwd,text=True).strip()
with tempfile.TemporaryDirectory() as td:
 repo=pathlib.Path(td)/"repo";repo.mkdir();run("git","init","-q",cwd=repo);run("git","config","user.email","t@example.com",cwd=repo);run("git","config","user.name","T",cwd=repo)
 (repo/"value.txt").write_text("old\n");run("git","add","value.txt",cwd=repo);run("git","commit","-qm","base",cwd=repo);sha=run("git","rev-parse","HEAD",cwd=repo)
 p={"schema_version":1,"project":"P","item_id":"change-value","source_sha":sha,"allowed_paths":["value.txt"],"changes":{"value.txt":"new\n"},"verification_argv":[sys.executable,"-c","assert open('value.txt').read()=='new\\n'"]}
 out=execute_proposal(str(repo),p,workspace_root=str(pathlib.Path(td)/"ws"),keep_workspace=False)
 assert out["state"]=="READY_FOR_CONVERGENCE" and not out["main_mutated"]
 assert (repo/"value.txt").read_text()=="old\n" and run("git","status","--porcelain",cwd=repo)==""
 bad={**p,"verification_argv":[sys.executable,"-c","raise SystemExit(1)"]}
 out2=execute_proposal(str(repo),bad,workspace_root=str(pathlib.Path(td)/"ws2"),keep_workspace=False);assert out2["state"]=="VERIFICATION_FAILED"
 try: validate_proposal({**p,"allowed_paths":["other.txt"]});raise AssertionError()
 except ProposalError as e: assert str(e)=="CHANGE_SURFACE_MUST_EQUAL_ALLOWED_PATHS"
 assert proposal_hash(p)==proposal_hash(dict(reversed(list(p.items()))))
print("7 mutation-proposal invariants passed")
