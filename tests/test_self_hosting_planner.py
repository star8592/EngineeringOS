import sys
sys.path.insert(0,'src/engineeringos')
from self_hosting_planner import plan_from_reconciliation
r={"intents":[
 {"intent":{"id":"voice","statement":"Voice conversation stays usable while work runs"},"state":"UNKNOWN","requirements":[{"requirement":"durable voice handoff","state":"UNKNOWN"}]},
 {"intent":{"id":"amb","statement":""},"state":"NEEDS_INTENT","requirements":[]}
]}
p=plan_from_reconciliation(r,"EngineeringOS")
assert p["admitted"]
assert p["summary"]=={"work_items":1,"dispatchable":1,"human_interruptions":1}
assert p["dispatch"][0]["lane"]=="REASONING_REVIEW"
assert p["work_items"][0]["completion_predicate"]["accepted_states"]==["VERIFIED"]
assert p["human_interruptions"][0]["intent_id"]=="amb"
assert all(x["intent_id"]!="amb" for x in p["work_items"])
print('6 self-hosting planner invariants passed')
