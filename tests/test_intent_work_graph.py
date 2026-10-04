import sys
sys.path.insert(0,'src/engineeringos')
from intent_work_graph import gap_work_items,user_interruptions
r={"intents":[
 {"intent":{"id":"a","statement":"Users can pay"},"state":"UNKNOWN","requirements":[{"requirement":"payments","state":"UNKNOWN"}]},
 {"intent":{"id":"b","statement":""},"state":"NEEDS_INTENT","requirements":[]},
 {"intent":{"id":"c","statement":"Students practice"},"state":"VERIFIED","requirements":[{"requirement":"student","state":"VERIFIED"}]},
 {"intent":{"id":"d","statement":"Checks exist"},"state":"DISCOVERED","requirements":[{"requirement":"checks","state":"DISCOVERED"}]}
]}
w=gap_work_items(r,"demo")
assert len(w)==2 and w[0]["requirement"]=="payments"
assert w[1]["kind"]=="VERIFICATION_GAP" and w[1]["requirement"]=="checks"
assert w[0]["completion_predicate"]["accepted_states"]==["VERIFIED"]
assert w[0]["id"]==gap_work_items(r,"demo")[0]["id"]
u=user_interruptions(r);assert len(u)==1 and u[0]["intent_id"]=="b"
assert all(x["intent_id"]!="b" for x in w)
print('8 intent-work-graph invariants passed')
