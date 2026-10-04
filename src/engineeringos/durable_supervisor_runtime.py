from __future__ import annotations
import pathlib
from project_journal import append,events
from project_replay import replay_project
from scheduler import schedule
from autopilot_supervisor import supervisor_tick

def journal_path(runtime_root,project):
 return pathlib.Path(runtime_root)/"projects"/project/"journal.jsonl"
def recover(runtime_root,project):
 p=journal_path(runtime_root,project);return replay_project(events(p)) if p.exists() else {"schema_version":1,"project":project,"intents":{},"work_items":{},"last_seq":0}
def record_intent(runtime_root,project,*,intent_id,generation,statement,required_capabilities,revision=False):
 p=journal_path(runtime_root,project);typ="INTENT_REVISED" if revision else "INTENT_RECORDED"
 return append(p,project=project,typ=typ,key=intent_id,generation=generation,payload={"statement":statement,"required_capabilities":list(required_capabilities)})
def discover_work(runtime_root,project,item):
 p=journal_path(runtime_root,project)
 payload={k:v for k,v in item.items() if k!="id"}
 return append(p,project=project,typ="WORK_DISCOVERED",key=item["id"],generation=item.get("intent_generation",0),payload=payload)
def _record_result(path,project,item,result):
 state=result["state"]; typ={"REOPENED":"WORK_REOPENED","WAITING_CONTRACT":"WORK_WAITING_CONTRACT","COMMITTED":"WORK_COMMITTED"}.get(state)
 if not typ:return None
 payload={"reason":result.get("reason")} if state!="COMMITTED" else {"commit_receipt":result["commit_receipt"],"capability_evidence":result["capability_evidence"]}
 ev=append(path,project=project,typ=typ,key=item["id"],generation=item.get("intent_generation",0),payload=payload)
 if state=="COMMITTED":
  pred=item.get("completion_predicate") or {}
  if item.get("required_assurance","A1") in ("A1","A2") and pred.get("type")=="CAPABILITY_EVIDENCE" and "VERIFIED" in pred.get("accepted_states",[]):
   refs=result.get("capability_evidence") or []
   if refs:
    append(path,project=project,typ="WORK_RESOLVED",key=item["id"],generation=item.get("intent_generation",0),payload={"verifier":"durable-supervisor","resolution_evidence_refs":refs,"requirement":pred.get("requirement")})
 return ev
def resume_once(repo,runtime_root,project,providers,*,workspace_root,verification_timeout=120):
 before=recover(runtime_root,project);items=list(before["work_items"].values());dispatch=schedule(items)
 result=supervisor_tick(repo,items,dispatch,providers,workspace_root=workspace_root,verification_timeout=verification_timeout)
 p=journal_path(runtime_root,project);by={x["id"]:x for x in items}
 for row in result["results"]:
  if row["item_id"] in by:_record_result(p,project,by[row["item_id"]],row)
 return {"before":before,"dispatch":dispatch,"execution":result,"after":recover(runtime_root,project)}
