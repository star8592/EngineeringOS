#!/usr/bin/env python3
import json, pathlib, subprocess
ROOT=pathlib.Path('artifacts')
def ensure(file,cmd):
 p=ROOT/file
 if not p.exists(): subprocess.check_call(cmd)
 return json.load(open(p))
# Refresh all read-only evidence before deciding.
subprocess.check_call(['python3','src/engineeringos/devcontrol_inventory.py'],stdout=subprocess.DEVNULL)
subprocess.check_call(['python3','src/engineeringos/devcontrol_lineage.py'],stdout=subprocess.DEVNULL)
subprocess.check_call(['python3','src/engineeringos/convergence_debt.py'],stdout=subprocess.DEVNULL)
subprocess.check_call(['python3','src/engineeringos/devcontrol_release_evidence.py'],stdout=subprocess.DEVNULL)
subprocess.check_call(['python3','src/engineeringos/evidence_plane.py'],stdout=subprocess.DEVNULL)
subprocess.check_call(['python3','src/engineeringos/reconcile_devcontrol.py'],stdout=subprocess.DEVNULL)
subprocess.check_call(['python3','src/engineeringos/policy_devcontrol.py'],stdout=subprocess.DEVNULL)
debt=json.load(open(ROOT/'convergence-debt.json')); ev=json.load(open(ROOT/'evidence-plane.json')); rec=json.load(open(ROOT/'devcontrol-reconciliation.json')); pol=json.load(open(ROOT/'policy-devcontrol.json'))
D=debt['dimensions']; I=ev['interpretation']; qualification=I['qualification']; liveprod=I['live_production_qualification']
actions=[]
def add(priority,kind,reason,assurance='A1',automation='REVIEW'):
 actions.append({'priority':priority,'kind':kind,'reason':reason,'required_assurance':assurance,'automation':automation})
if qualification=='FAIL': add(0,'RESTORE_MAIN_QUALIFICATION','current authoritative source head has failing CI','A2','BLOCK_UNTIL_RESOLVED')
elif qualification=='UNKNOWN': add(1,'RESOLVE_MAIN_QUALIFICATION','qualification evidence is unknown','A2')
if liveprod=='UNKNOWN': add(1,'RESOLVE_LIVE_PRODUCTION_QUALIFICATION','live production qualification/provenance is unresolved','A2')
if I['deployment_identity'] not in ('RESOLVED',): add(2,'CLOSE_DEPLOYMENT_IDENTITY_GAP',f"deployment identity is {I['deployment_identity']}",'A2')
if I['artifact_identity'] not in ('RESOLVED',): add(2,'CLOSE_ARTIFACT_IDENTITY_GAP',f"artifact identity is {I['artifact_identity']}",'A2')
if D['dirty_workspace']['count']: add(2,'TRIAGE_DIRTY_WORKSPACES',f"{D['dirty_workspace']['count']} branch-attached worktrees contain uncommitted state",'A1')
if D['overlap']['count']: add(2,'REVIEW_OVERLAPPING_LINES',f"{D['overlap']['count']} independent branch pairs have high changed-surface overlap",'A1')
if D['duplicate_state']['count']: add(3,'RECONCILE_DUPLICATE_STATE',f"{D['duplicate_state']['count']} exact-head alias groups need role/ownership reconciliation",'A1')
if D['divergence']['count']: add(3,'REVIEW_DIVERGENT_DEVELOPMENT',f"{D['divergence']['count']} development lines are materially behind origin/main",'A1')
if pol['decision']['state']=='REVIEW': add(1,'RESOLVE_SOURCE_PRODUCTION_DRIFT',pol['decision']['reason'],'A2')
# Manager never mutates target project in this phase.
actions.sort(key=lambda x:x['priority'])
out={'mode':'ADVISORY_READ_ONLY','project':'DevControl','summary':{'qualification':qualification,'live_production_qualification':liveprod,'source_head_production_verification':I['source_head_production_verification'],'deployment_identity':I['deployment_identity'],'artifact_identity':I['artifact_identity'],'source_production_policy':pol['decision']['state'],'convergence_debt':{k:v.get('count',v.get('status')) for k,v in D.items()}},'work_queue':actions,'execution_guardrail':'No merge/delete/deploy action is authorized by this manager prototype.'}
(ROOT/'manager-plan.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(out,indent=2,ensure_ascii=False))
