import sys
sys.path.insert(0,'src/engineeringos')
from autopilot_supervision import *
base={"status":"WORKING","intent_state":{"generation":1},"work_items":[],"dispatch":[],"human_interruptions":[]}
a=supervisor_decision(base);assert a["action"]=="OBSERVE"
b=supervisor_decision(base,a["fingerprint"]);assert b["action"]=="SLEEP"
p={**base,"dispatch":[{"id":"w1","schedule_state":"DISPATCHABLE"}]}
assert supervisor_decision(p)["action"]=="ADVANCE"
h={**base,"human_interruptions":[{"intent_id":"x"}]}
x=supervisor_decision(h);assert x["action"]=="WAIT_FOR_INTENT" and x["should_notify"]
assert not supervisor_decision(h,x["fingerprint"])["should_notify"]
assert bounded_history(list(range(500)),200)==list(range(300,500))
print("6 autopilot-supervision invariants passed")
