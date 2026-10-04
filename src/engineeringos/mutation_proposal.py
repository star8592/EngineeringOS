from __future__ import annotations
import hashlib,json,pathlib,subprocess,datetime as dt
from isolated_mutation_lane import create_workspace,apply_file_changes,cleanup_workspace,MutationLaneError

class ProposalError(ValueError): pass

def validate_proposal(p:dict)->None:
 required=("schema_version","project","item_id","source_sha","allowed_paths","changes","verification_argv")
 for k in required:
  if k not in p: raise ProposalError("MISSING:"+k)
 if p["schema_version"]!=1: raise ProposalError("UNSUPPORTED_SCHEMA")
 if sorted(p["changes"])!=sorted(p["allowed_paths"]): raise ProposalError("CHANGE_SURFACE_MUST_EQUAL_ALLOWED_PATHS")
 if not p["verification_argv"] or not all(isinstance(x,str) and x for x in p["verification_argv"]): raise ProposalError("INVALID_VERIFICATION_ARGV")

def proposal_hash(p:dict)->str:
 return hashlib.sha256(json.dumps(p,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def execute_proposal(repo:str,p:dict,*,workspace_root:str,timeout:int=120,keep_workspace:bool=True)->dict:
 validate_proposal(p);ph=proposal_hash(p)
 w=create_workspace(repo,project=p["project"],item_id=p["item_id"],source_sha=p["source_sha"],root=workspace_root)
 try:
  mutation=apply_file_changes(w["path"],changes=p["changes"],allowed_paths=p["allowed_paths"])
  try:
   proc=subprocess.run(p["verification_argv"],cwd=w["path"],text=True,capture_output=True,timeout=timeout,env={"PATH":__import__("os").environ.get("PATH",""),"CI":"1"})
   rc=proc.returncode;timed_out=False;stdout=proc.stdout[-4000:];stderr=proc.stderr[-4000:]
  except subprocess.TimeoutExpired as exc:
   rc=124;timed_out=True;stdout=(exc.stdout or "")[-4000:] if isinstance(exc.stdout,str) else "";stderr=(exc.stderr or "")[-4000:] if isinstance(exc.stderr,str) else ""
  state="READY_FOR_CONVERGENCE" if rc==0 and not timed_out else "VERIFICATION_FAILED"
  return {"schema_version":1,"proposal_sha256":ph,"workspace_id":w["workspace_id"],"workspace_path":w["path"],"source_sha":p["source_sha"],
          "changed_paths":mutation["changed_paths"],"diff_sha256":mutation["diff_sha256"],"verification":{"argv":p["verification_argv"],"exit_code":rc,"timed_out":timed_out,"stdout_tail":stdout,"stderr_tail":stderr},"state":state,"main_mutated":False}
 finally:
  if not keep_workspace: cleanup_workspace(repo,w["path"])
