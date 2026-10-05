import json,pathlib,subprocess,sys,tempfile
sys.path.insert(0,'src/engineeringos')
from external_project_baseline import inspect_project,refresh_registered_projects

def run(*args,cwd=None):
 return subprocess.check_output(args,cwd=cwd,text=True).strip()

with tempfile.TemporaryDirectory() as td:
 root=pathlib.Path(td);repo=root/'repo';repo.mkdir()
 run('git','init','-q',cwd=repo);run('git','config','user.email','t@example.com',cwd=repo);run('git','config','user.name','T',cwd=repo)
 (repo/'package.json').write_text(json.dumps({'scripts':{'build':'next build','test:smoke':'python x.py','dev':'next dev','verify:public':'bash q.sh'}}))
 (repo/'a.txt').write_text('base');run('git','add','.',cwd=repo);run('git','commit','-qm','base',cwd=repo)
 cfg={'name':'P','display_name':'产品P','repo':str(repo),'autopilot_enabled':False}
 clean=inspect_project(cfg)
 assert clean['state']=='CLEAN_CONNECTED' and clean['mutation_eligible'] and clean['dirty_path_count']==0
 assert clean['verification_entrypoints']==['build','test:smoke','verify:public']
 (repo/'a.txt').write_text('changed');(repo/'new.txt').write_text('new')
 dirty=inspect_project(cfg)
 assert dirty['state']=='PROTECTED_EXISTING_WORK' and not dirty['mutation_eligible'] and dirty['protected_existing_work']
 assert dirty['modified_paths']==['a.txt'] and dirty['untracked_paths']==['new.txt']
 assert 'changed' not in json.dumps(dirty) and 'new\n' not in json.dumps(dirty)
 runtime=root/'rt';reg=runtime/'projects'/'registry.json';reg.parent.mkdir(parents=True)
 reg.write_text(json.dumps({'schema_version':1,'projects':[cfg]}))
 out=refresh_registered_projects(reg,runtime)
 assert out['projects'][0]['fingerprint']==dirty['fingerprint']
 assert json.loads((runtime/'projects'/'P'/'baseline.json').read_text())['state']=='PROTECTED_EXISTING_WORK'
 print('14 external-project-baseline invariants passed')
