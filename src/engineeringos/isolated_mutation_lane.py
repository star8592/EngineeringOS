from __future__ import annotations
import hashlib,json,pathlib,subprocess,tempfile,shutil,os
from dataclasses import dataclass

class MutationLaneError(ValueError): pass

PROTECTED_PREFIXES=(".git/",".engineeringos/")
PROTECTED_EXACT={".git",".engineeringos"}

def _git(repo,*args): return subprocess.check_output(["git","-C",str(repo),*args],text=True).strip()

def validate_paths(paths:list[str], allowed_paths:list[str])->None:
 allowed=set(allowed_paths)
 if not paths: raise MutationLaneError("EMPTY_MUTATION_SURFACE")
 for raw in paths:
  p=pathlib.PurePosixPath(raw)
  s=p.as_posix()
  if p.is_absolute() or ".." in p.parts: raise MutationLaneError("PATH_ESCAPE")
  if s in PROTECTED_EXACT or any(s.startswith(x) for x in PROTECTED_PREFIXES): raise MutationLaneError("PROTECTED_PATH")
  if s not in allowed: raise MutationLaneError("PATH_OUTSIDE_DECLARED_SURFACE:"+s)

def workspace_identity(project:str,item_id:str,source_sha:str)->str:
 return hashlib.sha256(f"{project}|{item_id}|{source_sha}".encode()).hexdigest()[:16]

def create_workspace(repo:str, *, project:str,item_id:str,source_sha:str,root:str)->dict:
 repo=pathlib.Path(repo).resolve(); root=pathlib.Path(root).resolve()
 if _git(repo,"status","--porcelain"): raise MutationLaneError("SOURCE_WORKTREE_DIRTY")
 actual=_git(repo,"rev-parse","HEAD")
 if actual!=source_sha: raise MutationLaneError("SOURCE_SHA_DRIFT")
 wid=workspace_identity(project,item_id,source_sha); path=root/wid
 root.mkdir(parents=True,exist_ok=True)
 if path.exists():
  head=_git(path,"rev-parse","HEAD")
  if head!=source_sha: raise MutationLaneError("EXISTING_WORKSPACE_SHA_DRIFT")
  return {"workspace_id":wid,"path":str(path),"source_sha":source_sha,"reused":True}
 subprocess.run(["git","-C",str(repo),"worktree","add","--detach",str(path),source_sha],check=True,capture_output=True,text=True)
 return {"workspace_id":wid,"path":str(path),"source_sha":source_sha,"reused":False}

def apply_file_changes(workspace:str, *, changes:dict[str,str], allowed_paths:list[str])->dict:
 validate_paths(list(changes),allowed_paths)
 ws=pathlib.Path(workspace).resolve()
 before=_git(ws,"rev-parse","HEAD")
 for rel,content in changes.items():
  p=(ws/rel).resolve()
  if ws not in p.parents: raise MutationLaneError("PATH_ESCAPE")
  p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content)
 tracked=[x for x in _git(ws,"diff","--name-only").splitlines() if x.strip()]
 untracked=[x for x in _git(ws,"ls-files","--others","--exclude-standard").splitlines() if x.strip()]
 paths=sorted(set(tracked+untracked))
 validate_paths(paths,allowed_paths)
 diff=subprocess.check_output(["git","-C",str(ws),"diff","--binary","--",*allowed_paths],text=True)
 if untracked:
  for rel in untracked:
   diff += subprocess.check_output(["git","-C",str(ws),"diff","--no-index","--binary","/dev/null",rel],text=True,stderr=subprocess.DEVNULL) if False else "UNTRACKED:"+rel+"\n"
 return {"source_sha":before,"changed_paths":paths,"diff_sha256":hashlib.sha256(diff.encode()).hexdigest(),"diff":diff}

def cleanup_workspace(repo:str,workspace:str)->None:
 subprocess.run(["git","-C",repo,"worktree","remove","--force",workspace],check=True,capture_output=True,text=True)
