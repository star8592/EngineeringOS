import sys,tempfile,pathlib,json
sys.path.insert(0,'src/engineeringos')
from shadow_control_loop import run_loop
from event_store import read_events
with tempfile.TemporaryDirectory() as d:
 d=pathlib.Path(d);q=d/'q.json';dp=d/'d.json';s=d/'s.json';ev=d/'events.jsonl';ed=d/'evidence';proj=d/'projection.json'
 q.write_text(json.dumps({'items':[{'id':'w1','kind':'CHECK','state':'DISCOVERED'},{'id':'w2','kind':'BLOCKED','state':'DISCOVERED'}]}))
 dp.write_text(json.dumps({'items':[{'id':'w1','schedule_state':'DISPATCHABLE','lane':'DETERMINISTIC'},{'id':'w2','schedule_state':'BLOCKED','blocked_by':['x']}]}))
 s.write_text(json.dumps({'target':'DevControl','content_sha256':'abc123'}))
 x=run_loop(queue_path=q,dispatch_path=dp,snapshot_path=s,event_path=ev,evidence_dir=ed,projection_path=proj)
 assert x['target_mutation_authorized'] is False
 assert x['summary']=={'items':2,'succeeded':1,'blocked':1}
 a=next(i for i in x['items'] if i['item_id']=='w1');assert a['command_state']=='SUCCEEDED' and a['evidence_refs'] and a['attempts']==1
 b=next(i for i in x['items'] if i['item_id']=='w2');assert b['policy']=='DENY' and b['command_state'] is None
 assert len(read_events(ev))==3
 y=run_loop(queue_path=q,dispatch_path=dp,snapshot_path=s,event_path=ev,evidence_dir=ed,projection_path=proj)
 assert len(read_events(ev))==3 and y['summary']['succeeded']==1
print('7 shadow-control-loop invariants passed')
