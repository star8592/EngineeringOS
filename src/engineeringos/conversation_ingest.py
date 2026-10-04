from __future__ import annotations
from dataclasses import dataclass
from project_journal import append,events
from project_replay import replay_project
from durable_supervisor_runtime import journal_path
import hashlib

KINDS={"DESIRE","FEEDBACK","CORRECTION","REVERSAL","QUESTION","APPROVAL","ARTIFACT","INTERRUPTION"}
class ConversationCommandError(ValueError):pass

def _state(root,project):
 p=journal_path(root,project);return replay_project(events(p)) if p.exists() else {"project":project,"intents":{},"work_items":{},"conversation_turns":[],"last_seq":0}
def _ensure_planning_work(path,project,intent_id,generation,statement,capabilities):
 for requirement in capabilities:
  seed=f"{project}|{intent_id}|{generation}|{requirement}";wid="plan-"+hashlib.sha256(seed.encode()).hexdigest()[:12]
  append(path,project=project,typ="WORK_DISCOVERED",key=wid,generation=generation,payload={"project":project,"kind":"CAPABILITY_PLANNING","intent_id":intent_id,"intent_generation":generation,"requirement":requirement,"expected_outcome":statement,"automation":"REVIEW","required_assurance":"A2","completion_predicate":{"type":"CAPABILITY_EVIDENCE","requirement":requirement,"accepted_states":["VERIFIED"]}})

def _reconcile_old_work(path,project,st,intent_id,generation,command_id):
 for item in st.get("work_items",{}).values():
  if item.get("intent_id")!=intent_id or int(item.get("intent_generation",0))>=generation or item.get("state") in {"RESOLVED","SUPERSEDED","PROTECT"}:continue
  if item.get("state") in {"IN_PROGRESS","PENDING_RESOLUTION"} and not item.get("safe_to_supersede",False):
   append(path,project=project,typ="WORK_PROTECTED",key=item["id"],generation=generation,payload={"protection_reason":"Intent changed while work was in flight without safe-supersession evidence.","superseded_by_intent_revision":f"{intent_id}@{generation}","source_command_id":command_id})
  else:
   append(path,project=project,typ="WORK_SUPERSEDED",key=item["id"],generation=generation,payload={"superseded_by_intent_revision":f"{intent_id}@{generation}","supersession_evidence_refs":[f"conversation-command:{command_id}"]})

def ingest(root,*,project,command_id,conversation_id,kind,text,intent_id=None,artifact_ref=None,affects_task=True,required_capabilities=None):
 if kind not in KINDS:raise ConversationCommandError("UNKNOWN_KIND")
 if not command_id or not conversation_id or not text.strip():raise ConversationCommandError("COMMAND_ID_CONVERSATION_TEXT_REQUIRED")
 if kind in {"DESIRE","CORRECTION","REVERSAL","FEEDBACK","APPROVAL"} and not intent_id:raise ConversationCommandError("INTENT_ID_REQUIRED")
 st=_state(root,project);cur=st["intents"].get(intent_id,{}) if intent_id else {};gen=int(cur.get("generation",0))
 if kind in {"DESIRE","CORRECTION","REVERSAL"}:gen+=1
 p=journal_path(root,project)
 if kind in {"CORRECTION","REVERSAL"}:_reconcile_old_work(p,project,st,intent_id,gen,command_id)
 turn={"command_id":command_id,"conversation_id":conversation_id,"kind":kind,"text":text,"intent_id":intent_id,"artifact_ref":artifact_ref,"affects_task":bool(affects_task)}
 append(p,project=project,typ="CONVERSATION_TURN",key=command_id,generation=gen,payload=turn,idempotency_key="conversation:"+command_id)
 if kind in {"DESIRE","CORRECTION"}:
  caps=list(required_capabilities if required_capabilities is not None else cur.get("required_capabilities",[]))
  append(p,project=project,typ="INTENT_REVISED" if cur else "INTENT_RECORDED",key=intent_id,generation=gen,payload={"statement":text,"required_capabilities":caps,"source_command_id":command_id})
  _ensure_planning_work(p,project,intent_id,gen,text,caps)
 elif kind=="REVERSAL":
  append(p,project=project,typ="INTENT_REVERSED",key=intent_id,generation=gen,payload={"statement":text,"required_capabilities":list(cur.get("required_capabilities",[])),"source_command_id":command_id})
 return _state(root,project)
