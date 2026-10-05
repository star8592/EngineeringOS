from __future__ import annotations
import json,pathlib
from project_journal import events
from project_replay import replay_project

FINAL_STATES={"RESOLVED","SUPERSEDED"}
def _text(item:dict)->str:
 return item.get("expected_outcome") or item.get("requirement") or item.get("goal") or item.get("kind") or "正在推进一项产品工作"
def build(registry_path,runtime_root)->dict:
 registry=json.loads(pathlib.Path(registry_path).read_text()) if pathlib.Path(registry_path).exists() else {"projects":[]}
 products=[]
 for cfg in registry.get("projects",[]):
  name=cfg.get("name")
  if not name:continue
  jp=pathlib.Path(runtime_root)/"projects"/name/"journal.jsonl"
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
  status="NEEDS_INTENT" if needs else ("WORKING" if active else "HEALTHY")
  products.append({
   "id":name,"name":name,"connected":True,"autopilot_enabled":bool(cfg.get("autopilot_enabled")),
   "status":status,
   "active_work":[{"text":_text(x)} for x in active[:5]],
   "recent_completed":recent,
   "decisions":decisions
  })
 return {"schema_version":1,"products":products}
