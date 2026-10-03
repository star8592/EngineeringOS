#!/usr/bin/env python3
import subprocess,json,pathlib
from collision import dispatch_collision_decision
R='/mnt/disk1/Code/DevControl2'
def git(*a):return subprocess.check_output(['git','-C',R,*a],text=True).strip()
active=(git('diff','--name-only').splitlines()+git('ls-files','--others','--exclude-standard').splitlines())
# Producer-side provenance change surface, intentionally explicit before implementation.
planned=['scripts/deploy_production.sh','scripts/stage_server_package.sh','scripts/stage_agent_package.sh','scripts/check_release_pipeline_contract.sh','docs/architecture/RELEASE_PROVENANCE.md']
r=dispatch_collision_decision(planned,active,bool(active));r.update({'active_branch':git('branch','--show-current'),'planned_change':'DEVCONTROL_RELEASE_PROVENANCE_CONTRACT'})
pathlib.Path('artifacts/devcontrol-collision-probe.json').write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n');print(json.dumps(r,indent=2,ensure_ascii=False))
