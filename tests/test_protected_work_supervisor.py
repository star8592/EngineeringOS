import json,pathlib,subprocess,sys,tempfile
sys.path.insert(0,'src/engineeringos')
import supervisor as sup

def run(*a,cwd=None):return subprocess.check_output(a,cwd=cwd,text=True).strip()

with tempfile.TemporaryDirectory() as td:
 root=pathlib.Path(td);repo=root/'repo';repo.mkdir()
 run('git','init','-q',cwd=repo);run('git','config','user.email','t@example.com',cwd=repo);run('git','config','user.name','T',cwd=repo)
 (repo/'a.ts').write_text('export const x=1\n');run('git','add','a.ts',cwd=repo);run('git','commit','-qm','base',cwd=repo)
 (repo/'a.ts').write_text('import { y } from "./b"; export const x=y\n');(repo/'b.ts').write_text('export const y=2\n')
 rt=root/'runtime';(rt/'projects').mkdir(parents=True)
 (rt/'projects'/'registry.json').write_text(json.dumps({'schema_version':1,'projects':[{'name':'P','display_name':'产品P','repo':str(repo),'autopilot_enabled':False}]}))
 old=sup.STATE
 try:
  sup.STATE=rt
  first=sup.run_project_baseline_lane()
  assert first['health']=='HEALTHY' and first['states']['PROTECTED_EXISTING_WORK']==1
  assert first['protected_work']['P']['dirty_path_count']==2 and first['protected_work']['P']['candidate_packages']==1
  inv=json.loads((rt/'projects'/'P'/'protected-work.json').read_text())
  assert inv['state']=='PROTECTED_EXISTING_WORK' and inv['safety']['mutation_authorized'] is False
  second=sup.run_project_baseline_lane()
  inv2=json.loads((rt/'projects'/'P'/'protected-work.json').read_text())
  assert all(x['observation']=='STABLE' for x in inv2['paths'])
  run('git','reset','--hard','HEAD',cwd=repo);(repo/'b.ts').unlink()
  third=sup.run_project_baseline_lane()
  inv3=json.loads((rt/'projects'/'P'/'protected-work.json').read_text())
  assert third['states']['CLEAN_CONNECTED']==1 and inv3['state']=='CLEAN' and inv3['dirty_path_count']==0
 finally:
  sup.STATE=old
print('12 protected-work-supervisor invariants passed')
