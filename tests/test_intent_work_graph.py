import sys
sys.path.insert(0,'src/engineeringos')
from intent_work_graph import gap_work_items,user_interruptions
r={"intents":[
 {"intent":{"id":"a","statement":"Users can pay"},"state":"UNKNOWN","requirements":[{"requirement":"payments","state":"UNKNOWN"}]},
 {"intent":{"id":"b","statement":""},"state":"NEEDS_INTENT","requirements":[]},
 {"intent":{"id":"c","statement":"Students practice"},"state":"VERIFIED","requirements":[{"requirement":"student","state":"VERIFIED"}]}
]}
w=gap_work_items(r,"demo")
assert len(w)==1 and w[0]["requirement"]=="payments"
assert w[0]["completion_predicate"]["accepted_states"]==["VERIFIED"]
assert w[0]["id"]==gap_work_items(r,"demo")[0]["id"]
u=user_interruptions(r);assert len(u)==1 and u[0]["intent_id"]=="b"
assert all(x["intent_id"]!="b" for x in w)
print('6 intent-work-graph invariants passed')
