#!/usr/bin/env python3
import json,pathlib
root=pathlib.Path(__file__).resolve().parents[1]
state=root/'.engineeringos/runtime'
def load(rel):
 p=state/rel
 return json.loads(p.read_text()) if p.exists() else None
status=load('supervisor/status.json')
brief=load('action-brief.json')
history=load('time-series-summary.json')
print('EngineeringOS Supervisor:', (status or {}).get('health','NOT_RUNNING'))
if status:
 print('Last cycle:', status.get('completed_at') or status.get('failed_at'), 'duration=',status.get('duration_seconds'),'s')
 print('Observations:',status.get('observations'),'active_work_items=',status.get('active_work_items'))
if history:
 print('Debt delta:',json.dumps(history.get('debt_delta',{}),ensure_ascii=False,sort_keys=True))
if brief:
 print('\nTop actions:')
 for i,a in enumerate(brief.get('actions',[]),1):
  print(f"{i}. P{a['priority']} {a['kind']} [{a['state']}/{a['schedule_state']}] — {a['reason']}")
