from __future__ import annotations
from dataclasses import dataclass,asdict
from typing import Iterable

@dataclass(frozen=True)
class Intent:
 id:str
 statement:str
 required_capabilities:tuple[str,...]
 source:str="human"
 status:str="ACTIVE"

@dataclass(frozen=True)
class Capability:
 id:str
 label:str
 evidence:tuple[str,...]
 confidence:float=1.0
 verification_level:str="DISCOVERED"

def normalize(text:str)->str:
 return " ".join(text.lower().replace("_"," ").replace("-"," ").replace("/"," ").replace(":"," ").split())

def reconcile(intents:Iterable[Intent], capabilities:Iterable[Capability])->dict:
 caps=list(capabilities); rows=[]; needs_intent=[]
 for intent in intents:
  required=[]
  for req in intent.required_capabilities:
   n=normalize(req); matches=[]
   for cap in caps:
    hay=normalize(cap.id+" "+cap.label)
    if n==normalize(cap.id) or n==normalize(cap.label) or n in hay:
     matches.append(cap)
   if matches:
    level="VERIFIED" if any(c.verification_level=="VERIFIED" for c in matches) else "DISCOVERED"
    required.append({"requirement":req,"state":level,"capability_ids":[c.id for c in matches],"evidence":[e for c in matches for e in c.evidence]})
   else:
    required.append({"requirement":req,"state":"UNKNOWN","capability_ids":[],"evidence":[]})
  state="VERIFIED" if required and all(x["state"]=="VERIFIED" for x in required) else ("DISCOVERED" if required and all(x["state"] in ("VERIFIED","DISCOVERED") for x in required) else ("UNKNOWN" if required else "NEEDS_INTENT"))
  if not intent.statement.strip() or not required: needs_intent.append(intent.id)
  rows.append({"intent":asdict(intent),"state":state,"requirements":required})
 return {"schema_version":1,"intents":rows,"needs_intent":needs_intent,
         "summary":{"verified":sum(x["state"]=="VERIFIED" for x in rows),"discovered":sum(x["state"]=="DISCOVERED" for x in rows),"unknown":sum(x["state"]=="UNKNOWN" for x in rows),"needs_intent":sum(x["state"]=="NEEDS_INTENT" for x in rows)}}

def capabilities_from_doctor(report:dict)->list[Capability]:
 u=report.get("software_understanding",{}); out=[]
 for route in u.get("visible_capabilities",[]):
  out.append(Capability("surface:"+route,route,(f"route:{route}",),0.9))
 for cmd in u.get("verification_commands",[]):
  out.append(Capability("verification:"+cmd,cmd,(f"declared-command:{cmd}",),1.0,"DECLARED_CHECK"))
 return out
