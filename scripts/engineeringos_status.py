#!/usr/bin/env python3
import json,pathlib
root=pathlib.Path(__file__).resolve().parents[1]
state=root/'.engineeringos/runtime'
def load(rel):
 p=state/rel
 return json.loads(p.read_text()) if p.exists() else None
status=load('supervisor/status.json');brief=load('action-brief.json');history=load('time-series-summary.json')
print('EngineeringOS Supervisor:',(status or {}).get('health','NOT_RUNNING'))
if status:
 print('Last cycle:',status.get('completed_at') or status.get('failed_at'),'duration=',status.get('duration_seconds'),'s')
 print('Observations:',status.get('observations'),'active_work_items=',status.get('active_work_items'))
if history: print('Debt delta:',json.dumps(history.get('debt_delta',{}),ensure_ascii=False,sort_keys=True))
if brief:
 print('\nTop actions:')
 for i,a in enumerate(brief.get('actions',[]),1):
  print(f"{i}. P{a['priority']} {a['kind']} [{a['state']}/{a['schedule_state']}] — {a['reason']}")
g3=load('g3/controller.json')
if g3:
 print('\nG3 bounded decisions:')
 for x in g3.get('decisions',[]):
  if x.get('kind')=='RESOLVE_MAIN_QUALIFICATION' or x.get('decision')!='NO_ACTION':
   print(f"- {x.get('kind')}: {x.get('decision')} ({x.get('reason')})")
g3e=load('g3/projection.json')
if g3e:
 latest=g3e.get('latest') or {}
 print(f"Latest bounded execution: {latest.get('action')} check={g3e.get('check_result')} source={(latest.get('source_sha') or '')[:12]}")
