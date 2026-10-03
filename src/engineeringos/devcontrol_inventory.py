#!/usr/bin/env python3
import json, subprocess, pathlib, re, datetime
REPO=pathlib.Path('/mnt/disk1/Code/DevControl2')
OUT=pathlib.Path('artifacts/devcontrol-inventory.json')
def git(*args):
    return subprocess.check_output(['git','-C',str(REPO),*args], text=True, stderr=subprocess.DEVNULL)
def concern(name):
    rules=[('approval-tool-surface',r'approval|tool-surface|no-inline|device-manager'),('mcp-protocol',r'mcp|host-acceptance|resource-transition|legacy-agent-tool|process-route'),('release',r'release|prod'),('browser',r'browser'),('mobile',r'android|ios|mobile'),('gateway-ha',r'gateway|rqlite|ha'),('incident-quality',r'incident|hygiene'),('auth',r'auth|oauth')]
    return next((k for k,p in rules if re.search(p,name,re.I)),'other')
raw=git('worktree','list','--porcelain').splitlines(); w=[]; cur={}
for line in raw+['']:
    if not line:
        if cur: w.append(cur); cur={}
    elif line.startswith('worktree '): cur['path']=line[9:]
    elif line.startswith('HEAD '): cur['head']=line[5:]
    elif line.startswith('branch '): cur['branch']=line[7:].removeprefix('refs/heads/')
    elif line=='detached': cur['detached']=True
    elif line.startswith('locked'): cur['locked']=line[7:].strip()
branches=[]
fmt='%(refname:short)|%(objectname:short)|%(committerdate:iso8601)|%(upstream:short)|%(upstream:track)'
for line in git('for-each-ref','--sort=-committerdate',f'--format={fmt}','refs/heads/').splitlines():
    name,sha,date,up,track=(line.split('|')+['','','','',''])[:5]
    branches.append({'name':name,'sha':sha,'date':date,'upstream':up,'track':track,'concern':concern(name)})
for x in w:
    if 'branch' in x: x['concern']=concern(x['branch'])
summary={'worktrees':len(w),'attached_worktrees':sum('branch'in x for x in w),'detached_worktrees':sum(x.get('detached',False) for x in w),'locked_worktrees':sum('locked'in x for x in w),'local_branches':len(branches)}
clusters={}
for b in branches: clusters.setdefault(b['concern'],[]).append(b['name'])
# evidence-backed risk signals only; no mutation or automatic supersede decisions.
risks=[]
for c,names in clusters.items():
    if len(names)>=3: risks.append({'type':'high_parallelism','concern':c,'count':len(names),'branches':names})
for b in branches:
    m=re.search(r'behind (\d+)',b['track'])
    if m and int(m.group(1))>=30: risks.append({'type':'stale_vs_upstream','branch':b['name'],'behind':int(m.group(1)),'concern':b['concern']})
data={'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'repo':str(REPO),'summary':summary,'clusters':clusters,'risk_signals':risks,'worktrees':w,'branches':branches}
OUT.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'summary':summary,'cluster_counts':{k:len(v) for k,v in clusters.items()},'risk_signal_count':len(risks)},indent=2))
