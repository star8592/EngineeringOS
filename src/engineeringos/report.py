#!/usr/bin/env python3
import json, pathlib
p=pathlib.Path('artifacts/convergence-debt.json')
if not p.exists(): raise SystemExit('run convergence_debt.py first')
r=json.load(open(p))
print('EngineeringOS — DevControl Convergence Debt')
for k,v in r['dimensions'].items():
    if 'count' in v: print(f'{k:20} {v["count"]}')
    else: print(f'{k:20} {v["status"]}')
print('workspace_roles      '+', '.join(f'{k}={v}' for k,v in r['workspace_roles'].items()))
print(r['guardrail'])
