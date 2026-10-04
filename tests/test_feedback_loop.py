import sys
sys.path.insert(0,'src/engineeringos')
from conversation_intent import new_turn,reduce_intent
from feedback_loop import apply_feedback
a=new_turn("c","DESIRE","make a simple home page",intent_id="home")
b=new_turn("c","CORRECTION","move the main button below",intent_id="home",artifact_ref="preview:home:1",supersedes=a.id)
state=reduce_intent([a,b],"home")
old=[{"id":"w1","intent_id":"home","intent_generation":1,"state":"DISCOVERED"}]
r=apply_feedback(project="EngineeringOS",intent_state=state,feedback_text=b.text,artifact_ref=b.artifact_ref,work_items=old,requirement="home preview",evidence_ref="turn:"+b.id)
assert r["reconciliation"]["superseded"]==["w1"]
assert r["created"][0]["intent_generation"]==2
assert r["created"][0]["feedback_artifact_ref"]=="preview:home:1"
assert r["dispatch"][0]["schedule_state"]=="DISPATCHABLE"
assert r["user_message"]["status"]=="WORKING"
print('5 feedback-loop invariants passed')
