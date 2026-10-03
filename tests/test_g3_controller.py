import sys;sys.path.insert(0,'src/engineeringos')
from g3_controller import decide
item={'kind':'RESOLVE_MAIN_QUALIFICATION'}
assert decide(item,{'current_head_evidence':{'ci':'IN_PROGRESS'}})=={'decision':'DEFER','reason':'AUTHORITATIVE_CI_IN_PROGRESS'}
assert decide(item,{'current_head_evidence':{'ci':'SUCCESS'}})['reason']=='AUTHORITATIVE_CI_ALREADY_PASS'
assert decide(item,{'current_head_evidence':{'ci':'FAILURE'}})['decision']=='ALLOW'
assert decide(item,{'current_head_evidence':{'ci':'UNKNOWN'}})['decision']=='ALLOW'
assert decide({'kind':'TRIAGE_DIRTY_WORKSPACES'},{})['decision']=='NO_ACTION'
print('5 G3-controller invariants passed')
