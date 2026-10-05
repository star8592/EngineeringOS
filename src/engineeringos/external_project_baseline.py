from __future__ import annotations
import datetime as dt
import hashlib
import json
import os
import pathlib
import subprocess
import tempfile

class BaselineError(ValueError):
    pass

def _run(repo:pathlib.Path,*args:str,timeout:int=20,check:bool=True)->str:
    p=subprocess.run(["git","-C",str(repo),*args],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout)
    if check and p.returncode:
        raise BaselineError("GIT_"+args[0].upper().replace("-","_")+"_FAILED:"+p.stderr[-400:])
    return p.stdout.strip()

def _names(repo:pathlib.Path,args:list[str],limit:int=200)->list[str]:
    out=_run(repo,*args)
    rows=[x for x in out.splitlines() if x]
    return sorted(rows)[:limit]

def _package_entrypoints(repo:pathlib.Path)->list[str]:
    p=repo/"package.json"
    if not p.exists():
        return []
    try:
        body=json.loads(p.read_text())
    except Exception:
        return []
    scripts=body.get("scripts") if isinstance(body,dict) else {}
    if not isinstance(scripts,dict):
        return []
    keep=[]
    for name in scripts:
        if name in {"build","lint","test","prebuild","postbuild"} or name.startswith(("test:","verify:","check:","audit:")):
            keep.append(name)
    return sorted(keep)[:120]

def inspect_project(cfg:dict)->dict:
    name=cfg.get("name")
    repo_raw=cfg.get("repo")
    if not name or not repo_raw:
        raise BaselineError("PROJECT_IDENTITY_REQUIRED")
    repo=pathlib.Path(repo_raw)
    observed_at=dt.datetime.now(dt.timezone.utc).isoformat()
    if not repo.exists():
        return {
            "schema_version":1,"project":name,"display_name":cfg.get("display_name") or name,
            "observed_at":observed_at,"state":"UNAVAILABLE","mutation_eligible":False,
            "protected_existing_work":False,"reason":"REPOSITORY_PATH_UNAVAILABLE"
        }
    try:
        top=pathlib.Path(_run(repo,"rev-parse","--show-toplevel")).resolve()
        head=_run(repo,"rev-parse","HEAD")
        branch=_run(repo,"branch","--show-current") or "DETACHED"
        origin=_run(repo,"remote","get-url","origin",check=False) or None
        modified=_names(repo,["diff","HEAD","--name-only"])
        untracked=_names(repo,["ls-files","--others","--exclude-standard"])
        dirty=bool(modified or untracked)
        upstream=_run(repo,"rev-parse","--abbrev-ref","@{upstream}",check=False) or None
        ahead=behind=None
        if upstream:
            counts=_run(repo,"rev-list","--left-right","--count",f"HEAD...{upstream}",check=False)
            parts=counts.split()
            if len(parts)==2 and all(x.isdigit() for x in parts):
                ahead,behind=map(int,parts)
        state="PROTECTED_EXISTING_WORK" if dirty else "CLEAN_CONNECTED"
        facts={
            "schema_version":1,
            "project":name,
            "display_name":cfg.get("display_name") or name,
            "observed_at":observed_at,
            "state":state,
            "canonical_repo":str(top),
            "configured_repo":str(repo.resolve()),
            "origin":origin,
            "branch":branch,
            "head":head,
            "upstream":upstream,
            "ahead":ahead,
            "behind":behind,
            "modified_paths":modified,
            "untracked_paths":untracked,
            "dirty_path_count":len(set(modified+untracked)),
            "protected_existing_work":dirty,
            "mutation_eligible":not dirty,
            "verification_entrypoints":_package_entrypoints(top),
        }
        stable={k:facts[k] for k in ("project","canonical_repo","origin","branch","head","modified_paths","untracked_paths","verification_entrypoints")}
        facts["fingerprint"]=hashlib.sha256(json.dumps(stable,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
        return facts
    except (BaselineError,subprocess.TimeoutExpired,OSError) as exc:
        return {
            "schema_version":1,"project":name,"display_name":cfg.get("display_name") or name,
            "observed_at":observed_at,"state":"INVALID_REPOSITORY","mutation_eligible":False,
            "protected_existing_work":False,"reason":type(exc).__name__+":"+str(exc)[:500]
        }

def _atomic_json(path:pathlib.Path,obj:dict)->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(obj,sort_keys=True,indent=2,ensure_ascii=False)+"\n").encode()
    fd,tmp=tempfile.mkstemp(prefix=path.name+".",suffix=".tmp",dir=path.parent)
    try:
        with os.fdopen(fd,"wb") as f:
            f.write(raw);f.flush();os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)

def refresh_registered_projects(registry_path,runtime_root)->dict:
    rp=pathlib.Path(registry_path)
    registry=json.loads(rp.read_text()) if rp.exists() else {"projects":[]}
    rows=[]
    for cfg in registry.get("projects",[]):
        row=inspect_project(cfg)
        rows.append(row)
        _atomic_json(pathlib.Path(runtime_root)/"projects"/cfg["name"]/"baseline.json",row)
    summary={"schema_version":1,"observed_at":dt.datetime.now(dt.timezone.utc).isoformat(),"projects":rows}
    _atomic_json(pathlib.Path(runtime_root)/"projects"/"baseline-summary.json",summary)
    return summary
