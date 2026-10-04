from __future__ import annotations
import hashlib

def gap_work_items(reconciliation:dict, project:str)->list[dict]:
 out=[]
 for row in reconciliation.get("intents",[]):
  intent=row["intent"]
  if row["state"]=="NEEDS_INTENT":
   continue
  for req in row.get("requirements",[]):
   if req["state"]=="VERIFIED":
    continue
   kind="CAPABILITY_GAP" if req["state"]=="UNKNOWN" else "VERIFICATION_GAP"
   seed=f'{project}|{intent["id"]}|{kind}|{req["requirement"]}'
   wid=("gap-" if kind=="CAPABILITY_GAP" else "verify-")+hashlib.sha256(seed.encode()).hexdigest()[:12]
   out.append({
    "id":wid,"project":project,"kind":kind,
    "intent_id":intent["id"],"requirement":req["requirement"],
    "expected_outcome":intent["statement"],
    "state":"DISCOVERED","automation":"REVIEW",
    "required_assurance":"A2",
    "completion_predicate":{
      "type":"CAPABILITY_EVIDENCE",
      "requirement":req["requirement"],
      "accepted_states":["VERIFIED"]
    },
    "reason":("Active human intent is clear, but the required capability has not been discovered." if kind=="CAPABILITY_GAP" else "The capability is discovered, but current evidence does not verify its behavior." )
   })
 return out

def user_interruptions(reconciliation:dict)->list[dict]:
 out=[]
 for row in reconciliation.get("intents",[]):
  if row["state"]=="NEEDS_INTENT":
   out.append({"intent_id":row["intent"]["id"],"question":"I need the desired outcome clarified before I can continue safely."})
 return out
