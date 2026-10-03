#!/usr/bin/env python3
import json, pathlib, subprocess
from policy import source_production_drift
p=pathlib.Path('artifacts/devcontrol-reconciliation.json')
if not p.exists(): subprocess.check_call(['python3','src/engineeringos/reconcile_devcontrol.py'])
r=json.load(open(p)); by={x['predicate']:x for x in r['reconciliation']}
d=by['source_vs_production_version']; runtime=by['runtime_endpoint_consistency']; prov=by['production_release_to_source']
decision=source_production_drift(d['source'],d['production'],prov['state']=='RESOLVED',runtime['state']=='RESOLVED')
out={'decision':decision.to_dict(),'input_states':{k:v['state'] for k,v in by.items()}}
pathlib.Path('artifacts/policy-devcontrol.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
