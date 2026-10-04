from __future__ import annotations
import hashlib
from command_processor import Command

SAFE_ACTIONS={"RUN_VERIFICATION","READ_PROJECT_STATE","BUILD_PREVIEW"}
ASSURANCE_RANK={"A0":0,"A1":1,"A2":2,"A3":3,"A4":4,"A5":5}

def admit(item:dict, dispatch:dict, *, action_kind:str, max_auto_assurance:str="A2")->dict:
 if item.get("state") in {"PROTECT","SUPERSEDED","RESOLVED","PENDING_RESOLUTION"}:
  return {"decision":"DENY","reason":"WORK_STATE_NOT_EXECUTABLE"}
 if dispatch.get("schedule_state")!="DISPATCHABLE":
  return {"decision":"DENY","reason":"NOT_DISPATCHABLE"}
 if item.get("needs_intent") or item.get("human_authority_unresolved"):
  return {"decision":"DENY","reason":"HUMAN_INTENT_OR_AUTHORITY_REQUIRED"}
 if action_kind not in SAFE_ACTIONS:
  return {"decision":"DENY","reason":"ACTION_NOT_IN_AUTOPILOT_ALLOWLIST"}
 req=item.get("required_assurance","A5")
 if req not in ASSURANCE_RANK or max_auto_assurance not in ASSURANCE_RANK:
  return {"decision":"DENY","reason":"UNKNOWN_ASSURANCE_LEVEL"}
 if ASSURANCE_RANK[req]>ASSURANCE_RANK[max_auto_assurance]:
  return {"decision":"DENY","reason":"ASSURANCE_EXCEEDS_AUTOPILOT_BOUNDARY"}
 return {"decision":"ALLOW","reason":"SAFE_AUTOPILOT_BOUNDARY"}

def make_command(item:dict, *, action_kind:str, subject_sha:str|None=None)->Command:
 seed=f'{item["project"]}|{item["id"]}|{action_kind}|{subject_sha or "no-sha"}'
 cid=hashlib.sha256(seed.encode()).hexdigest()[:24]
 return Command(command_id=cid,idempotency_key="autopilot:"+hashlib.sha256(seed.encode()).hexdigest(),action_kind=action_kind,side_effecting=False,policy_decision="ALLOW")
