#!/usr/bin/env python3
import json,pathlib,subprocess,datetime,hashlib
from state_paths import runtime
A=pathlib.Path('artifacts'); S=runtime('shadow'); S.mkdir(parents=True,exist_ok=True)
def run(cmd): subprocess.check_call(cmd,stdout=subprocess.DEVNULL)
for cmd in [
 ['python3','src/engineeringos/devcontrol_inventory.py'],
 ['python3','src/engineeringos/devcontrol_lineage.py'],
 ['python3','src/engineeringos/convergence_debt.py'],
 ['python3','src/engineeringos/devcontrol_release_evidence.py'],
 ['python3','src/engineeringos/evidence_plane.py'],
 ['python3','src/engineeringos/reconcile_devcontrol.py'],
 ['python3','src/engineeringos/policy_devcontrol.py'],
 ['python3','src/engineeringos/manager.py'],
 ['python3','src/engineeringos/work_queue.py'],
 ['python3','src/engineeringos/reconcile_queue_outcomes.py'],
 ['python3','src/engineeringos/dispatch_plan.py']]: run(cmd)
now=datetime.datetime.now(datetime.timezone.utc); rid=now.strftime('%Y%m%dT%H%M%SZ')
plan=json.load(open(A/'manager-plan.json')); dispatch=json.load(open(A/'dispatch-plan.json')); debt=json.load(open(A/'convergence-debt.json')); ev=json.load(open(A/'evidence-plane.json')); rec=json.load(open(A/'devcontrol-reconciliation.json'))
snap={'schema_version':1,'run_id':rid,'observed_at':now.isoformat(),'mode':'SHADOW','target':'DevControl','source_head':rec['facts'][0]['value'],'manager_summary':plan['summary'],'work_queue_count':len(plan['work_queue']),'dispatchable_count':sum(x.get('schedule_state')=='DISPATCHABLE' for x in dispatch['items']),'execution_authorized':False,'evidence_interpretation':ev['interpretation'],'reconciliation':rec['reconciliation'],'debt_counts':{k:v.get('count',v.get('status')) for k,v in debt['dimensions'].items()}}
stable={k:v for k,v in snap.items() if k not in ('run_id','observed_at')};snap['content_sha256']=hashlib.sha256(json.dumps(stable,sort_keys=True).encode()).hexdigest()
p=S/f'{rid}.json'; p.write_text(json.dumps(snap,indent=2,ensure_ascii=False)+'\n')
latest=S/'latest.json'; latest.write_text(json.dumps(snap,indent=2,ensure_ascii=False)+'\n')
run(['python3','src/engineeringos/shadow_control_loop.py'])
print(json.dumps(snap,indent=2,ensure_ascii=False))
