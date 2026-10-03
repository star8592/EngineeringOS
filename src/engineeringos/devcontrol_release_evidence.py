#!/usr/bin/env python3
import json,pathlib,subprocess,hashlib,urllib.request,ssl,datetime
REPO=pathlib.Path('/mnt/disk1/Code/DevControl2'); E=pathlib.Path.home()/'.local/state/devcontrol3/release-evidence'; OUT=pathlib.Path('artifacts/devcontrol-release-evidence.json')
def git(*a): return subprocess.check_output(['git','-C',str(REPO),*a],text=True).strip()
def fetch(url):
 with urllib.request.urlopen(url,timeout=8,context=ssl._create_unverified_context()) as r:return json.load(r)
ready=fetch('https://mcp.devcontrol.dev/readyz'); rid=ready['release_id']; p=E/f'{rid}.json'; ev=json.load(open(p)) if p.exists() else None
matches=[x for x in git('rev-list','--all').splitlines() if x.startswith(rid)]
full=matches[0] if len(matches)==1 else None
# Inspect staged package checksum manifests if retained; do not claim artifact identity without exact package bytes/manifest binding.
qualified=bool(ev and 'release_gate_all' in ev.get('gates',[]) and 'post_deploy' in ev.get('gates',[]))
out={'observed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'production':ready,'release_evidence_file':str(p) if p.exists() else None,'qualification_evidence':ev,'full_source_sha':full,'source_identity_state':'RESOLVED' if full else 'UNKNOWN','qualification_state':'RESOLVED' if qualified else 'UNKNOWN','artifact_identity_state':'UNKNOWN','deployment_identity_state':'PARTIAL','reasoning':{'artifact_identity':'release evidence records qualification gates but not immutable server/agent artifact digests','deployment_identity':'runtime release_id is observed and maps to source, but runtime does not expose full source SHA/artifact digest'}}
OUT.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n');print(json.dumps(out,indent=2,ensure_ascii=False))
