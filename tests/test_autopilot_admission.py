import sys
sys.path.insert(0,'src/engineeringos')
from autopilot_admission import *
item={"id":"w1","project":"EngineeringOS","state":"DISCOVERED","required_assurance":"A2"}
dispatch={"id":"w1","schedule_state":"DISPATCHABLE"}
assert admit(item,dispatch,action_kind="RUN_VERIFICATION")["decision"]=="ALLOW"
assert admit(item,dispatch,action_kind="WRITE_CODE")["decision"]=="DENY"
assert admit({**item,"state":"PROTECT"},dispatch,action_kind="RUN_VERIFICATION")["decision"]=="DENY"
assert admit({**item,"required_assurance":"A3"},dispatch,action_kind="RUN_VERIFICATION")["decision"]=="DENY"
assert admit(item,{"id":"w1","schedule_state":"BLOCKED"},action_kind="RUN_VERIFICATION")["decision"]=="DENY"
c1=make_command(item,action_kind="RUN_VERIFICATION",subject_sha="abc")
c2=make_command(item,action_kind="RUN_VERIFICATION",subject_sha="abc")
assert c1==c2 and not c1.side_effecting
print("7 autopilot-admission invariants passed")
