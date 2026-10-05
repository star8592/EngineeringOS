import sys,tempfile,pathlib,subprocess
sys.path.insert(0,'src/engineeringos')
from commit_receipt import *

def run(*a,cwd=None):return subprocess.check_output(a,cwd=cwd,text=True).strip()

with tempfile.TemporaryDirectory() as td:
 r=pathlib.Path(td);run("git","init","-q",cwd=r);run("git","config","user.email","t@example.com",cwd=r);run("git","config","user.name","T",cwd=r)
 (r/"x").write_text("a");run("git","add","x",cwd=r);run("git","commit","-qm","b",cwd=r);sha=run("git","rev-parse","HEAD",cwd=r)
 argv=[sys.executable,"-c","assert True"];token=commit_recovery_token(project="P",item_id="i",generation=1,source_sha=sha,allowed_paths=["x"],verification_argv=argv)
 (r/"x").write_text("b");run("git","add","x",cwd=r)
 rec=commit_converged(str(r),item_id="i",source_sha=sha,changed_paths=["x"],message="change x",recovery_token=token)
 assert rec["state"]=="COMMITTED" and rec["source_sha"]==sha and rec["result_sha"]==run("git","rev-parse","HEAD",cwd=r) and len(rec["evidence_refs"])==3
 assert rec["recovery_token"]==token and rec["recovered"] is False
 body=run("git","show","-s","--format=%B","HEAD",cwd=r)
 for marker in ("EngineeringOS-Item: i","EngineeringOS-Source: "+sha,"EngineeringOS-Recovery-Token: "+token):assert marker in body
 recovered=recover_commit_receipt(str(r),project="P",item_id="i",generation=1,source_sha=sha,allowed_paths=["x"],verification_argv=argv)
 assert recovered and recovered["recovered"] is True and recovered["result_sha"]==rec["result_sha"] and recovered["diff_sha256"]==rec["diff_sha256"]
 assert recover_commit_receipt(str(r),project="P",item_id="i",generation=1,source_sha=sha,allowed_paths=["x"],verification_argv=["wrong"]) is None
 # Recovery still finds the exact first descendant if an unrelated later commit exists.
 (r/"z").write_text("later");run("git","add","z",cwd=r);run("git","commit","-qm","later",cwd=r)
 later=recover_commit_receipt(str(r),project="P",item_id="i",generation=1,source_sha=sha,allowed_paths=["x"],verification_argv=argv)
 assert later and later["result_sha"]==rec["result_sha"]
print("11 commit-receipt invariants passed")
