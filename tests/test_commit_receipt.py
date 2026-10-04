import sys,tempfile,pathlib,subprocess
sys.path.insert(0,'src/engineeringos')
from commit_receipt import *
def run(*a,cwd=None):return subprocess.check_output(a,cwd=cwd,text=True).strip()
with tempfile.TemporaryDirectory() as td:
 r=pathlib.Path(td);run("git","init","-q",cwd=r);run("git","config","user.email","t@example.com",cwd=r);run("git","config","user.name","T",cwd=r);(r/"x").write_text("a");run("git","add","x",cwd=r);run("git","commit","-qm","b",cwd=r);sha=run("git","rev-parse","HEAD",cwd=r);(r/"x").write_text("b");run("git","add","x",cwd=r)
 rec=commit_converged(str(r),item_id="i",source_sha=sha,changed_paths=["x"],message="change x")
 assert rec["state"]=="COMMITTED" and rec["source_sha"]==sha and rec["result_sha"]==run("git","rev-parse","HEAD",cwd=r) and len(rec["evidence_refs"])==3
print("4 commit-receipt invariants passed")
