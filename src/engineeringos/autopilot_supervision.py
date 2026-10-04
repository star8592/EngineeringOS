from __future__ import annotations
import hashlib,json,pathlib
from state_paths import runtime

def projection_fingerprint(projection:dict)->str:
 stable={"status":projection.get("status"),"intent_state":projection.get("intent_state"),
         "work_items":projection.get("work_items",[]),"dispatch":projection.get("dispatch",[]),
         "human_interruptions":projection.get("human_interruptions",[])}
 return hashlib.sha256(json.dumps(stable,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def supervisor_decision(projection:dict, previous_fingerprint:str|None=None)->dict:
 fp=projection_fingerprint(projection)
 if projection.get("human_interruptions"):
  return {"action":"WAIT_FOR_INTENT","reason":"HUMAN_INTENT_REQUIRED","fingerprint":fp,"should_notify":fp!=previous_fingerprint}
 dispatchable=[x for x in projection.get("dispatch",[]) if x.get("schedule_state")=="DISPATCHABLE"]
 if dispatchable:
  return {"action":"ADVANCE","reason":"MACHINE_WORK_AVAILABLE","fingerprint":fp,"should_notify":False,"item_ids":[x["id"] for x in dispatchable]}
 if fp==previous_fingerprint:
  return {"action":"SLEEP","reason":"NO_STATE_CHANGE","fingerprint":fp,"should_notify":False}
 return {"action":"OBSERVE","reason":"STATE_CHANGED_NO_DISPATCH","fingerprint":fp,"should_notify":False}

def bounded_history(rows:list[dict],limit:int=200)->list[dict]:
 if limit<1: raise ValueError("limit must be positive")
 return rows[-limit:]
