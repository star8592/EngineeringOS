import json,pathlib,subprocess,sys,tempfile,time
sys.path.insert(0,'src/engineeringos')
from protected_work_inventory import inspect

def run(*a,cwd=None):return subprocess.check_output(a,cwd=cwd,text=True).strip()

with tempfile.TemporaryDirectory() as td:
 root=pathlib.Path(td);repo=root/'repo';repo.mkdir()
 run('git','init','-q',cwd=repo);run('git','config','user.email','t@example.com',cwd=repo);run('git','config','user.name','T',cwd=repo)
 (repo/'src').mkdir();(repo/'src'/'page.tsx').write_text('export const x=1\n')
 (repo/'README.md').write_text('base\n');run('git','add','.',cwd=repo);run('git','commit','-qm','base',cwd=repo)
 (repo/'src'/'page.tsx').write_text('import { y } from "./lib"; export const x=y\n')
 (repo/'src'/'lib.ts').write_text('export const y=2\n')
 (repo/'docs').mkdir();(repo/'docs'/'GOV.md').write_text('see ops/state.py\n')
 (repo/'ops').mkdir();(repo/'ops'/'state.py').write_text('print("state")\n')
 (repo/'.env.local').write_text('SECRET=never-store-me\n')
 first=inspect(repo)
 assert first['state']=='PROTECTED_EXISTING_WORK' and first['dirty_path_count']==5
 rows={x['path']:x for x in first['paths']}
 assert rows['.env.local']['sensitive'] and rows['.env.local']['fingerprint'] is None
 assert all(x['authority']=='PROTECTED_EXISTING_WORK' for x in first['paths'])
 edgepairs={(e['a'],e['b'],e['kind']) for e in first['structural_edges']}
 assert ('src/lib.ts','src/page.tsx','LOCAL_IMPORT') in edgepairs
 assert ('docs/GOV.md','ops/state.py','EXACT_PATH_REFERENCE') in edgepairs
 comps=[set(x['paths']) for x in first['candidate_packages']]
 assert {'src/lib.ts','src/page.tsx'} in comps and {'docs/GOV.md','ops/state.py'} in comps
 assert first['safety']['mutation_authorized'] is False and first['safety']['candidate_groups_authoritative'] is False
 second=inspect(repo,first)
 assert all(x['observation']=='STABLE' for x in second['paths'])
 assert all(x['state']=='STABLE_RECENT' for x in second['candidate_packages'])
 old=json.loads(json.dumps(second))
 for x in old['paths']:x['last_changed']='2020-01-01T00:00:00+00:00'
 quiet=inspect(repo,old,quiet_after_seconds=1);assert all(x['state']=='QUIET' for x in quiet['candidate_packages'])
 (repo/'src'/'lib.ts').write_text('export const y=3\n')
 third=inspect(repo,second);rows3={x['path']:x for x in third['paths']}
 assert rows3['src/lib.ts']['observation']=='CHANGED' and rows3['src/page.tsx']['observation']=='STABLE'
 (repo/'docs'/'GOV.md').unlink()
 fourth=inspect(repo,third)
 assert 'docs/GOV.md' in fourth['disappeared_paths']
 run('git','reset','--hard','HEAD',cwd=repo)
 for p in ['src/lib.ts','ops/state.py','.env.local']:
  q=repo/p
  if q.exists():q.unlink()
 clean=inspect(repo,fourth)
 assert clean['state']=='CLEAN' and clean['dirty_path_count']==0
print('21 protected-work-inventory invariants passed')
