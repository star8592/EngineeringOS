from __future__ import annotations
import subprocess,hashlib,json,datetime as dt

class CommitReceiptError(RuntimeError): pass

def commit_recovery_token(*,project:str,item_id:str,generation:int,source_sha:str,allowed_paths:list[str],verification_argv:list[str])->str:
 payload={"project":project,"item_id":item_id,"generation":int(generation),"source_sha":source_sha,"allowed_paths":sorted(allowed_paths),"verification_argv":list(verification_argv)}
 return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def _trailered_message(message:str,*,item_id:str,source_sha:str,diff_sha:str,recovery_token:str)->str:
 for value in (item_id,source_sha,diff_sha,recovery_token):
  if "\n" in value or "\r" in value:raise CommitReceiptError("INVALID_COMMIT_TRAILER_VALUE")
 return (message.rstrip()+"\n\n"
         f"EngineeringOS-Item: {item_id}\n"
         f"EngineeringOS-Source: {source_sha}\n"
         f"EngineeringOS-Diff-SHA256: {diff_sha}\n"
         f"EngineeringOS-Recovery-Token: {recovery_token}")

def _receipt(*,item_id,source_sha,result_sha,changed_paths,diff_sha,committed_at,recovery_token,recovered=False):
 return {"schema_version":1,"item_id":item_id,"state":"COMMITTED","source_sha":source_sha,"result_sha":result_sha,
         "changed_paths":sorted(changed_paths),"diff_sha256":diff_sha,"committed_at":committed_at,
         "recovery_token":recovery_token,"recovered":bool(recovered),
         "evidence_refs":[f"source-sha:{source_sha}",f"result-sha:{result_sha}",f"diff-sha256:{diff_sha}"]}

def commit_converged(repo:str,*,item_id:str,source_sha:str,changed_paths:list[str],message:str,recovery_token:str)->dict:
 head=subprocess.check_output(["git","-C",repo,"rev-parse","HEAD"],text=True).strip()
 if head!=source_sha: raise CommitReceiptError("SOURCE_SHA_DRIFT")
 staged=subprocess.check_output(["git","-C",repo,"diff","--cached","--name-only"],text=True).splitlines()
 if sorted(staged)!=sorted(changed_paths): raise CommitReceiptError("STAGED_SURFACE_DRIFT")
 diff=subprocess.check_output(["git","-C",repo,"diff","--cached","--binary"])
 diff_sha=hashlib.sha256(diff).hexdigest()
 final_message=_trailered_message(message,item_id=item_id,source_sha=source_sha,diff_sha=diff_sha,recovery_token=recovery_token)
 proc=subprocess.run(["git","-C",repo,"commit","-m",final_message],text=True,capture_output=True)
 if proc.returncode: raise CommitReceiptError("COMMIT_FAILED:"+proc.stderr[-1000:])
 result_sha=subprocess.check_output(["git","-C",repo,"rev-parse","HEAD"],text=True).strip()
 committed_at=subprocess.check_output(["git","-C",repo,"show","-s","--format=%cI",result_sha],text=True).strip()
 return _receipt(item_id=item_id,source_sha=source_sha,result_sha=result_sha,changed_paths=changed_paths,diff_sha=diff_sha,committed_at=committed_at,recovery_token=recovery_token)

def _parse_trailers(body:str)->dict[str,str]|None:
 keys=("EngineeringOS-Item","EngineeringOS-Source","EngineeringOS-Diff-SHA256","EngineeringOS-Recovery-Token")
 out={}
 for line in body.splitlines():
  for key in keys:
   prefix=key+": "
   if line.startswith(prefix):
    if key in out:return None
    out[key]=line[len(prefix):].strip()
 return out if set(out)==set(keys) else None

def recover_commit_receipt(repo:str,*,project:str,item_id:str,generation:int,source_sha:str,allowed_paths:list[str],verification_argv:list[str])->dict|None:
 token=commit_recovery_token(project=project,item_id=item_id,generation=generation,source_sha=source_sha,allowed_paths=allowed_paths,verification_argv=verification_argv)
 anc=subprocess.run(["git","-C",repo,"merge-base","--is-ancestor",source_sha,"HEAD"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 if anc.returncode:return None
 revs=subprocess.check_output(["git","-C",repo,"rev-list","--first-parent","--reverse",f"{source_sha}..HEAD"],text=True).splitlines()
 if not revs:return None
 candidate=revs[0]
 parent=subprocess.check_output(["git","-C",repo,"rev-parse",candidate+"^"],text=True).strip()
 if parent!=source_sha:return None
 body=subprocess.check_output(["git","-C",repo,"show","-s","--format=%B",candidate],text=True)
 trailers=_parse_trailers(body)
 if not trailers:return None
 if trailers["EngineeringOS-Item"]!=item_id or trailers["EngineeringOS-Source"]!=source_sha or trailers["EngineeringOS-Recovery-Token"]!=token:return None
 changed=subprocess.check_output(["git","-C",repo,"diff","--name-only",source_sha,candidate],text=True).splitlines()
 if not changed or not set(changed).issubset(set(allowed_paths)):return None
 diff=subprocess.check_output(["git","-C",repo,"diff","--binary",source_sha,candidate])
 diff_sha=hashlib.sha256(diff).hexdigest()
 if trailers["EngineeringOS-Diff-SHA256"]!=diff_sha:return None
 committed_at=subprocess.check_output(["git","-C",repo,"show","-s","--format=%cI",candidate],text=True).strip()
 return _receipt(item_id=item_id,source_sha=source_sha,result_sha=candidate,changed_paths=changed,diff_sha=diff_sha,committed_at=committed_at,recovery_token=token,recovered=True)
