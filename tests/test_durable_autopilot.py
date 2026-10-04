import sys,tempfile,pathlib
sys.path.insert(0,'src/engineeringos')
from conversation_intent import new_turn
from durable_autopilot import run_durable_tick,load_projection
with tempfile.TemporaryDirectory() as td:
 p=pathlib.Path(td)/"state.json"
 a=new_turn("c","DESIRE","keep conversation state durable",intent_id="durable")
 r=run_durable_tick(project="EngineeringOS",turns=[a],intent_id="durable",required_capabilities=["durable conversation"],capabilities=[],work_items=[],state_path=p)
 assert p.exists()
 q=load_projection(p)
 assert q["status"]=="WORKING" and q["turn_ids"]==[a.id]
 assert q["work_items"] and q["dispatch"][0]["schedule_state"]=="DISPATCHABLE"
 assert ".engineeringos/runtime" not in str(p)
print("4 durable-autopilot invariants passed")
