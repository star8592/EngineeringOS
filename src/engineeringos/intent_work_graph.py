from __future__ import annotations
import hashlib

def gap_work_items(reconciliation:dict, project:str)->list[dict]:
 out=[]
 for row in reconciliation.get("intents",[]):
  intent=row["intent"]
  if row["state"]=="NEEDS_INTENT":
   continue
  for req in row.get("requirements",[]):
   if req["state"]!="UNKNOWN":
    continue
   seed=f'{project}|{intent["id"]}|{req["requirement"]}'
   wid="gap-"+hashlib.sha256(seed.encode()).hexdigest()[:12]
   out.append({
    "id":wid,"project":project,"kind":"CAPABILITY_GAP",
    "intent_id":intent["id"],"requirement":req["requirement"],
    "expected_outcome":intent["statement"],
    "state":"DISCOVERED","automation":"REVIEW",
    "required_assurance":"A2",
    "completion_predicate":{
      "type":"CAPABILITY_EVIDENCE",
      "requirement":req["requirement"],
      "accepted_states":["VERIFIED"]
    },
    "reason":"Active human intent is clear, but current evidence cannot verify the required capability."
   })
 return out

def user_interruptions(reconciliation:dict)->list[dict]:
 out=[]
 for row in reconciliation.get("intents",[]):
  if row["state"]=="NEEDS_INTENT":
   out.append({"intent_id":row["intent"]["id"],"question":"I need the desired outcome clarified before I can continue safely."})
 return out
