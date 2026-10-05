from __future__ import annotations
import json,pathlib,time
from durable_supervisor_runtime import recover,resume_once
from continuous_autopilot import classify,after_execution
from project_registry import load,management_requested
from project_promotion import assess as assess_promotion
from codex_readonly_provider import CodexReadOnlyProvider
from claude_readonly_provider import ClaudeReadonlyProvider
from codex_planning_provider import CodexPlanningProvider
from planning_phase import plan_one

def atomic(path,obj):
 p=pathlib.Path(path);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(".tmp");tmp.write_text(json.dumps(obj,sort_keys=True,ensure_ascii=False)+"\n");tmp.replace(p)
def run_registered_once(registry_path,runtime_root,*,provider_factory=None,planner_factory=None,now=None):
 def default_provider_factory(cfg):
  budgets=cfg.get("provider_timeouts",{})
  return [CodexReadOnlyProvider(**({"timeout":int(budgets["codex-cli-readonly"])} if "codex-cli-readonly" in budgets else {})),ClaudeReadonlyProvider(**({"timeout":int(budgets["claude-cli-readonly"])} if "claude-cli-readonly" in budgets else {}))]
 provider_factory=provider_factory or default_provider_factory
 planner_factory=planner_factory or (lambda cfg:[CodexPlanningProvider(timeout=int(cfg.get("planner_timeout",60)))])
 now=time.time() if now is None else now;out=[]
 for cfg in load(registry_path)["projects"]:
  if not management_requested(cfg):continue
  project_root=pathlib.Path(runtime_root)/"projects"/cfg["name"]
  if cfg.get("require_clean_baseline") or cfg.get("management_target")=="A2_MANAGED":
   bp=project_root/"baseline.json"
   baseline=json.loads(bp.read_text()) if bp.exists() else None
   if cfg.get("management_target")=="A2_MANAGED":
    promotion=assess_promotion(cfg,baseline)
    if not promotion.get("eligible"):
     out.append({"project":cfg["name"],"action":"PROMOTION_BLOCKED","reason":promotion.get("reason"),"should_notify":False})
     continue
   elif not baseline or baseline.get("state")!="CLEAN_CONNECTED":
    out.append({"project":cfg["name"],"action":"BASELINE_BLOCKED","reason":("BASELINE_MISSING" if not baseline else baseline.get("state","BASELINE_INVALID")),"should_notify":False})
    continue
  state=recover(runtime_root,cfg["name"]);dp=project_root/"continuous.json";prev=json.loads(dp.read_text()) if dp.exists() else {}
  if prev.get("next_eligible_at",0)>now:
   out.append({"project":cfg["name"],"action":"BACKOFF_WAIT","delay_seconds":round(prev["next_eligible_at"]-now)});continue
  retry_due=prev.get("last_result")=="MACHINE_FAILURE" and prev.get("next_eligible_at",0)<=now
  decision=classify(state,{**prev,"last_result":None} if retry_due else prev)
  if decision["action"]=="ADVANCE":
   planning=plan_one(cfg["repo"],runtime_root,cfg["name"],planner_factory(cfg))
   if planning["state"]=="CONTRACT_ADMITTED":
    decision["last_result"]="SUCCESS";decision["failures"]=0;out.append({"project":cfg["name"],"action":"PLAN","result":planning})
   elif planning["state"]=="PLANNER_FAILED":
    decision["last_result"]="MACHINE_FAILURE";out.append({"project":cfg["name"],"action":"PLAN_FAILED","result":planning})
   else:
    result=resume_once(cfg["repo"],runtime_root,cfg["name"],provider_factory(cfg),workspace_root=cfg["workspace_root"],verification_timeout=int(cfg.get("verification_timeout",120)))
    decision=after_execution(decision,result);out.append({"project":cfg["name"],"action":"ADVANCE","result":result["execution"]})
  else:out.append({"project":cfg["name"],"action":decision["action"],"reason":decision["reason"],"should_notify":decision.get("should_notify",False)})
  delay=decision.get("delay_seconds",0)
  if decision.get("last_result")=="MACHINE_FAILURE":
   failures=int(prev.get("failures",0))+1;decision["failures"]=failures
   from continuous_autopilot import next_delay
   delay=next_delay(failures)
  elif decision.get("last_result") in ("SUCCESS","RECONCILE"):
   decision["failures"]=0
  decision["next_eligible_at"]=now+delay;atomic(dp,decision)
 return out
