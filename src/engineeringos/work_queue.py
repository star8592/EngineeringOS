#!/usr/bin/env python3
import json,pathlib,hashlib,datetime
from state_paths import runtime
ART=pathlib.Path('artifacts'); path=runtime('work-queue.json'); path.parent.mkdir(parents=True,exist_ok=True)
plan=json.load(open(ART/'manager-plan.json'))
old=json.load(open(path)) if path.exists() else {'items':[]}; by={x['id']:x for x in old['items']}
now=datetime.datetime.now(datetime.timezone.utc).isoformat(); seen=set()
for p in plan['work_queue']:
    wid=hashlib.sha256(f"{plan['project']}|{p['kind']}".encode()).hexdigest()[:16]; seen.add(wid)
    if wid in by:
        x=by[wid]; x.update({'priority':p['priority'],'reason':p['reason'],'required_assurance':p['required_assurance'],'automation':p['automation'],'last_seen_at':now})
        if x['state']=='RESOLVED': x['state']='REOPENED'; x['reopened_at']=now
    else:
        by[wid]={'id':wid,'project':plan['project'],**p,'state':'DISCOVERED','first_seen_at':now,'last_seen_at':now,'evidence_refs':[]}
for wid,x in by.items():
    if wid not in seen and x['state'] not in ('RESOLVED','SUPERSEDED'):
        x['state']='PENDING_RESOLUTION'; x['last_missing_at']=now
state={'schema_version':1,'updated_at':now,'items':sorted(by.values(),key=lambda x:(x['priority'],x['kind']))}
path.write_text(json.dumps(state,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'items':len(state['items']),'states':{s:sum(x['state']==s for x in state['items']) for s in sorted(set(x['state'] for x in state['items']))}},indent=2))
for x in state['items']: print(x['priority'],x['state'],x['kind'],x['id'])
