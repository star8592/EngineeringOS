#!/usr/bin/env python3
import json, pathlib, subprocess, re
from facts import Fact, now_utc, contradictions
REPO=pathlib.Path('/mnt/disk1/Code/DevControl2'); OUT=pathlib.Path('artifacts/fact-registry.json')
def git(*a): return subprocess.check_output(['git','-C',str(REPO),*a],text=True).strip()
obs=now_utc(); head=git('rev-parse','origin/main'); version=git('show','origin/main:VERSION')
facts=[Fact('devcontrol','source_sha',head,'repository/origin-main',obs,'git-ref','origin/main','canonical-source',1.0),Fact('devcontrol','product_version',version,'repository/origin-main',obs,'git-file',f'VERSION@{head}','canonical-source',1.0),Fact('devcontrol','modern_mcp_protocol','2026-07-28','architecture/current',obs,'canonical-doc','docs/architecture/CHATGPT_MCP_INTEGRATION.md','accepted-architecture',1.0)]
# Extract explicitly scoped current production claims from canonical architecture docs as claims, not runtime truth.
p=REPO/'docs/architecture/APPROVAL_SEMANTICS_AND_TOOL_SURFACE_PLAN.md'
for n,line in enumerate(p.read_text(errors='ignore').splitlines(),1):
    m=re.search(r'Production health reports `version=(3\.\d+\.\d+)`, `release_id=([^`]+)`',line)
    if m:
        ref=f'{p.relative_to(REPO)}:{n}'
        facts += [Fact('devcontrol','product_version',m.group(1),'production',obs,'canonical-doc',ref,'documented-claim',0.8,ref),Fact('devcontrol','release_id',m.group(2),'production',obs,'canonical-doc',ref,'documented-claim',0.8,ref)]
# Cross-scope drift is not contradiction: emit reconciliation candidates explicitly.
recon=[]
repo_versions=[f for f in facts if f.predicate=='product_version' and f.scope=='repository/origin-main']
prod_versions=[f for f in facts if f.predicate=='product_version' and f.scope=='production']
for a in repo_versions:
    for b in prod_versions:
        if a.value!=b.value:
            recon.append({'kind':'SOURCE_PRODUCTION_VERSION_DRIFT','left':a.to_dict(),'right':b.to_dict(),'resolution_required':['live production runtime identity','release provenance linking production release_id to full source SHA']})
data={'facts':[f.to_dict() for f in facts],'contradictions':[c.to_dict() for c in contradictions(facts)],'reconciliation_candidates':recon,'semantics':{'contradiction':'same subject/predicate/scope with incompatible values','drift':'different compatible scopes whose relationship requires provenance'}}
OUT.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'facts':len(facts),'contradictions':len(data['contradictions']),'reconciliation_candidates':len(recon)},indent=2))
for x in recon: print(x['kind'],x['left']['value'],'vs',x['right']['value'])
