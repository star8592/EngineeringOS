from __future__ import annotations
import hashlib,io,json,os,pathlib,shutil,subprocess,tarfile,tempfile,time
from protected_work_verifier import _git,_status_fingerprint,_safe_extract_tar,_overlay,_diagnostic_signature
from isolated_dependencies import materialize_node_modules

class ProtectedCompositionError(RuntimeError):pass

def _candidate_patch(candidate:dict)->str:
 patch=candidate.get("patch")
 if not isinstance(patch,str) or not patch.strip():
  raise ProtectedCompositionError("DEFERRED_CANDIDATE_PATCH_REQUIRED")
 return patch

def verify_composed(repo_path:str|pathlib.Path,inventory:dict,candidate:dict,command:list[str],*,replacements:dict[str,str]|None=None,timeout_seconds:int=900)->dict:
 repo=pathlib.Path(repo_path).resolve()
 if inventory.get("state")!="PROTECTED_EXISTING_WORK":
  raise ProtectedCompositionError("PROTECTED_INVENTORY_REQUIRED")
 source_head=_git(repo,"rev-parse","HEAD").strip()
 if inventory.get("head")!=source_head or candidate.get("source_sha")!=source_head:
  raise ProtectedCompositionError("SOURCE_SHA_DRIFT")
 if candidate.get("state")!="VERIFIED_DEFERRED_CANDIDATE":
  raise ProtectedCompositionError("VERIFIED_DEFERRED_CANDIDATE_REQUIRED")
 protected_paths={x.get("path") for x in inventory.get("paths",[]) if x.get("path")}
 candidate_paths=set(candidate.get("changed_paths") or [])
 if not candidate_paths:
  raise ProtectedCompositionError("CANDIDATE_CHANGED_PATHS_REQUIRED")
 overlap=sorted(protected_paths & candidate_paths)
 if overlap:
  raise ProtectedCompositionError("CANDIDATE_PROTECTED_PATH_OVERLAP:"+",".join(overlap))
 if any(x.get("sensitive") for x in inventory.get("paths",[])):
  raise ProtectedCompositionError("SENSITIVE_DIRTY_PATH_BLOCKED")
 status_before=_status_fingerprint(repo);started=time.monotonic()
 with tempfile.TemporaryDirectory(prefix="engineeringos-protected-composed-") as td:
  ws=pathlib.Path(td)
  archive=subprocess.check_output(["git","-C",str(repo),"archive","--format=tar",source_head])
  _safe_extract_tar(archive,ws)
  subprocess.run(["git","init","-q"],cwd=ws,check=True)
  subprocess.run(["git","config","user.email","engineeringos@local"],cwd=ws,check=True)
  subprocess.run(["git","config","user.name","EngineeringOS"],cwd=ws,check=True)
  subprocess.run(["git","add","-A"],cwd=ws,check=True)
  subprocess.run(["git","commit","-qm","composed verification base"],cwd=ws,check=True)
  patch_path=ws/".engineeringos-deferred.patch";patch_path.write_text(_candidate_patch(candidate))
  apply=subprocess.run(["git","apply","--whitespace=nowarn",str(patch_path)],cwd=ws,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  patch_path.unlink(missing_ok=True)
  if apply.returncode:
   raise ProtectedCompositionError("DEFERRED_PATCH_APPLY_FAILED:"+apply.stderr[-1000:])
  _overlay(repo,ws,inventory)
  replacement_paths=set((replacements or {}).keys())
  if not replacement_paths.issubset(protected_paths):
   raise ProtectedCompositionError("REPLACEMENT_OUTSIDE_PROTECTED_SURFACE:"+",".join(sorted(replacement_paths-protected_paths)))
  for rel,content in (replacements or {}).items():
   target=(ws/rel).resolve()
   if ws not in target.parents:raise ProtectedCompositionError("REPLACEMENT_PATH_ESCAPE:"+rel)
   target.parent.mkdir(parents=True,exist_ok=True);target.write_text(content)
  deps=materialize_node_modules(repo,ws)
  try:
   proc=subprocess.run(command,cwd=ws,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout_seconds,env={**os.environ,"CI":"1"})
   timed_out=False;rc=proc.returncode;stdout=proc.stdout;stderr=proc.stderr
  except subprocess.TimeoutExpired as exc:
   timed_out=True;rc=124
   stdout=exc.stdout if isinstance(exc.stdout,str) else ""
   stderr=exc.stderr if isinstance(exc.stderr,str) else ""
  diagnostic=_diagnostic_signature(stdout,stderr,ws,rc)
  changed=subprocess.check_output(["git","status","--porcelain=v1","-z","--untracked-files=all"],cwd=ws)
  workspace_sha=hashlib.sha256(changed).hexdigest()
 elapsed_ms=round((time.monotonic()-started)*1000)
 source_unchanged=source_head==_git(repo,"rev-parse","HEAD").strip() and status_before==_status_fingerprint(repo)
 state="PASS" if rc==0 and not timed_out and source_unchanged else ("SOURCE_CHANGED_DURING_VERIFY" if not source_unchanged else "FAIL")
 payload={
  "schema_version":1,"state":state,"source_head":source_head,"source_unchanged":source_unchanged,
  "protected_inventory_head":inventory.get("head"),"deferred_item_id":candidate.get("item_id"),
  "deferred_diff_sha256":candidate.get("diff_sha256"),"deferred_changed_paths":sorted(candidate_paths),
  "replacement_paths":sorted((replacements or {}).keys()),"protected_path_count":len(protected_paths),"command":list(command),"exit_code":rc,"timed_out":timed_out,
  "elapsed_ms":elapsed_ms,"dependency_materialization":deps,"workspace_status_sha256":workspace_sha,
  "diagnostic_signature":diagnostic,"stdout_tail":stdout[-6000:],"stderr_tail":stderr[-6000:],
  "authority":"COMPOSED_ISOLATED_VERIFICATION_ONLY","convergence_authorized":False,
 }
 return payload
