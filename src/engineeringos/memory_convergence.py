#!/usr/bin/env python3
import json,re,pathlib,subprocess,datetime
REPO=pathlib.Path('/mnt/disk1/Code/DevControl2'); OUT=pathlib.Path('artifacts/memory-convergence.json')
def text(p):
 try:return p.read_text(errors='ignore')
 except:return ''
version=text(REPO/'VERSION').strip()
findings=[]
# High-confidence fact: canonical VERSION versus explicit claims of production/current health versions.
pat=re.compile(r'(?i)(?:production health reports|current(?:ly)?(?: production)? version|production[^\n]{0,40}version)\s*[=`:]?\s*(3\.\d+\.\d+)')
for p in (REPO/'docs').rglob('*.md'):
 t=text(p)
 for i,line in enumerate(t.splitlines(),1):
  m=pat.search(line)
  if m and m.group(1)!=version:
   findings.append({'type':'VERSION_CLAIM_DRIFT','file':str(p.relative_to(REPO)),'line':i,'claimed':m.group(1),'canonical_version':version,'text':line.strip()[:240]})
# Accepted/current architecture should not contain obviously retired protocol as canonical unless bounded compatibility context is explicit.
for p in (REPO/'docs/architecture').rglob('*.md'):
 for i,line in enumerate(text(p).splitlines(),1):
  if '2025-11-25' in line and not re.search(r'compat|handshake|legacy|older|bounded|migration',line,re.I):
   findings.append({'type':'PROTOCOL_CONTEXT_REVIEW','file':str(p.relative_to(REPO)),'line':i,'text':line.strip()[:240]})
# Machine facts that should be visible to memory checker.
head=subprocess.check_output(['git','-C',str(REPO),'rev-parse','origin/main'],text=True).strip()
report={'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'canonical_facts':{'version':version,'origin_main':head,'modern_mcp':'2026-07-28'},'finding_count':len(findings),'findings':findings,'guardrail':'Findings are review candidates. Historical/incident documents may intentionally contain old facts; only canonical-current claims should be repaired.'}
OUT.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'canonical_facts':report['canonical_facts'],'finding_count':len(findings)},indent=2))
for f in findings[:30]: print(f)
