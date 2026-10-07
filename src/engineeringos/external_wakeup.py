from __future__ import annotations
import json,pathlib,datetime as dt
from durable_run import read_run,transition

def _path(runtime_root,project):
    return pathlib.Path(runtime_root)/"projects"/project/"wake-events.jsonl"

def record_external_wait(runtime_root,project,*,kind,correlation_id,detail=None):
    cur=read_run(runtime_root,project)
    if not cur: raise ValueError("RUN_NOT_ARMED")
    transition(runtime_root,project,"WAITING_EXTERNAL",action="WAIT_EXTERNAL",reason=kind)
    p=_path(runtime_root,project);p.parent.mkdir(parents=True,exist_ok=True)
    row={"time":dt.datetime.now(dt.timezone.utc).isoformat(),"type":"WAIT","kind":kind,"correlation_id":correlation_id,"detail":detail or {}}
    with p.open("a",encoding="utf-8") as f:f.write(json.dumps(row,sort_keys=True,ensure_ascii=False)+"\n")
    return row

def wake(runtime_root,project,*,kind,correlation_id,detail=None):
    cur=read_run(runtime_root,project)
    if not cur:return {"state":"IGNORED","reason":"RUN_NOT_ARMED"}
    p=_path(runtime_root,project);p.parent.mkdir(parents=True,exist_ok=True)
    row={"time":dt.datetime.now(dt.timezone.utc).isoformat(),"type":"WAKE","kind":kind,"correlation_id":correlation_id,"detail":detail or {}}
    with p.open("a",encoding="utf-8") as f:f.write(json.dumps(row,sort_keys=True,ensure_ascii=False)+"\n")
    run=transition(runtime_root,project,"ARMED",action="EXTERNAL_EVENT",reason=None)
    # Clear backoff so the next supervisor cycle is immediately eligible.
    cp=pathlib.Path(runtime_root)/"projects"/project/"continuous.json"
    if cp.exists():
        data=json.loads(cp.read_text());data["next_eligible_at"]=0
        tmp=cp.with_suffix(".tmp");tmp.write_text(json.dumps(data,sort_keys=True,ensure_ascii=False)+"\n");tmp.replace(cp)
    return {"state":"WOKEN","event":row,"run":run}
