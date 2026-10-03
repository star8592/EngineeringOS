import sys;sys.path.insert(0,'src/engineeringos')
from production_evidence_semantics import interpret
r=interpret(source_ci='SUCCESS',source_head_smoke='UNKNOWN',release_evidence={'qualification_state':'RESOLVED','source_identity_state':'RESOLVED','deployment_identity_state':'PARTIAL','artifact_identity_state':'UNKNOWN'})
assert r['qualification']=='PASS'
assert r['source_head_production_verification']=='UNKNOWN'
assert r['live_production_qualification']=='PASS'
assert r['deployment_identity']=='PARTIAL'
assert r['artifact_identity']=='UNKNOWN'
r=interpret(source_ci='FAILURE',source_head_smoke='SUCCESS',release_evidence={});assert r['qualification']=='FAIL' and r['live_production_qualification']=='UNKNOWN'
print('6 production-evidence semantic invariants passed')
