#!/usr/bin/env python3
from __future__ import annotations
import argparse,datetime as dt,hashlib,importlib.util,json,os,pathlib,subprocess,sys,tempfile

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"/"engineeringos"))
from chatgpt_tool_surface_adapter import adapt

def sha256(path:pathlib.Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def atomic_json(path:pathlib.Path,obj:dict)->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+"\n").encode()
    fd,tmp=tempfile.mkstemp(prefix=path.name+".",suffix=".tmp",dir=path.parent)
    try:
        with os.fdopen(fd,"wb") as f:
            f.write(raw);f.flush();os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)

def load_module(path:pathlib.Path,name:str):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:raise RuntimeError("MODULE_LOAD_FAILED:"+str(path))
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def run(profile_path:pathlib.Path,host_raw:pathlib.Path,output:pathlib.Path)->dict:
    profile=json.loads(profile_path.read_text())
    if profile.get("schema_version")!=1 or profile.get("authority")!="BACKEND_OWNED_CANONICAL_CONTRACT":
        raise RuntimeError("BACKEND_SURFACE_PROFILE_INVALID")
    repo=pathlib.Path(profile["repo"])
    raw=json.loads(host_raw.read_text())
    host=adapt(raw)
    with tempfile.TemporaryDirectory(prefix="engineeringos-devcontrol-surface-") as td:
        td=pathlib.Path(td);host_path=td/"host.json";canonical_path=td/"canonical.json"
        host_path.write_text(json.dumps(host,ensure_ascii=False,indent=2,sort_keys=True)+"\n")
        checker=subprocess.run([sys.executable,str(repo/profile["canonical_checker"]),"--live",profile["live_base"]],cwd=repo,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        canonical_provider=load_module(repo/profile["canonical_catalog_provider"],"devcontrol_chatgpt_product_readiness")
        try:
            canonical=canonical_provider.live_catalog(profile["live_base"],canonical_provider.MODERN_ERA,"declared")
            canonical_path.write_text(json.dumps(canonical,ensure_ascii=False,indent=2,sort_keys=True)+"\n")
            verifier=subprocess.run([sys.executable,str(repo/profile["host_verifier"]),str(canonical_path),str(host_path)],cwd=repo,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            canonical_error=None
        except Exception as exc:
            verifier=None;canonical_error=type(exc).__name__+":"+str(exc)[:1000]
        version=(repo/"VERSION").read_text().strip() if (repo/"VERSION").exists() else None
        head=subprocess.check_output(["git","-C",str(repo),"rev-parse","HEAD"],text=True).strip()
        source_live_ok=checker.returncode==0
        host_ok=verifier is not None and verifier.returncode==0
        state="OBSERVED_MATCH" if source_live_ok and host_ok else "TOOL_SURFACE_DRIFT"
        payload={
            "schema_version":1,
            "backend":profile["backend"],
            "authority":profile["authority"],
            "state":state,
            "observed_at":dt.datetime.now(dt.timezone.utc).isoformat(),
            "backend_version":version,
            "backend_source_head":head,
            "host_tool_count":len(host["tools"]),
            "source_live_check":"PASS" if source_live_ok else "FAIL",
            "host_observable_contract_check":"PASS" if host_ok else "FAIL",
            "host_acceptance":"NOT_PROVEN_BY_SURFACE_OBSERVATION",
            "source_live_output":checker.stdout.strip()[-4000:],
            "host_verifier_output":(verifier.stdout.strip()[-4000:] if verifier is not None else canonical_error),
            "host_surface_sha256":sha256(host_path),
            "canonical_catalog_sha256":(sha256(canonical_path) if canonical_path.exists() else None),
        }
    atomic_json(output,payload)
    return payload

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--profile",type=pathlib.Path,default=ROOT/"project_profiles/devcontrol/backend-surface.json")
    p.add_argument("--host-raw",type=pathlib.Path,required=True)
    p.add_argument("--output",type=pathlib.Path,default=ROOT/".engineeringos/runtime/backends/DevControl/surface-evidence.json")
    a=p.parse_args();result=run(a.profile,a.host_raw,a.output)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result["state"]=="OBSERVED_MATCH" else 2

if __name__=="__main__":
    raise SystemExit(main())
