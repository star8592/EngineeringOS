import sys
sys.path.insert(0,'src/engineeringos')
from conversation_intent import new_turn
from intent_capability import Capability
from autopilot_control_loop import tick
a=new_turn("c","DESIRE","natural conversation drives development",intent_id="chat")
r=tick(project="EngineeringOS",turns=[a],intent_id="chat",required_capabilities=["conversation shell"],capabilities=[],work_items=[])
assert r["status"]=="WORKING" and len(r["plan"]["work_items"])==1
b=new_turn("c","CORRECTION","voice should be the easiest path",intent_id="chat",artifact_ref="preview:chat:1",supersedes=a.id)
old=r["plan"]["work_items"];old[0]["intent_generation"]=1
r2=tick(project="EngineeringOS",turns=[a,b],intent_id="chat",required_capabilities=["conversation shell"],capabilities=[],work_items=old)
assert r2["revision"]["reconciliation"]["superseded"]==[old[0]["id"]]
assert r2["plan"]["work_items"][0]["intent_generation"]==2
assert r2["plan"]["work_items"][0]["feedback_artifact_ref"]=="preview:chat:1"
d=[Capability("conversation shell","conversation shell",("route:/chat",),1.0,"DISCOVERED")]
rd=tick(project="EngineeringOS",turns=[a],intent_id="chat",required_capabilities=["conversation shell"],capabilities=d,work_items=[])
assert rd["status"]=="WORKING" and rd["plan"]["work_items"][0]["kind"]=="VERIFICATION_GAP"
v=[Capability("conversation shell","conversation shell",("test:pass",),1.0,"VERIFIED")]
r3=tick(project="EngineeringOS",turns=[a],intent_id="chat",required_capabilities=["conversation shell"],capabilities=v,work_items=[])
assert r3["status"]=="VERIFIED" and not r3["plan"]["work_items"]
print("9 autopilot-control-loop invariants passed")
