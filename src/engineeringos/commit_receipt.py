from __future__ import annotations
import subprocess,hashlib,json,datetime as dt

class CommitReceiptError(RuntimeError): pass

def commit_converged(repo:str,*,item_id:str,source_sha:str,changed_paths:list[str],message:str)->dict:
 head=subprocess.check_output(["git","-C",repo,"rev-parse","HEAD"],text=True).strip()
 if head!=source_sha: raise CommitReceiptError("SOURCE_SHA_DRIFT")
 staged=subprocess.check_output(["git","-C",repo,"diff","--cached","--name-only"],text=True).splitlines()
 if sorted(staged)!=sorted(changed_paths): raise CommitReceiptError("STAGED_SURFACE_DRIFT")
 diff=subprocess.check_output(["git","-C",repo,"diff","--cached","--binary"])
 diff_sha=hashlib.sha256(diff).hexdigest()
 proc=subprocess.run(["git","-C",repo,"commit","-m",message],text=True,capture_output=True)
 if proc.returncode: raise CommitReceiptError("COMMIT_FAILED:"+proc.stderr[-1000:])
 result_sha=subprocess.check_output(["git","-C",repo,"rev-parse","HEAD"],text=True).strip()
 return {"schema_version":1,"item_id":item_id,"state":"COMMITTED","source_sha":source_sha,"result_sha":result_sha,
         "changed_paths":sorted(changed_paths),"diff_sha256":diff_sha,"committed_at":dt.datetime.now(dt.timezone.utc).isoformat(),
         "evidence_refs":[f"source-sha:{source_sha}",f"result-sha:{result_sha}",f"diff-sha256:{diff_sha}"]}
