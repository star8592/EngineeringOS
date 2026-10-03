#!/usr/bin/env python3
import subprocess,json,pathlib
from semantic_collision import assess
R='/mnt/disk1/Code/DevControl2'
def git(*a):return subprocess.check_output(['git','-C',R,*a],text=True).strip()
active=git('status','--porcelain=v1').splitlines(); paths=[]
for line in active:
 p=line[3:]; paths.append(p.split(' -> ')[-1])
planned=['scripts/deploy_production.sh','scripts/stage_server_package.sh','scripts/stage_agent_package.sh','scripts/check_release_pipeline_contract.sh','docs/architecture/RELEASE_PROVENANCE.md']
r=assess(planned,paths,['release_identity','release_qualification']);r.update({'active_branch':git('branch','--show-current'),'planned_change':'DEVCONTROL_RELEASE_PROVENANCE_CONTRACT'})
pathlib.Path('artifacts/devcontrol-semantic-collision.json').write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n');print(json.dumps(r,indent=2,ensure_ascii=False))
