import sys,json,subprocess,tempfile,pathlib
sys.path.insert(0,'src/engineeringos')
from command_processor import *
from event_store import read_events

def rust(events,cid):
 raw=json.dumps({'command_id':cid,'events':events},separators=(',',':'))
 return json.loads(subprocess.check_output(['cargo','run','--quiet','--manifest-path','rust/eos-core/Cargo.toml','--bin','command_parity'],input=raw,text=True))
def py(events,cid):
 s=replay_command(events,cid);return {'state':s,'retry_decision':retry_decision(s)}
with tempfile.TemporaryDirectory() as d:
 p=pathlib.Path(d)/'c.jsonl';c=Command('c1','k1','DEPLOY',True,'ALLOW')
 record_intent(p,c,0)
 stages=[read_events(p)]
 append_command_event(p,c,'COMMAND_DISPATCHED');stages.append(read_events(p))
 append_command_event(p,c,'COMMAND_COMPLETION_UNKNOWN');stages.append(read_events(p))
 append_command_event(p,c,'COMMAND_EFFECT_NOT_APPLIED',{'evidence_refs':['probe:none']});stages.append(read_events(p))
 append_command_event(p,c,'COMMAND_DISPATCHED');append_command_event(p,c,'COMMAND_EFFECT_CONFIRMED',{'evidence_refs':['runtime:r1']});stages.append(read_events(p))
 for es in stages:
  a,b=py(es,'c1'),rust(es,'c1');assert a==b,(a,b)
 assert [py(es,'c1')['retry_decision'] for es in stages]==['RETRY_ALLOWED','PROBE_REQUIRED','PROBE_REQUIRED','RETRY_ALLOWED','DO_NOT_RETRY']
print('10 command Python↔Rust parity assertions passed')
