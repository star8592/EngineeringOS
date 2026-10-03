from __future__ import annotations
import subprocess,pathlib
from facts import Fact,now_utc

def git(repo,*args):
 p=subprocess.run(['git','-C',str(repo),*args],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 if p.returncode: raise RuntimeError(p.stderr.strip() or 'git failed')
 return p.stdout.strip()

def inventory(repo, project):
 repo=pathlib.Path(repo); obs=now_utc(); head=git(repo,'rev-parse','HEAD'); branch=git(repo,'branch','--show-current') or 'DETACHED'; dirty=bool(git(repo,'status','--porcelain'))
 try: origin=git(repo,'rev-parse','origin/main')
 except: origin=None
 branches=git(repo,'for-each-ref','--format=%(refname:short)','refs/heads').splitlines()
 facts=[Fact(project,'source_sha',head,f'repository/{branch}',obs,'git-ref',branch,'repository-observation'),Fact(project,'workspace_dirty',dirty,f'repository/{branch}',obs,'git-status',str(repo),'repository-observation')]
 if origin:facts.append(Fact(project,'source_sha',origin,'repository/origin-main',obs,'git-ref','origin/main','canonical-source'))
 return {'project':project,'repo':str(repo),'branch':branch,'head':head,'origin_main':origin,'dirty':dirty,'branches':branches,'facts':[x.to_dict() for x in facts]}
