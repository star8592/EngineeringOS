import sys
sys.path.insert(0,'src/engineeringos')
from autopilot_router import route
p={"work_items":[{"id":"g1","project":"EngineeringOS","kind":"CAPABILITY_GAP","state":"DISCOVERED","required_assurance":"A2"}],
   "dispatch":[{"id":"g1","schedule_state":"DISPATCHABLE"}]}
r=route(p,action_by_kind={"CAPABILITY_GAP":"RUN_VERIFICATION"},subject_sha="abc")
assert r["summary"]=={"allowed":1,"denied":0}
assert r["rows"][0]["command"]["side_effecting"] is False
assert r["rows"][0]["command"]["policy_decision"]=="ALLOW"
assert route(p,action_by_kind={})["summary"]["denied"]==1
print("4 autopilot-router invariants passed")
