from __future__ import annotations
from intent_revision import reconcile_revision,make_revision_work
from scheduler import schedule

def apply_feedback(*,project:str,intent_state:dict,feedback_text:str,artifact_ref:str|None,work_items:list[dict],requirement:str,evidence_ref:str)->dict:
 gen=int(intent_state["generation"])
 rec=reconcile_revision(intent_id=intent_state["intent_id"],generation=gen,active=intent_state["active"],latest_direction=intent_state.get("latest_direction",{}).get("text"),work_items=work_items,evidence_ref=evidence_ref)
 created=[]
 if intent_state["active"]:
  item=make_revision_work(project=project,intent_id=intent_state["intent_id"],generation=gen,statement=feedback_text,requirement=requirement)
  item["feedback_artifact_ref"]=artifact_ref
  created.append(item)
 dispatch=schedule(created)
 return {"reconciliation":rec,"created":created,"dispatch":dispatch,
         "user_message":{"status":"WORKING" if created else "UPDATED","text":"收到，我按你的反馈继续调整。","artifact_ref":artifact_ref}}
