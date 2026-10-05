import sys
sys.path.insert(0,'src/engineeringos')
from backend_surface_admission import assess

fresh={'state':'CONVERGED'}
base={'state':'OBSERVED_MATCH','source_live_check':'PASS','host_observable_contract_check':'PASS','host_acceptance':'NOT_PROVEN_BY_SURFACE_OBSERVATION'}
assert assess(None,freshness=fresh)['reason']=='BACKEND_SURFACE_EVIDENCE_MISSING'
assert assess(base)['reason']=='BACKEND_SURFACE_FRESHNESS_REQUIRED'
a=assess(base,freshness=fresh);assert a['decision']=='ALLOW' and a['host_acceptance']=='NOT_PROVEN_BY_SURFACE_OBSERVATION'
assert assess({**base,'state':'TOOL_SURFACE_DRIFT'},freshness=fresh)['reason']=='TOOL_SURFACE_DRIFT'
assert assess({**base,'source_live_check':'FAIL'},freshness=fresh)['reason']=='SOURCE_LIVE_SURFACE_NOT_VERIFIED'
assert assess({**base,'host_observable_contract_check':'FAIL'},freshness=fresh)['reason']=='HOST_OBSERVABLE_SURFACE_NOT_VERIFIED'
assert assess(base,freshness={'state':'HOST_OBSERVATION_STALE'})['reason']=='HOST_OBSERVATION_STALE'
assert assess(base,freshness=fresh,require_host_acceptance=True)['reason']=='HOST_ACCEPTANCE_REQUIRED'
b=assess({**base,'host_acceptance':'ACCEPTED'},freshness=fresh,require_host_acceptance=True);assert b['decision']=='ALLOW'
print('9 backend-surface-admission invariants passed')
