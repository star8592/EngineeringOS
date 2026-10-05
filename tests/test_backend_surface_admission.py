import sys
sys.path.insert(0,'src/engineeringos')
from backend_surface_admission import assess

assert assess(None)['reason']=='BACKEND_SURFACE_EVIDENCE_MISSING'
base={'state':'OBSERVED_MATCH','source_live_check':'PASS','host_observable_contract_check':'PASS','host_acceptance':'NOT_PROVEN_BY_SURFACE_OBSERVATION'}
a=assess(base);assert a['decision']=='ALLOW' and a['host_acceptance']=='NOT_PROVEN_BY_SURFACE_OBSERVATION'
assert assess({**base,'state':'TOOL_SURFACE_DRIFT'})['reason']=='TOOL_SURFACE_DRIFT'
assert assess({**base,'source_live_check':'FAIL'})['reason']=='SOURCE_LIVE_SURFACE_NOT_VERIFIED'
assert assess({**base,'host_observable_contract_check':'FAIL'})['reason']=='HOST_OBSERVABLE_SURFACE_NOT_VERIFIED'
assert assess(base,require_host_acceptance=True)['reason']=='HOST_ACCEPTANCE_REQUIRED'
b=assess({**base,'host_acceptance':'ACCEPTED'},require_host_acceptance=True);assert b['decision']=='ALLOW'
print('7 backend-surface-admission invariants passed')
