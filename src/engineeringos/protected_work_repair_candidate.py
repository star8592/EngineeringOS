from __future__ import annotations
import hashlib,json,pathlib,time
from coding_agent_provider import TaskEnvelope,CodingAgentProvider,validate_candidate
from protected_work_composed_verifier import verify_composed,ProtectedCompositionError

class ProtectedRepairError(RuntimeError):pass

def _fingerprint_changes(changes:dict[str,str])->str:
 raw=json.dumps(changes,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()
 return hashlib.sha256(raw).hexdigest()

def _current_files(repo:pathlib.Path,inventory:dict,allowed_paths:tuple[str,...])->dict[str,str]:
 protected={x.get("path") for x in inventory.get("paths",[]) if x.get("path")}
 if not set(allowed_paths).issubset(protected):
  raise ProtectedRepairError("ALLOWED_PATH_OUTSIDE_PROTECTED_WORK")
 files={}
 for rel in allowed_paths:
  p=repo/rel
  if not p.is_file():raise ProtectedRepairError("PROTECTED_SOURCE_FILE_UNAVAILABLE:"+rel)
  files[rel]=p.read_text()
 return files

def prepare(repo_path:str|pathlib.Path,inventory:dict,deferred_candidate:dict,task:TaskEnvelope,provider:CodingAgentProvider,*,verification_timeout:int=900)->dict:
 repo=pathlib.Path(repo_path).resolve()
 head=inventory.get("head")
 if not head or task.source_sha!=head or deferred_candidate.get("source_sha")!=head:
  raise ProtectedRepairError("SOURCE_SHA_DRIFT")
 if deferred_candidate.get("state")!="VERIFIED_DEFERRED_CANDIDATE":
  raise ProtectedRepairError("VERIFIED_DEFERRED_CANDIDATE_REQUIRED")
 files=_current_files(repo,inventory,task.allowed_paths)
 started=time.monotonic()
 candidate=provider.propose(task=task,files=files);validate_candidate(task,candidate)
 composed=verify_composed(repo,inventory,deferred_candidate,list(task.verification_argv),replacements=candidate.changes,timeout_seconds=verification_timeout)
 state="VERIFIED_PROTECTED_REPAIR_CANDIDATE" if composed.get("state")=="PASS" else ("SOURCE_CHANGED_DURING_PREPARATION" if composed.get("state")=="SOURCE_CHANGED_DURING_VERIFY" else "VERIFICATION_FAILED")
 return {
  "schema_version":1,"state":state,"project":task.project,"item_id":task.item_id,"source_sha":task.source_sha,
  "goal":task.goal,"allowed_paths":list(task.allowed_paths),"verification_argv":list(task.verification_argv),
  "provider":candidate.provider,"model":candidate.model,"confidence":candidate.confidence,"rationale":candidate.rationale,
  "changes":candidate.changes,"changes_sha256":_fingerprint_changes(candidate.changes),
  "composed_verification":composed,"elapsed_ms":round((time.monotonic()-started)*1000),
  "authority":"CANDIDATE_ONLY_NO_CONVERGENCE_AUTHORITY","convergence_authorized":False,
 }
