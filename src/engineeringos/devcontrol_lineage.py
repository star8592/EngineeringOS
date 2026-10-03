#!/usr/bin/env python3
import json, subprocess, pathlib, itertools, collections
REPO=pathlib.Path('/mnt/disk1/Code/DevControl2'); OUT=pathlib.Path('artifacts/devcontrol-lineage.json')
def g(*a, check=True):
 p=subprocess.run(['git','-C',str(REPO),*a],text=True,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
 if check and p.returncode: raise RuntimeError(a)
 return p.stdout.strip()
def ok(*a): return subprocess.run(['git','-C',str(REPO),*a],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
inv=json.load(open('artifacts/devcontrol-inventory.json')) if pathlib.Path('artifacts/devcontrol-inventory.json').exists() else None
if inv is None:
 subprocess.check_call(['python3','src/engineeringos/devcontrol_inventory.py']); inv=json.load(open('artifacts/devcontrol-inventory.json'))
branches=[b for b in inv['branches'] if b['name']!='main']
base='origin/main'
# changed paths and divergence are mechanical evidence only.
for b in branches:
 b['ahead_origin_main']=int(g('rev-list','--count',f'{base}..{b["name"]}') or 0)
 b['behind_origin_main']=int(g('rev-list','--count',f'{b["name"]}..{base}') or 0)
 b['merge_base']=g('merge-base',base,b['name'],check=False)
 b['changed_paths']=g('diff','--name-only',f'{base}...{b["name"]}',check=False).splitlines()
 b['contained_in_origin_main']=ok('merge-base','--is-ancestor',b['name'],base)
heads=collections.defaultdict(list)
for b in branches: heads[b['sha']].append(b['name'])
aliases=[v for v in heads.values() if len(v)>1]
pairs=[]
# Compare within concern plus exact-head aliases; this keeps output bounded and meaningful.
for a,b in itertools.combinations(branches,2):
 if a['concern']!=b['concern'] and a['sha']!=b['sha']: continue
 A=set(a['changed_paths']); B=set(b['changed_paths']); inter=A&B; union=A|B
 overlap=(len(inter)/len(union)) if union else 0.0
 a_in_b=ok('merge-base','--is-ancestor',a['name'],b['name']); b_in_a=ok('merge-base','--is-ancestor',b['name'],a['name'])
 if overlap>=0.15 or a_in_b or b_in_a or a['sha']==b['sha']:
  pairs.append({'a':a['name'],'b':b['name'],'concern':a['concern'] if a['concern']==b['concern'] else 'cross-concern','same_head':a['sha']==b['sha'],'a_ancestor_of_b':a_in_b,'b_ancestor_of_a':b_in_a,'path_overlap':round(overlap,3),'shared_paths':sorted(inter)[:30]})
pairs.sort(key=lambda x:(x['same_head'],x['a_ancestor_of_b'] or x['b_ancestor_of_a'],x['path_overlap']),reverse=True)
data={'base':base,'branch_count':len(branches),'exact_head_aliases':aliases,'relationships':pairs,'branches':branches}
OUT.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'branches':len(branches),'exact_head_alias_groups':len(aliases),'relationship_candidates':len(pairs),'contained_in_origin_main':sum(b['contained_in_origin_main'] for b in branches)},indent=2))
print('\nTOP RELATIONSHIPS')
for x in pairs[:20]: print(f"{x['a']} <-> {x['b']} | {x['concern']} | overlap={x['path_overlap']} same={x['same_head']} ancestor={x['a_ancestor_of_b']}/{x['b_ancestor_of_a']}")
