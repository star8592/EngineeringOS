#!/usr/bin/env python3
import argparse,json,pathlib,hashlib
from git_adapter import inventory
from scheduler import schedule
ap=argparse.ArgumentParser();ap.add_argument('--project',required=True);ap.add_argument('--repo',required=True);a=ap.parse_args()
i=inventory(a.repo,a.project); items=[]
def add(kind,priority,reason,assurance='A1'):
 wid=hashlib.sha256(f'{a.project}|{kind}'.encode()).hexdigest()[:16];items.append({'id':wid,'project':a.project,'kind':kind,'priority':priority,'reason':reason,'required_assurance':assurance,'automation':'REVIEW','state':'DISCOVERED','depends_on':[]})
if i['dirty']:add('TRIAGE_DIRTY_WORKSPACE',2,'current workspace contains uncommitted state')
if i['origin_main'] and i['head']!=i['origin_main']:add('RECONCILE_HEAD_WITH_ORIGIN_MAIN',3,'current workspace HEAD differs from origin/main')
q={'schema_version':1,'project':a.project,'items':items}; s=schedule(items)
out={'mode':'SHADOW','inventory':i,'queue':q,'dispatch':s,'execution_authorized':False}
p=pathlib.Path('artifacts')/f'{a.project.lower()}-g1-shadow.json';p.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n');print(json.dumps({'project':a.project,'facts':len(i['facts']),'queue_items':len(items),'dispatchable':sum(x['schedule_state']=='DISPATCHABLE' for x in s),'dirty':i['dirty'],'branch_count':len(i['branches'])},indent=2))
