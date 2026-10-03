#!/usr/bin/env python3
import json, pathlib, subprocess, re, collections
ROOT=pathlib.Path('/mnt/disk1/Code/DevControl2'); ART=pathlib.Path('artifacts')
def run(*a):
 p=subprocess.run(['git','-C',str(ROOT),*a],text=True,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL); return p.stdout.strip(),p.returncode
if not (ART/'devcontrol-lineage.json').exists(): subprocess.check_call(['python3','src/engineeringos/devcontrol_lineage.py'])
p=json.load(open(ART/'devcontrol-lineage.json')); inv=json.load(open(ART/'devcontrol-inventory.json'))
wt_by_branch={w.get('branch'):w for w in inv['worktrees'] if w.get('branch')}
def role(branch,wt=None):
 path=(wt or {}).get('path',''); locked=(wt or {}).get('locked','')
 if branch.startswith('release/'): return 'release'
 if 'prod' in path.lower() or 'production' in locked.lower(): return 'production-reference'
 if 'incident' in branch or 'forensic' in path.lower(): return 'forensic'
 if branch.startswith('docs/'): return 'documentation'
 if branch.startswith(('feat/','fix/','work/')): return 'development'
 return 'unknown'
items=[]
for b in p['branches']:
 wt=wt_by_branch.get(b['name']); r=role(b['name'],wt)
 dirty=None
 if wt:
  q=subprocess.run(['git','-C',wt['path'],'status','--porcelain'],text=True,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
  dirty=(q.returncode==0 and bool(q.stdout.strip()))
  dirty_lines=q.stdout.splitlines() if q.returncode==0 else []
  dirty_paths=[]
  for line in dirty_lines:
   path=line[3:] if len(line)>=4 else line
   dirty_paths.append(path.split(' -> ')[-1])
 items.append({**b,'workspace':wt,'role':r,'dirty':dirty,'dirty_change_count':len(dirty_lines),'dirty_paths':dirty_paths[:30]})
# dimensions preserve evidence; no automatic merge/delete recommendation.
duplicate=[]
for grp in p['exact_head_aliases']:
 active=[x for x in grp if x!='main']
 if len(active)>1: duplicate.append({'branches':active,'head':next((b['sha'] for b in items if b['name']==active[0]),None)})
overlap=[x for x in p['relationships'] if x['path_overlap']>=.30 and not x['same_head'] and not x['a_ancestor_of_b'] and not x['b_ancestor_of_a']]
divergence=[]
for b in items:
 if b['role']=='development' and not b['contained_in_origin_main'] and b['behind_origin_main']>=20:
  divergence.append({'branch':b['name'],'behind':b['behind_origin_main'],'ahead':b['ahead_origin_main'],'concern':b['concern']})
role_debt=[{'branch':b['name'],'workspace':(b['workspace'] or {}).get('path')} for b in items if b['workspace'] and b['role']=='unknown']
dirty=[{'branch':b['name'],'role':b['role'],'workspace':b['workspace']['path'],'change_count':b['dirty_change_count'],'changed_paths':b['dirty_paths']} for b in items if b['dirty']]
# Verification debt cannot yet be asserted without CI/release/prod evidence graph. Track as UNKNOWN rather than zero.
report={'dimensions':{
 'duplicate_state':{'count':len(duplicate),'evidence':duplicate},
 'divergence':{'count':len(divergence),'evidence':divergence},
 'overlap':{'count':len(overlap),'evidence':overlap},
 'role':{'count':len(role_debt),'evidence':role_debt},
 'dirty_workspace':{'count':len(dirty),'evidence':dirty},
 'verification':{'status':'UNKNOWN','reason':'CI, release, deployment, and production evidence are not yet joined into the World Model'}},
 'workspace_roles':dict(collections.Counter(b['role'] for b in items)),
 'guardrail':'Counts are pressure indicators, not merge/delete recommendations.'}
(ART/'convergence-debt.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({k:(v.get('count') if isinstance(v,dict) else v) for k,v in report['dimensions'].items()},indent=2))
print('roles',report['workspace_roles'])
print('\nDIRTY WORKSPACES')
for x in dirty: print(x)
