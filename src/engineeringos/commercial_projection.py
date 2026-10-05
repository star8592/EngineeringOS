from __future__ import annotations
import json,pathlib
from project_journal import events
from project_replay import replay_project
from project_registry import effective_autopilot

FINAL_STATES={"RESOLVED","SUPERSEDED"}
def _text(item:dict)->str:
 return item.get("expected_outcome") or item.get("requirement") or item.get("goal") or item.get("kind") or "正在推进一项产品工作"
def build(registry_path,runtime_root)->dict:
 registry=json.loads(pathlib.Path(registry_path).read_text()) if pathlib.Path(registry_path).exists() else {"projects":[]}
 products=[]
 for cfg in registry.get("projects",[]):
  name=cfg.get("name")
  if not name:continue
  display_name=cfg.get("display_name") or name
  project_root=pathlib.Path(runtime_root)/"projects"/name
  jp=project_root/"journal.jsonl"
  bp=project_root/"baseline.json"
  pp=project_root/"promotion.json"
  baseline=json.loads(bp.read_text()) if bp.exists() else None
  promotion=json.loads(pp.read_text()) if pp.exists() else None
  evs=events(jp) if jp.exists() else []
  state=replay_project(evs) if evs else {"work_items":{}}
  items=list(state.get("work_items",{}).values())
  last_by_key={}
  for e in evs:
   if str(e.get("type","")).startswith("WORK_"):last_by_key[e.get("key")]=e
  active=[x for x in items if x.get("state") not in FINAL_STATES]
  active.sort(key=lambda x:last_by_key.get(x.get("id"),{}).get("seq",0),reverse=True)
  needs=[x for x in active if x.get("needs_intent") or x.get("state")=="NEEDS_INTENT"]
  resolved=[e for e in evs if e.get("type")=="WORK_RESOLVED"]
  resolved.sort(key=lambda e:e.get("seq",0),reverse=True)
  by_id={x.get("id"):x for x in items}
  recent=[]
  for e in resolved[:5]:
   item=by_id.get(e.get("key"),{})
   recent.append({"text":_text(item),"completed_at":e.get("observed_at")})
  decisions=[]
  for x in needs[:3]:
   decisions.append({"question":x.get("question") or x.get("intent_question") or "有一个产品方向需要你确认。"})
  baseline_state=baseline.get("state") if baseline else None
  effective=effective_autopilot(cfg,promotion)
  promotion_blocked=cfg.get("management_target")=="A2_MANAGED" and promotion and promotion.get("state")=="BLOCKED"
  if needs: status="NEEDS_INTENT"
  elif baseline_state=="PROTECTED_EXISTING_WORK": status="PROTECTED"
  elif promotion_blocked: status="MANAGEMENT_BLOCKED"
  elif active and effective: status="WORKING"
  elif active: status="QUEUED"
  elif effective: status="HEALTHY"
  elif baseline_state=="CLEAN_CONNECTED": status="BASELINED"
  else: status="CONNECTED"
  products.append({
   "id":name,"name":display_name,"connected":True,"autopilot_enabled":effective,
   "status":status,
   "management_note":("检测到现有未提交工作，AI开发经理会保护它们，不会覆盖或自动提交。" if status=="PROTECTED" else ("自动管理条件尚未满足，系统不会越过安全门。" if status=="MANAGEMENT_BLOCKED" else ("已有需求进入队列，但自动管理尚未生效。" if status=="QUEUED" else ("安全基线已建立，当前没有自动管理授权。" if status=="BASELINED" else None)))),
   "active_work":[{"text":_text(x)} for x in active[:5]],
   "recent_completed":recent,
   "decisions":decisions
  })
 return {"schema_version":1,"products":products}
