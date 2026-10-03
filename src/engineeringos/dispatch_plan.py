#!/usr/bin/env python3
import json,pathlib
from scheduler import schedule
from state_paths import runtime
Q=runtime('work-queue.json'); OUT=pathlib.Path('artifacts/dispatch-plan.json')
q=json.load(open(Q)); sched=schedule(q['items']); by={x['id']:x for x in q['items']}
plan=[]
for s in sched:
    x=by[s['id']]
    row={**s,'kind':x['kind'],'priority':x['priority'],'reason':x['reason'],'automation':x['automation']}
    if s['schedule_state']=='DISPATCHABLE':
        row['execution_authorized']=False
        row['next_step']='produce lane-specific review/evidence; no target mutation'
    plan.append(row)
out={'mode':'SHADOW','project':'DevControl','items':sorted(plan,key=lambda x:(x['priority'],x['kind'])),'guardrail':'Dispatch is advisory. No target-project mutation is authorized.'}
OUT.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(out,indent=2,ensure_ascii=False))
