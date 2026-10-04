from __future__ import annotations
from dataclasses import asdict
from conversation_intent import IntentTurn,reduce_intent
from intent_capability import Intent,reconcile
from self_hosting_planner import plan_from_reconciliation
from feedback_loop import apply_feedback

def tick(*,project:str,turns:list[IntentTurn],intent_id:str,required_capabilities:list[str],capabilities:list,work_items:list[dict])->dict:
 state=reduce_intent(turns,intent_id)
 latest=state.get("latest_direction") or {}
 statement=latest.get("text","")
 if not state["active"]:
  fb=apply_feedback(project=project,intent_state=state,feedback_text=statement,artifact_ref=None,work_items=work_items,requirement=required_capabilities[0] if required_capabilities else intent_id,evidence_ref="turn:"+latest.get("turn_id","unknown"))
  return {"intent_state":state,"reconciliation":None,"plan":{"work_items":[],"dispatch":[],"human_interruptions":[]},"revision":fb,"status":"UPDATED"}
 rec=reconcile([Intent(intent_id,statement,tuple(required_capabilities))],capabilities)
 # Feedback/correction after generation 1 must reconcile obsolete work before planning the new generation.
 revision=None
 if state["generation"]>1:
  last_turn=next((t for t in reversed(turns) if t.intent_id==intent_id and t.id==latest.get("turn_id")),None)
  revision=apply_feedback(project=project,intent_state=state,feedback_text=statement,artifact_ref=getattr(last_turn,"artifact_ref",None),work_items=work_items,requirement=required_capabilities[0] if required_capabilities else intent_id,evidence_ref="turn:"+latest.get("turn_id","unknown"))
  # apply_feedback already creates the revision work; avoid duplicate gap work.
  plan={"schema_version":1,"project":project,"admitted":True,"errors":[],"work_items":revision["created"],"dispatch":revision["dispatch"],"human_interruptions":[],"summary":{"work_items":len(revision["created"]),"dispatchable":sum(x["schedule_state"]=="DISPATCHABLE" for x in revision["dispatch"]),"human_interruptions":0}}
 else:
  plan=plan_from_reconciliation(rec,project)
 intent_state=rec["intents"][0]["state"] if rec.get("intents") else "NEEDS_INTENT"
 status="NEEDS_INTENT" if plan.get("human_interruptions") else ("VERIFIED" if intent_state=="VERIFIED" else "WORKING")
 return {"schema_version":1,"project":project,"intent_state":state,"reconciliation":rec,"plan":plan,"revision":revision,"status":status}
