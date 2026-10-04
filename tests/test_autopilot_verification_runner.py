import sys,tempfile,pathlib
sys.path.insert(0,'src/engineeringos')
from autopilot_verification_runner import run_verification
item={"id":"verify-1","project":"EngineeringOS","kind":"CAPABILITY_GAP","state":"DISCOVERED","required_assurance":"A2",
"completion_predicate":{"type":"CAPABILITY_EVIDENCE","requirement":"verification runner","accepted_states":["VERIFIED"]}}
d={"id":"verify-1","schedule_state":"DISPATCHABLE"}
with tempfile.TemporaryDirectory() as td:
 r=run_verification(item,d,argv=[sys.executable,"-c","print('PASS')"],cwd=td,subject_sha="abc")
 assert r["executed"] and r["exit_code"]==0
 assert r["closure"]["item"]["state"]=="RESOLVED"
 assert r["closure"]["capability_state"]=="VERIFIED"
bad={"id":"x","project":"EngineeringOS","state":"PROTECT","required_assurance":"A2"}
assert not run_verification(bad,{"id":"x","schedule_state":"DISPATCHABLE"},argv=["true"],cwd=".")["executed"]
print("4 autopilot-verification-runner invariants passed")
