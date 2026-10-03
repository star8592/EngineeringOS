import sys,tempfile,pathlib,subprocess,json
sys.path.insert(0,'src/engineeringos')
from command_processor import *
from event_store import read_events,current_version,EventStoreError

def c(i='c1',key='k1',side=True,policy='ALLOW'): return Command(i,key,'DEPLOY',side,policy)
with tempfile.TemporaryDirectory() as d:
 p=pathlib.Path(d)/'commands.jsonl';cmd=c()
 record_intent(p,cmd,0);s=replay_command(read_events(p),'c1');assert s['state']=='INTENT_RECORDED' and retry_decision(s)=='RETRY_ALLOWED'
 append_command_event(p,cmd,'COMMAND_DISPATCHED');s=replay_command(read_events(p),'c1');assert s['attempts']==1 and retry_decision(s)=='PROBE_REQUIRED'
 append_command_event(p,cmd,'COMMAND_COMPLETION_UNKNOWN');s=replay_command(read_events(p),'c1');assert s['state']=='UNKNOWN_COMPLETION' and retry_decision(s)=='PROBE_REQUIRED'
 append_command_event(p,cmd,'COMMAND_EFFECT_NOT_APPLIED',{'evidence_refs':['probe:not-found']});s=replay_command(read_events(p),'c1');assert retry_decision(s)=='RETRY_ALLOWED'
 append_command_event(p,cmd,'COMMAND_DISPATCHED');append_command_event(p,cmd,'COMMAND_EFFECT_CONFIRMED',{'evidence_refs':['runtime:release-abc']});s=replay_command(read_events(p),'c1');assert s['state']=='SUCCEEDED' and s['attempts']==2 and retry_decision(s)=='DO_NOT_RETRY'
 try: record_intent(p,c('c2','k1'),current_version(p));raise AssertionError('duplicate idempotency key accepted')
 except CommandError as e: assert str(e)=='IDEMPOTENCY_KEY_CONFLICT'
 q=pathlib.Path(d)/'policy.jsonl'
 try: record_intent(q,c(policy='DENY'),0);raise AssertionError('denied command recorded')
 except CommandError as e: assert str(e)=='POLICY_DENIED'
 # CAS: two commands based on version 0; exactly one intent may commit.
 r=pathlib.Path(d)/'race.jsonl'
 record_intent(r,c('a','ka'),0)
 try: record_intent(r,c('b','kb'),0);raise AssertionError('stale command committed')
 except EventStoreError as e: assert str(e)=='VERSION_CONFLICT'
 # success/outcome cannot be asserted without evidence.
 z=pathlib.Path(d)/'evidence.jsonl';cc=c('z','kz');record_intent(z,cc,0);append_command_event(z,cc,'COMMAND_DISPATCHED')
 try: append_command_event(z,cc,'COMMAND_EFFECT_CONFIRMED',{});raise AssertionError('success without evidence')
 except CommandError as e: assert str(e)=='OUTCOME_EVIDENCE_REQUIRED'
print('10 command-processor invariants passed')
