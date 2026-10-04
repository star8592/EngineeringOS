from __future__ import annotations
from dataclasses import dataclass,asdict
from datetime import datetime,timezone
from typing import Optional
import uuid

KINDS={"DESIRE","FEEDBACK","CORRECTION","REVERSAL","QUESTION","APPROVAL","ARTIFACT","INTERRUPTION"}

@dataclass(frozen=True)
class IntentTurn:
 id:str
 conversation_id:str
 kind:str
 text:str
 created_at:str
 intent_id:Optional[str]=None
 artifact_ref:Optional[str]=None
 supersedes:Optional[str]=None
 affects_task:bool=True

def new_turn(conversation_id:str,kind:str,text:str,**kwargs)->IntentTurn:
 if kind not in KINDS: raise ValueError("unknown conversational turn kind")
 return IntentTurn(str(uuid.uuid4()),conversation_id,kind,text,datetime.now(timezone.utc).isoformat(),**kwargs)

def reduce_intent(turns:list[IntentTurn], intent_id:str)->dict:
 relevant=[t for t in turns if t.intent_id==intent_id]
 active=True; statements=[]; feedback=[]; approvals=[]; artifacts=[]; generation=0
 for t in relevant:
  if t.kind in {"DESIRE","CORRECTION"}:
   generation+=1
   statements.append({"turn_id":t.id,"kind":t.kind,"text":t.text})
   active=True
  elif t.kind=="REVERSAL":
   generation+=1
   statements.append({"turn_id":t.id,"kind":t.kind,"text":t.text});active=False
  elif t.kind=="FEEDBACK": feedback.append({"turn_id":t.id,"text":t.text,"artifact_ref":t.artifact_ref})
  elif t.kind=="APPROVAL": approvals.append({"turn_id":t.id,"text":t.text,"artifact_ref":t.artifact_ref})
  elif t.kind=="ARTIFACT": artifacts.append({"turn_id":t.id,"artifact_ref":t.artifact_ref,"text":t.text})
 return {"intent_id":intent_id,"generation":generation,"active":active,"history":statements,"feedback":feedback,"approvals":approvals,"artifacts":artifacts,
         "latest_direction":statements[-1] if statements else None}

def task_effect(turn:IntentTurn)->str:
 if turn.kind=="INTERRUPTION" and not turn.affects_task:return "KEEP_TASK_YIELD_CONVERSATION"
 if turn.kind in {"CORRECTION","REVERSAL"}:return "RECONCILE_IN_FLIGHT_TASK"
 if turn.kind in {"DESIRE","FEEDBACK"}:return "UPDATE_OR_START_TASK"
 if turn.kind=="APPROVAL":return "CONTINUE"
 return "NO_TASK_CHANGE"
