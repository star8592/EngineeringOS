import sys;sys.path.insert(0,'src/engineeringos')
from execution_receipt import *
r=ExecutionReceipt('x1','deploy:abc','DEPLOY')
transition(r,'DISPATCHED');transition(r,'ACCEPTED');assert retry_decision(r)=='PROBE_REQUIRED'
transition(r,'LOST_CONTACT');assert retry_decision(r)=='PROBE_REQUIRED'
assert retry_decision(r,'PROVEN_NOT_APPLIED')=='RETRY_ALLOWED';assert retry_decision(r,'PROVEN_APPLIED')=='DO_NOT_RETRY'
try: transition(r,'SUCCEEDED');raise AssertionError('success without evidence allowed')
except ExecutionError as e: assert str(e)=='SUCCESS_EVIDENCE_REQUIRED'
assert r.state=='LOST_CONTACT'
# transition mutates before validating evidence: ensure this is treated as a bug guard below
r=ExecutionReceipt('x2','git:1','GIT_PUSH',side_effecting=True);transition(r,'DISPATCHED');transition(r,'ACCEPTED');transition(r,'SUCCEEDED',['git:commit:abc']);assert retry_decision(r)=='DO_NOT_RETRY'
q=ExecutionReceipt('x3','read:1','READ_ONLY',side_effecting=False);transition(q,'DISPATCHED');assert retry_decision(q)=='RETRY_ALLOWED'
print('8 execution-receipt invariants passed')
