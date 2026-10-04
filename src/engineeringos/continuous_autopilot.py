from __future__ import annotations
import hashlib,json,datetime as dt

def fingerprint(state:dict)->str:
 stable={"intents":state.get("intents",{}),"work_items":state.get("work_items",{})}
 return hashlib.sha256(json.dumps(stable,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def next_delay(failures:int,*,base:int=30,ceiling:int=1800)->int:
 if failures<0: raise ValueError("failures must be >= 0")
 return min(ceiling,base*(2**max(0,failures-1))) if failures else 0
def classify(state:dict,previous:dict|None=None)->dict:
 previous=previous or {};fp=fingerprint(state);items=list(state.get("work_items",{}).values())
 needs=[x for x in items if x.get("needs_intent") or x.get("state")=="NEEDS_INTENT"]
 if needs:return {"action":"WAIT_FOR_INTENT","reason":"HUMAN_INTENT_REQUIRED","fingerprint":fp,"should_notify":fp!=previous.get("fingerprint"),"failures":0,"delay_seconds":0}
 machine=[x for x in items if x.get("state") not in ("RESOLVED","SUPERSEDED","PROTECT","COMMITTED") and not x.get("needs_intent")]
 if machine:
  failures=int(previous.get("failures",0))
  if previous.get("last_result")=="MACHINE_FAILURE":
   failures+=1;return {"action":"BACKOFF","reason":"MACHINE_FAILURE_RETRY","fingerprint":fp,"should_notify":False,"failures":failures,"delay_seconds":next_delay(failures)}
  return {"action":"ADVANCE","reason":"MACHINE_WORK_AVAILABLE","fingerprint":fp,"should_notify":False,"failures":0,"delay_seconds":0}
 if fp==previous.get("fingerprint"):return {"action":"SLEEP","reason":"STABLE_STATE","fingerprint":fp,"should_notify":False,"failures":0,"delay_seconds":300}
 return {"action":"OBSERVE","reason":"STATE_CHANGED_NO_MACHINE_WORK","fingerprint":fp,"should_notify":False,"failures":0,"delay_seconds":30}
def after_execution(decision:dict,result:dict)->dict:
 failed=any(x.get("state")=="REOPENED" for x in result.get("execution",{}).get("results",[]))
 out=dict(decision);out["last_result"]="MACHINE_FAILURE" if failed else "SUCCESS";return out
