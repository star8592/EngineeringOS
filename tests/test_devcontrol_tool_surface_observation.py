import json,pathlib,subprocess,sys,tempfile
sys.path.insert(0,'scripts')
from devcontrol_tool_surface_observation import run

with tempfile.TemporaryDirectory() as td:
 root=pathlib.Path(td);repo=root/'backend';scripts=repo/'scripts';scripts.mkdir(parents=True)
 subprocess.run(['git','init','-q'],cwd=repo,check=True)
 subprocess.run(['git','config','user.email','t@example.com'],cwd=repo,check=True)
 subprocess.run(['git','config','user.name','T'],cwd=repo,check=True)
 (repo/'VERSION').write_text('1.2.3\n')
 checker=scripts/'check.py';checker.write_text('print("SOURCE_OK")\n')
 verifier=scripts/'verify.py';verifier.write_text('print("HOST_OK")\n')
 provider=scripts/'provider.py';provider.write_text('MODERN_ERA="2026"\ndef live_catalog(base,era,tasks):\n return {"result":{"tools":[{"name":"x","description":"Do x","inputSchema":{"type":"object","properties":{"a":{"type":"string"}},"required":["a"]}}]}}\n')
 subprocess.run(['git','add','.'],cwd=repo,check=True);subprocess.run(['git','commit','-qm','base'],cwd=repo,check=True)
 profile=root/'profile.json';profile.write_text(json.dumps({'schema_version':1,'backend':'B','repo':str(repo),'live_base':'https://example.invalid','canonical_checker':'scripts/check.py','host_verifier':'scripts/verify.py','canonical_catalog_provider':'scripts/provider.py','authority':'BACKEND_OWNED_CANONICAL_CONTRACT'}))
 host=root/'host.json';host.write_text(json.dumps({'tools':[{'name':'x','description':'Do x\n\n```ts\ntool(args: { a: string }): Promise<{ result: any }>;\n```'}]}))
 out=root/'out.json';a=run(profile,host,out)
 assert a['state']=='OBSERVED_MATCH' and a['source_live_check']=='PASS' and a['host_observable_contract_check']=='PASS'
 checker.write_text('import sys;print("SOURCE_BAD");sys.exit(1)\n')
 b=run(profile,host,out)
 assert b['state']=='TOOL_SURFACE_DRIFT' and b['source_live_check']=='FAIL'
 print('8 devcontrol-surface-observation invariants passed')
