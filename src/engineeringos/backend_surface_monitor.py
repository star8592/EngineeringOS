from __future__ import annotations
import datetime as dt,hashlib,importlib.util,json,pathlib,subprocess,sys

class BackendSurfaceMonitorError(ValueError):
    pass

def semantic_sha256(obj:object)->str:
    raw=json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()

def _load_module(path:pathlib.Path,name:str):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:
        raise BackendSurfaceMonitorError("MODULE_LOAD_FAILED:"+str(path))
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def probe(profile:dict,*,timeout_seconds:int=45)->dict:
    if profile.get("schema_version")!=1 or profile.get("authority")!="BACKEND_OWNED_CANONICAL_CONTRACT":
        raise BackendSurfaceMonitorError("BACKEND_SURFACE_PROFILE_INVALID")
    repo=pathlib.Path(profile["repo"])
    checker=subprocess.run(
        [sys.executable,str(repo/profile["canonical_checker"]),"--live",profile["live_base"]],
        cwd=repo,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=timeout_seconds,
    )
    provider=_load_module(repo/profile["canonical_catalog_provider"],"engineeringos_backend_surface_provider")
    canonical_error=None;canonical=None
    try:
        canonical=provider.live_catalog(profile["live_base"],provider.MODERN_ERA,"declared")
    except Exception as exc:
        canonical_error=type(exc).__name__+":"+str(exc)[:1000]
    ok=checker.returncode==0 and canonical is not None
    return {
        "schema_version":1,
        "backend":profile["backend"],
        "observed_at":dt.datetime.now(dt.timezone.utc).isoformat(),
        "state":"LIVE_SURFACE_OK" if ok else "SOURCE_LIVE_DRIFT",
        "source_live_check":"PASS" if checker.returncode==0 else "FAIL",
        "canonical_catalog_semantic_sha256":semantic_sha256(canonical) if canonical is not None else None,
        "checker_output":checker.stdout.strip()[-4000:],
        "catalog_error":canonical_error,
    }

def reconcile(profile:dict,evidence:dict|None,*,timeout_seconds:int=45)->dict:
    live=probe(profile,timeout_seconds=timeout_seconds)
    out={**live,"host_observation_state":None,"host_acceptance":None}
    if live["state"]!="LIVE_SURFACE_OK":
        return {**out,"state":"TOOL_SURFACE_DRIFT","reason":"SOURCE_LIVE_SURFACE_DRIFT"}
    if not evidence:
        return {**out,"state":"HOST_OBSERVATION_MISSING","reason":"HOST_OBSERVATION_REQUIRED"}
    out["host_observation_state"]=evidence.get("state")
    out["host_acceptance"]=evidence.get("host_acceptance")
    observed_hash=evidence.get("canonical_catalog_semantic_sha256")
    if not observed_hash:
        return {**out,"state":"HOST_OBSERVATION_STALE","reason":"LEGACY_OBSERVATION_WITHOUT_SEMANTIC_HASH"}
    if observed_hash!=live["canonical_catalog_semantic_sha256"]:
        return {**out,"state":"HOST_OBSERVATION_STALE","reason":"CANONICAL_TOOL_CONTRACT_CHANGED"}
    if evidence.get("state")!="OBSERVED_MATCH" or evidence.get("host_observable_contract_check")!="PASS":
        return {**out,"state":"TOOL_SURFACE_DRIFT","reason":"HOST_OBSERVABLE_SURFACE_DRIFT"}
    return {**out,"state":"CONVERGED","reason":"CURRENT_CANONICAL_MATCHES_HOST_OBSERVATION"}
