import sys,tempfile,pathlib
sys.path.insert(0,'src/engineeringos')
from event_store import *
from event_replay import replay,replay_from
with tempfile.TemporaryDirectory() as d:
 p=pathlib.Path(d)/'events.jsonl'; s=pathlib.Path(d)/'snapshot.json'
 e1={'seq':1,'event_id':'e1','type':'WORK_DISCOVERED','payload':{'id':'w1'}}
 e2={'seq':2,'event_id':'e2','type':'LEASE_CLAIMED','payload':{'owner':'a','acquired_at':'t0','expires_at':'t1'}}
 append_event_cas(p,e1,0); append_event_cas(p,e2,1)
 base=replay(read_events(p)); write_snapshot(s,2,base); snap=read_snapshot(s); assert snap['last_seq']==2 and snap['state']==base
 e3={'seq':3,'event_id':'e3','type':'LEASE_RENEWED','payload':{'owner':'a','expires_at':'t2'}}; append_event_cas(p,e3,2)
 recovered=replay_from(snap['state'],snap['last_seq'],[x for x in read_events(p) if x['seq']>snap['last_seq']]); assert recovered==replay(read_events(p))
 # stale concurrent writer must lose rather than overwrite.
 e4={'seq':4,'event_id':'e4','type':'WORK_REOPENED','payload':{}}
 append_event_cas(p,e4,3)
 try: append_event_cas(p,dict(e4,event_id='e5'),3); raise AssertionError('stale writer committed')
 except EventStoreError as e: assert str(e)=='VERSION_CONFLICT'
 # snapshot corruption is detectable.
 import json
 body=json.loads(s.read_text()); body['state']['state']='BROKEN'; s.write_text(json.dumps(body)+'\n')
 try: read_snapshot(s); raise AssertionError('bad snapshot accepted')
 except EventStoreError as e: assert str(e)=='SNAPSHOT_DIGEST_MISMATCH'
print('5 checkpoint/CAS invariants passed')
