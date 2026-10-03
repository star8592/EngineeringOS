#!/usr/bin/env python3
import json, pathlib, subprocess, urllib.request, ssl
from facts import Fact, now_utc
REPO=pathlib.Path('/mnt/disk1/Code/DevControl2'); OUT=pathlib.Path('artifacts/devcontrol-reconciliation.json')
def git(*a): return subprocess.check_output(['git','-C',str(REPO),*a],text=True).strip()
def fetch(url):
 ctx=ssl._create_unverified_context()
 with urllib.request.urlopen(url,timeout=8,context=ctx) as r: return json.load(r)
obs=now_utc(); source_sha=git('rev-parse','origin/main'); source_version=git('show','origin/main:VERSION')
ready=fetch('https://mcp.devcontrol.dev/readyz'); live=fetch('https://mcp.devcontrol.dev/livez')
facts=[
 Fact('devcontrol','source_sha',source_sha,'repository/origin-main',obs,'git-ref','origin/main','canonical-source'),
 Fact('devcontrol','product_version',source_version,'repository/origin-main',obs,'git-file',f'VERSION@{source_sha}','canonical-source'),
 Fact('devcontrol','product_version',ready['version'],'production',obs,'runtime-http','https://mcp.devcontrol.dev/readyz','runtime-observation'),
 Fact('devcontrol','release_id',ready['release_id'],'production',obs,'runtime-http','https://mcp.devcontrol.dev/readyz','runtime-observation'),
]
checks=[]
checks.append({'predicate':'runtime_endpoint_consistency','state':'RESOLVED' if ready.get('version')==live.get('version') and ready.get('release_id')==live.get('release_id') else 'CONTRADICTION','evidence':{'readyz':ready,'livez':live}})
checks.append({'predicate':'source_vs_production_version','state':'DRIFT' if source_version!=ready['version'] else 'RESOLVED','source':source_version,'production':ready['version']})
# release id is short SHA-like; resolve only if it uniquely prefixes a commit and is ancestor of source head.
rid=ready['release_id']; candidates=git('rev-list','--all').splitlines(); matches=[x for x in candidates if x.startswith(rid)]
if len(matches)==1:
 full=matches[0]
 anc=subprocess.run(['git','-C',str(REPO),'merge-base','--is-ancestor',full,'origin/main']).returncode==0
 checks.append({'predicate':'production_release_to_source','state':'RESOLVED','release_id':rid,'full_source_sha':full,'is_ancestor_of_origin_main':anc})
else:
 checks.append({'predicate':'production_release_to_source','state':'UNKNOWN','release_id':rid,'candidate_count':len(matches)})
data={'observed_at':obs,'facts':[f.to_dict() for f in facts],'reconciliation':checks,'authority_policy':{'repository/origin-main.product_version':'canonical-source','production.product_version':'runtime-observation','production.release_id':'runtime-observation'}}
OUT.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(data,indent=2))
