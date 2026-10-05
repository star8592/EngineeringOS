from __future__ import annotations
import json,pathlib,datetime as dt

TERMINAL={"ACCEPTED","CANCELLED"}
ACTIVE={"ARMED","RUNNING","WAITING_EXTERNAL","BACKOFF","WAITING_HUMAN"}

def _path(runtime_root,project):
    return pathlib.Path(runtime_root)/"projects"/project/"run.json"

def _now():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def read_run(runtime_root,project):
    p=_path(runtime_root,project)
    return json.loads(p.read_text()) if p.exists() else None

def _write(runtime_root,project,obj):
    p=_path(runtime_root,project);p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_suffix(".tmp");tmp.write_text(json.dumps(obj,sort_keys=True,ensure_ascii=False)+"\n");tmp.replace(p)
    return obj

def arm_run(runtime_root,project,*,intent_id,conversation_id,command_id,acceptance="ALL_INTENT_WORK_RESOLVED"):
    previous=read_run(runtime_root,project) or {}
    generation=int(previous.get("generation",0))+1
    return _write(runtime_root,project,{
        "schema_version":1,"project":project,"run_id":f"{project}:{intent_id}:{generation}",
        "generation":generation,"intent_id":intent_id,"conversation_id":conversation_id,
        "source_command_id":command_id,"state":"ARMED","acceptance":acceptance,
        "created_at":_now(),"updated_at":_now(),"last_action":None,"waiting_reason":None,
    })

def transition(runtime_root,project,state,*,action=None,reason=None):
    if state not in ACTIVE|TERMINAL: raise ValueError("INVALID_RUN_STATE")
    cur=read_run(runtime_root,project)
    if not cur: raise ValueError("RUN_NOT_ARMED")
    if cur.get("state") in TERMINAL: return cur
    nxt={**cur,"state":state,"updated_at":_now(),"last_action":action,"waiting_reason":reason}
    return _write(runtime_root,project,nxt)

def reconcile_run(runtime_root,project,project_state,decision=None):
    cur=read_run(runtime_root,project)
    if not cur:return None
    intent=cur.get("intent_id")
    items=[x for x in project_state.get("work_items",{}).values() if x.get("intent_id")==intent and x.get("state")!="SUPERSEDED"]
    if items and all(x.get("state")=="RESOLVED" for x in items):
        return transition(runtime_root,project,"ACCEPTED",action="ACCEPTANCE_CONTRACT_SATISFIED")
    action=(decision or {}).get("action")
    if action=="WAIT_FOR_INTENT":
        return transition(runtime_root,project,"WAITING_HUMAN",action=action,reason=(decision or {}).get("reason"))
    if action=="BACKOFF":
        return transition(runtime_root,project,"BACKOFF",action=action,reason=(decision or {}).get("reason"))
    if action in {"ADVANCE","OBSERVE"}:
        return transition(runtime_root,project,"RUNNING",action=action)
    return cur
