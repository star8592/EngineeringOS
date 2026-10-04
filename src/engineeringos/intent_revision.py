from __future__ import annotations
import hashlib

ACTIVE={"DISCOVERED","REOPENED","IN_PROGRESS","PENDING_RESOLUTION"}

def revision_id(intent_id:str,generation:int)->str:
 return f"{intent_id}@{generation}"

def reconcile_revision(*, intent_id:str, generation:int, active:bool, latest_direction:str|None, work_items:list[dict], evidence_ref:str)->dict:
 """Reconcile work created for older generations of one intent."""
 current=revision_id(intent_id,generation); changed=[]; protected=[]
 for item in work_items:
  if item.get("intent_id")!=intent_id or item.get("state") not in ACTIVE: continue
  item_gen=int(item.get("intent_generation",1))
  if item_gen>=generation: continue
  if item.get("state") in {"IN_PROGRESS","PENDING_RESOLUTION"} and not item.get("safe_to_supersede",False):
   item["state"]="PROTECT"
   item["superseded_by_intent_revision"]=current
   item["protection_reason"]="In-flight work lacks evidence that it is safe to supersede automatically."
   protected.append(item["id"]);continue
  item["state"]="SUPERSEDED"
  item["superseded_by_intent_revision"]=current
  item["supersession_evidence_refs"]=list(dict.fromkeys((item.get("supersession_evidence_refs") or [])+[evidence_ref]))
  changed.append(item["id"])
 return {"intent_revision":current,"active":active,"latest_direction":latest_direction,"superseded":changed,"protected":protected}

def make_revision_work(*, project:str,intent_id:str,generation:int,statement:str,requirement:str)->dict:
 seed=f"{project}|{intent_id}|{generation}|{requirement}"
 return {"id":"rev-"+hashlib.sha256(seed.encode()).hexdigest()[:12],"project":project,"kind":"INTENT_REVISION",
         "intent_id":intent_id,"intent_generation":generation,"expected_outcome":statement,"requirement":requirement,
         "state":"DISCOVERED","automation":"REVIEW","required_assurance":"A2",
         "completion_predicate":{"type":"CAPABILITY_EVIDENCE","requirement":requirement,"accepted_states":["VERIFIED"]}}
