import pathlib,subprocess,sys,tempfile
sys.path.insert(0,'src/engineeringos')
from deferred_maintenance_candidate import prepare,prepare_iterative,DeferredCandidateError
from coding_agent_provider import TaskEnvelope,AgentCandidate

def run(*a,cwd=None):return subprocess.check_output(a,cwd=cwd,text=True).strip()

class Good:
 name='fixture-good'
 def propose(self,*,task,files):
  assert files['x.txt']=='old\n'
  return AgentCandidate(provider=self.name,model='fixture',changes={'x.txt':'new\n'},confidence=1.0)

class Noop:
 name='fixture-noop'
 def propose(self,*,task,files):
  return AgentCandidate(provider=self.name,model='fixture',changes={'x.txt':files['x.txt']})


class Repairing:
 name='fixture-repair'
 def __init__(self):self.calls=0
 def propose(self,*,task,files):
  self.calls+=1
  if self.calls==1:
   return AgentCandidate(provider=self.name,model='fixture',changes={'x.txt':'bad\n'},rationale='first')
  assert 'previous_attempt' in task.context and files['x.txt']=='bad\n'
  return AgentCandidate(provider=self.name,model='fixture',changes={'x.txt':'new\n'},rationale='repair')

with tempfile.TemporaryDirectory() as td:
 root=pathlib.Path(td);repo=root/'repo';repo.mkdir()
 run('git','init','-q',cwd=repo);run('git','config','user.email','t@example.com',cwd=repo);run('git','config','user.name','T',cwd=repo)
 (repo/'x.txt').write_text('old\n');run('git','add','x.txt',cwd=repo);run('git','commit','-qm','base',cwd=repo);sha=run('git','rev-parse','HEAD',cwd=repo)
 # Dirty unrelated source work is intentionally allowed and must survive unchanged.
 (repo/'unrelated.txt').write_text('protected\n')
 before=run('git','status','--porcelain=v1','--branch',cwd=repo)
 task=TaskEnvelope(project='P',item_id='m1',source_sha=sha,goal='make x new',allowed_paths=('x.txt',),verification_argv=(sys.executable,'-c',"assert open('x.txt').read()=='new\\n'"),context={})
 out=prepare(repo,task,Good(),verification_timeout=20)
 after=run('git','status','--porcelain=v1','--branch',cwd=repo)
 assert out['state']=='VERIFIED_DEFERRED_CANDIDATE' and out['convergence_authorized'] is False
 assert out['changed_paths']==['x.txt'] and out['diff_sha256'] and 'new' in out['patch'] and before==after
 badtask=TaskEnvelope(project='P',item_id='m2',source_sha=sha,goal='fail verify',allowed_paths=('x.txt',),verification_argv=(sys.executable,'-c','import sys;sys.exit(9)'),context={})
 bad=prepare(repo,badtask,Good(),verification_timeout=20)
 assert bad['state']=='VERIFICATION_FAILED' and bad['verification']['exit_code']==9 and before==run('git','status','--porcelain=v1','--branch',cwd=repo)
 repairing=Repairing()
 repaired=prepare_iterative(repo,task,repairing,max_attempts=3,verification_timeout=20)
 assert repaired['state']=='VERIFIED_DEFERRED_CANDIDATE' and repaired['attempt_count']==2 and repairing.calls==2
 assert [x['state'] for x in repaired['attempts']]==['VERIFICATION_FAILED','VERIFIED_DEFERRED_CANDIDATE']
 assert before==run('git','status','--porcelain=v1','--branch',cwd=repo)
 try:prepare(repo,task,Noop(),verification_timeout=20);raise AssertionError()
 except DeferredCandidateError as e:assert str(e)=='ACTUAL_MUTATION_SURFACE_DRIFT'
 run('git','add','unrelated.txt',cwd=repo);run('git','commit','-qm','advance',cwd=repo)
 try:prepare(repo,task,Good(),verification_timeout=20);raise AssertionError()
 except DeferredCandidateError as e:assert str(e)=='SOURCE_SHA_DRIFT'
print('15 deferred-maintenance-candidate invariants passed')
