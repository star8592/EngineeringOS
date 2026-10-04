from __future__ import annotations
from intent_work_graph import gap_work_items,user_interruptions
from scheduler import schedule
from dependency_graph import validate

def plan_from_reconciliation(reconciliation:dict,project:str)->dict:
 items=gap_work_items(reconciliation,project)
 errors=validate(items)
 if errors:
  return {"project":project,"admitted":False,"errors":errors,"work_items":items,"dispatch":[],"human_interruptions":user_interruptions(reconciliation)}
 dispatch=schedule(items)
 return {"schema_version":1,"project":project,"admitted":True,"errors":[],"work_items":items,"dispatch":dispatch,
         "human_interruptions":user_interruptions(reconciliation),
         "summary":{"work_items":len(items),"dispatchable":sum(x["schedule_state"]=="DISPATCHABLE" for x in dispatch),
                    "human_interruptions":len(user_interruptions(reconciliation))}}
