from __future__ import annotations
from autopilot_admission import admit,make_command

def route(projection:dict, *, action_by_kind:dict[str,str], max_auto_assurance:str="A2", subject_sha:str|None=None)->dict:
 by_work={x["id"]:x for x in projection.get("work_items",[])}
 rows=[]
 for dispatch in projection.get("dispatch",[]):
  item=by_work.get(dispatch["id"])
  if not item: rows.append({"item_id":dispatch["id"],"decision":"DENY","reason":"WORK_ITEM_MISSING"});continue
  action=action_by_kind.get(item.get("kind",""))
  if not action: rows.append({"item_id":item["id"],"decision":"DENY","reason":"NO_ACTION_MAPPING"});continue
  decision=admit(item,dispatch,action_kind=action,max_auto_assurance=max_auto_assurance)
  row={"item_id":item["id"],"action_kind":action,**decision}
  if decision["decision"]=="ALLOW":
   cmd=make_command(item,action_kind=action,subject_sha=subject_sha)
   row["command"]={"command_id":cmd.command_id,"idempotency_key":cmd.idempotency_key,"action_kind":cmd.action_kind,"side_effecting":cmd.side_effecting,"policy_decision":cmd.policy_decision}
  rows.append(row)
 return {"schema_version":1,"mode":"SAFE_AUTOPILOT","rows":rows,
         "summary":{"allowed":sum(x["decision"]=="ALLOW" for x in rows),"denied":sum(x["decision"]!="ALLOW" for x in rows)}}
