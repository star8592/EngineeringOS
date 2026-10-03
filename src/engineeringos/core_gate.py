#!/usr/bin/env python3
import subprocess,json,pathlib
checks=[]
def run(name,cmd):
 p=subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT); checks.append({'name':name,'pass':p.returncode==0,'output':p.stdout.strip()[-1000:]}); return p.returncode==0
ok=True
for name,file in [('facts','tests/test_facts.py'),('policy','tests/test_policy.py'),('work_queue','tests/test_work_queue.py'),('leases_closure','tests/test_queue_model.py'),('dependencies','tests/test_dependency_graph.py'),('scheduler','tests/test_scheduler.py')]: ok=run(name,['python3',file]) and ok
required=['src/engineeringos/facts.py','src/engineeringos/policy.py','src/engineeringos/manager.py','src/engineeringos/work_queue.py','src/engineeringos/dependency_graph.py','src/engineeringos/queue_model.py','src/engineeringos/scheduler.py']
missing=[x for x in required if not pathlib.Path(x).exists()]
if missing: ok=False
out={'gate':'G0_CORE_COHERENCE','pass':ok,'checks':checks,'missing':missing}
pathlib.Path('artifacts/g0-core-gate.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2)); raise SystemExit(0 if ok else 1)
