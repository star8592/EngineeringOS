from __future__ import annotations
import dataclasses,hashlib,os,pathlib,subprocess,tempfile,time
from coding_agent_provider import TaskEnvelope,CodingAgentProvider,validate_candidate
from isolated_dependencies import materialize_node_modules

class DeferredCandidateError(RuntimeError):pass

def _git(repo:pathlib.Path,*args:str,check=True)->str:
 p=subprocess.run(["git","-C",str(repo),*args],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 if check and p.returncode:raise DeferredCandidateError("GIT_"+args[0].upper().replace("-","_")+"_FAILED:"+p.stderr[-800:])
 return p.stdout.strip()

def _status_fp(repo:pathlib.Path)->str:
 raw=subprocess.check_output(["git","-C",str(repo),"status","--porcelain=v1","-z","--branch"])
 return hashlib.sha256(raw).hexdigest()

def _source_file(repo:pathlib.Path,sha:str,rel:str)->str:
 p=subprocess.run(["git","-C",str(repo),"show",f"{sha}:{rel}"],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 if p.returncode:raise DeferredCandidateError("SOURCE_FILE_UNAVAILABLE:"+rel)
 return p.stdout

def _verification_state(rc:int,timed_out:bool,stdout:str,stderr:str,source_unchanged:bool)->str:
 if not source_unchanged:return "SOURCE_CHANGED_DURING_PREPARATION"
 combined=stdout+"\n"+stderr
 if "Symlink [project]/node_modules is invalid" in combined:return "VERIFICATION_ENVIRONMENT_INVALID"
 if "Cannot find module" in combined and "node_modules" in combined:return "VERIFICATION_ENVIRONMENT_INVALID"
 if rc==0 and not timed_out:return "VERIFIED_DEFERRED_CANDIDATE"
 return "VERIFICATION_FAILED"

def _verify_candidate(repo:pathlib.Path,task:TaskEnvelope,candidate,*,verification_timeout:int,head_before:str,status_before:str,started:float)->dict:
 with tempfile.TemporaryDirectory(prefix="engineeringos-deferred-candidate-",dir=str(repo.parent)) as td:
  ws=pathlib.Path(td)/"repo"
  clone=subprocess.run(["git","clone","-q","--shared","--no-checkout",str(repo),str(ws)],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  if clone.returncode:raise DeferredCandidateError("ISOLATED_CLONE_FAILED:"+clone.stderr[-800:])
  subprocess.run(["git","-C",str(ws),"checkout","-q","--detach",task.source_sha],check=True)
  dependency_materialization=materialize_node_modules(repo,ws)
  for rel,content in candidate.changes.items():
   p=(ws/rel).resolve()
   if ws not in p.parents:raise DeferredCandidateError("PATH_ESCAPE")
   p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content)
  changed=[x for x in _git(ws,"diff","--name-only").splitlines() if x]
  if sorted(changed)!=sorted(task.allowed_paths):raise DeferredCandidateError("ACTUAL_MUTATION_SURFACE_DRIFT")
  patch=subprocess.check_output(["git","-C",str(ws),"diff","--binary","--",*task.allowed_paths],text=True)
  if not patch.strip():raise DeferredCandidateError("EMPTY_CANDIDATE_DIFF")
  diff_sha=hashlib.sha256(patch.encode()).hexdigest()
  try:
   proc=subprocess.run(list(task.verification_argv),cwd=ws,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=verification_timeout,
                       env={**os.environ,"CI":"1"})
   timed_out=False;rc=proc.returncode;stdout=proc.stdout[-6000:];stderr=proc.stderr[-6000:]
  except subprocess.TimeoutExpired as exc:
   timed_out=True;rc=124;stdout=(exc.stdout or "")[-6000:] if isinstance(exc.stdout,str) else "";stderr=(exc.stderr or "")[-6000:] if isinstance(exc.stderr,str) else ""
 elapsed_ms=round((time.monotonic()-started)*1000)
 head_after=_git(repo,"rev-parse","HEAD");status_after=_status_fp(repo)
 source_unchanged=head_before==head_after and status_before==status_after
 state=_verification_state(rc,timed_out,stdout,stderr,source_unchanged)
 return {
  "schema_version":1,"state":state,"project":task.project,"item_id":task.item_id,"source_sha":task.source_sha,
  "goal":task.goal,"allowed_paths":list(task.allowed_paths),"verification_argv":list(task.verification_argv),
  "provider":candidate.provider,"model":candidate.model,"confidence":candidate.confidence,"rationale":candidate.rationale,
  "changed_paths":changed,"diff_sha256":diff_sha,"patch":patch,
  "verification":{"exit_code":rc,"timed_out":timed_out,"stdout_tail":stdout,"stderr_tail":stderr,"environment":dependency_materialization},
  "elapsed_ms":elapsed_ms,"source_unchanged":source_unchanged,
  "authority":"CANDIDATE_ONLY_NO_CONVERGENCE_AUTHORITY","convergence_authorized":False,
 }

def _source_context(repo:pathlib.Path,task:TaskEnvelope)->tuple[str,str,dict[str,str]]:
 head=_git(repo,"rev-parse","HEAD");status=_status_fp(repo)
 if head!=task.source_sha:raise DeferredCandidateError("SOURCE_SHA_DRIFT")
 files={rel:_source_file(repo,task.source_sha,rel) for rel in task.allowed_paths}
 return head,status,files

def prepare(repo_path:str|pathlib.Path,task:TaskEnvelope,provider:CodingAgentProvider,*,verification_timeout:int=900)->dict:
 repo=pathlib.Path(repo_path).resolve();head,status,files=_source_context(repo,task);started=time.monotonic()
 candidate=provider.propose(task=task,files=files);validate_candidate(task,candidate)
 return _verify_candidate(repo,task,candidate,verification_timeout=verification_timeout,head_before=head,status_before=status,started=started)

def prepare_iterative(repo_path:str|pathlib.Path,task:TaskEnvelope,provider:CodingAgentProvider,*,max_attempts:int=3,verification_timeout:int=900)->dict:
 if max_attempts<1:raise DeferredCandidateError("MAX_ATTEMPTS_REQUIRED")
 repo=pathlib.Path(repo_path).resolve();head,status,current_files=_source_context(repo,task)
 attempts=[];started=time.monotonic();current_task=task
 for n in range(1,max_attempts+1):
  candidate=provider.propose(task=current_task,files=current_files);validate_candidate(current_task,candidate)
  result=_verify_candidate(repo,current_task,candidate,verification_timeout=verification_timeout,head_before=head,status_before=status,started=started)
  attempts.append({"attempt":n,"state":result["state"],"provider":candidate.provider,"model":candidate.model,"diff_sha256":result["diff_sha256"],
                   "verification":result["verification"],"rationale":candidate.rationale})
  if result["state"]=="VERIFIED_DEFERRED_CANDIDATE":
   result["attempts"]=attempts;result["attempt_count"]=n;return result
  if result["state"] in {"SOURCE_CHANGED_DURING_PREPARATION","VERIFICATION_ENVIRONMENT_INVALID"}:
   result["attempts"]=attempts;result["attempt_count"]=n;return result
  current_files=dict(candidate.changes)
  previous={"attempt":n,"rationale":candidate.rationale,"verification":result["verification"],
            "instruction":"Repair the candidate based on this verification failure. Preserve the original goal and exact allowed paths. Return full replacement text again."}
  current_task=dataclasses.replace(task,context={**task.context,"previous_attempt":previous})
 result["attempts"]=attempts;result["attempt_count"]=max_attempts
 return result
