import sys
sys.path.insert(0,'src/engineeringos')
from self_hosting_execution import execute_verified_check
base={"id":"gap-1","project":"EngineeringOS","state":"DISCOVERED","completion_predicate":{"type":"CAPABILITY_EVIDENCE","requirement":"conversation ledger","accepted_states":["VERIFIED"]}}
a=dict(base);r=execute_verified_check(a,owner="self-agent",verifier="deterministic-test",check_name="conversation-intent",check_passed=True,evidence_ref="test:conversation-intent:pass")
assert r["item"]["state"]=="RESOLVED" and r["capability_state"]=="VERIFIED"
assert r["receipt"].state=="SUCCEEDED" and r["receipt"].evidence_refs
b=dict(base);r=execute_verified_check(b,owner="self-agent",verifier="deterministic-test",check_name="conversation-intent",check_passed=True,evidence_ref=None)
assert r["item"]["state"]=="REOPENED" and r["receipt"].state=="RUNNING"
c=dict(base);r=execute_verified_check(c,owner="self-agent",verifier="deterministic-test",check_name="conversation-intent",check_passed=False,evidence_ref="test:failed")
assert r["item"]["state"]=="REOPENED" and r["receipt"].state=="FAILED"
print('7 self-hosting execution invariants passed')
