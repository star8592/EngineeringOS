#!/usr/bin/env python3
import json, subprocess, pathlib, datetime
TARGET='/mnt/disk1/Code/DevControl2'; OUT=pathlib.Path('artifacts/evidence-plane.json')
def cmd(args):
 p=subprocess.run(args,text=True,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL); return p.stdout.strip(),p.returncode
def git(*a): return cmd(['git','-C',TARGET,*a])[0]
def gh(*a): return cmd(['gh',*a],)[0]
origin=git('rev-parse','origin/main'); version=git('show','origin/main:VERSION')
runs_raw=gh('run','list','--repo','star8592/DevControl2','--branch','main','--limit','50','--json','databaseId,headSha,workflowName,status,conclusion,createdAt,updatedAt,url')
runs=json.loads(runs_raw or '[]')
by_sha={}
for r in runs: by_sha.setdefault(r['headSha'],[]).append(r)
head_runs=by_sha.get(origin,[])
ci=[r for r in head_runs if r['workflowName']=='DevControl 3 CI']
smoke=[r for r in head_runs if r['workflowName']=='Production Smoke']
spec=[r for r in head_runs if r['workflowName']=='External Spec Drift']
def state(xs):
 if not xs: return 'UNKNOWN'
 latest=sorted(xs,key=lambda x:x['createdAt'],reverse=True)[0]
 return latest['conclusion'].upper() if latest['status']=='completed' else latest['status'].upper()
# Reachability of latest known successful production smoke SHA from current main is useful evidence, not proof current main is deployed.
success_smokes=[r for r in runs if r['workflowName']=='Production Smoke' and r['conclusion']=='success']
latest_smoke=sorted(success_smokes,key=lambda x:x['createdAt'],reverse=True)[0] if success_smokes else None
smoke_reachable=None
if latest_smoke:
 smoke_reachable=(subprocess.run(['git','-C',TARGET,'merge-base','--is-ancestor',latest_smoke['headSha'],'origin/main']).returncode==0)
report={'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'repository':'star8592/DevControl2','origin_main':origin,'version':version,'current_head_evidence':{'ci':state(ci),'production_smoke':state(smoke),'external_spec_drift':state(spec),'runs':head_runs},'latest_successful_production_smoke':latest_smoke,'latest_smoke_reachable_from_current_main':smoke_reachable,'release_api':{'status':'EMPTY' if not gh('release','list','--repo','star8592/DevControl2','--limit','5') else 'PRESENT'},'interpretation':{'qualification':'FAIL' if state(ci)=='FAILURE' else ('PASS' if state(ci)=='SUCCESS' else 'UNKNOWN'),'production_verification':'PASS' if state(smoke)=='SUCCESS' else 'UNKNOWN','deployment_identity':'UNKNOWN','artifact_identity':'UNKNOWN'},'guardrail':'A successful smoke on an older SHA does not prove current origin/main is deployed or production-verified.'}
OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(report['current_head_evidence'],indent=2))
print('interpretation',report['interpretation'])
print('latest successful smoke', latest_smoke['headSha'] if latest_smoke else None, 'reachable=',smoke_reachable)
