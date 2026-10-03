import sys,tempfile,pathlib,json
sys.path.insert(0,'src/engineeringos')
from event_store import *
from event_replay import replay
with tempfile.TemporaryDirectory() as d:
 p=pathlib.Path(d)/'events.jsonl'
 e1={'seq':1,'event_id':'e1','type':'WORK_DISCOVERED','payload':{'id':'w1'}}
 e2={'seq':2,'event_id':'e2','type':'LEASE_CLAIMED','payload':{'owner':'a','acquired_at':'t0','expires_at':'t1'}}
 append_event(p,e1);append_event(p,e2);assert read_events(p)==[e1,e2]
 try: append_event(p,dict(e2,event_id='e3'));raise AssertionError('bad seq accepted')
 except EventStoreError as e: assert str(e)=='SEQUENCE_MISMATCH'
 # simulate power loss during final append: complete prefix must remain recoverable.
 with open(p,'ab') as f:f.write(b'{"seq":3,"event_id":"e3"')
 assert read_events(p)==[e1,e2];assert replay(read_events(p))['state']=='IN_PROGRESS'
 # corruption of a complete record is not recoverable/ignorable.
 q=pathlib.Path(d)/'bad.jsonl';q.write_bytes(b'{bad}\n')
 try: read_events(q);raise AssertionError('corruption ignored')
 except EventStoreError as e: assert str(e)=='CORRUPT_COMPLETE_RECORD'
print('4 durable event-store invariants passed')
