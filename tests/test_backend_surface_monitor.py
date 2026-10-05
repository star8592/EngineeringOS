import json,pathlib,subprocess,sys,tempfile
sys.path.insert(0,'src/engineeringos')
from backend_surface_monitor import reconcile,semantic_sha256

with tempfile.TemporaryDirectory() as td:
 root=pathlib.Path(td);repo=root/'backend';scripts=repo/'scripts';scripts.mkdir(parents=True)
 subprocess.run(['git','init','-q'],cwd=repo,check=True)
 checker=scripts/'check.py';checker.write_text('print("SOURCE_OK")\n')
 provider=scripts/'provider.py'
 canonical={'result':{'tools':[{'name':'x','description':'x','inputSchema':{'type':'object'}}]}}
 provider.write_text('MODERN_ERA="2026"\ndef live_catalog(base,era,tasks):\n return '+repr(canonical)+'\n')
 profile={'schema_version':1,'backend':'B','repo':str(repo),'live_base':'https://example.invalid','canonical_checker':'scripts/check.py','canonical_catalog_provider':'scripts/provider.py','authority':'BACKEND_OWNED_CANONICAL_CONTRACT'}
 evidence={'state':'OBSERVED_MATCH','host_observable_contract_check':'PASS','host_acceptance':'NOT_PROVEN_BY_SURFACE_OBSERVATION','canonical_catalog_semantic_sha256':semantic_sha256(canonical)}
 a=reconcile(profile,evidence);assert a['state']=='CONVERGED'
 b=reconcile(profile,None);assert b['state']=='HOST_OBSERVATION_MISSING'
 changed={'result':{'tools':[{'name':'x','description':'changed','inputSchema':{'type':'object'}}]}}
 provider.write_text('MODERN_ERA="2026"\ndef live_catalog(base,era,tasks):\n return '+repr(changed)+'\n')
 c=reconcile(profile,evidence);assert c['state']=='HOST_OBSERVATION_STALE' and c['reason']=='CANONICAL_TOOL_CONTRACT_CHANGED'
 checker.write_text('import sys;print("BAD");sys.exit(1)\n')
 d=reconcile(profile,evidence);assert d['state']=='TOOL_SURFACE_DRIFT' and d['reason']=='SOURCE_LIVE_SURFACE_DRIFT'
 legacy={k:v for k,v in evidence.items() if k!='canonical_catalog_semantic_sha256'}
 checker.write_text('print("SOURCE_OK")\n');provider.write_text('MODERN_ERA="2026"\ndef live_catalog(base,era,tasks):\n return '+repr(canonical)+'\n')
 e=reconcile(profile,legacy);assert e['state']=='HOST_OBSERVATION_STALE' and e['reason']=='LEGACY_OBSERVATION_WITHOUT_SEMANTIC_HASH'
 print('9 backend-surface-monitor invariants passed')
