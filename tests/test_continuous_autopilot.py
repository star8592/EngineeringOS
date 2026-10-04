import sys
sys.path.insert(0,'src/engineeringos')
from continuous_autopilot import *
base={"intents":{"i":{"active":True}},"work_items":{"w":{"id":"w","state":"DISCOVERED"}}}
a=classify(base);assert a["action"]=="ADVANCE"
b=after_execution(a,{"execution":{"results":[{"state":"REOPENED"}]}});c=classify(base,b);assert c["action"]=="BACKOFF" and c["delay_seconds"]==30 and not c["should_notify"]
c["last_result"]="MACHINE_FAILURE";d=classify(base,c);assert d["delay_seconds"]==60
done={"intents":{"i":{"active":True}},"work_items":{"w":{"id":"w","state":"RESOLVED"}}};o=classify(done);s=classify(done,o);assert s["action"]=="SLEEP" and s["delay_seconds"]==300
need={"intents":{},"work_items":{"w":{"id":"w","state":"NEEDS_INTENT","needs_intent":True}}};n=classify(need);assert n["action"]=="WAIT_FOR_INTENT" and n["should_notify"];n2=classify(need,n);assert not n2["should_notify"]
assert next_delay(10)==1800
print("10 continuous-autopilot invariants passed")
