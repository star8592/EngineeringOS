import pathlib,subprocess,sys,tempfile
sys.path.insert(0,'src/engineeringos')
from protected_work_inventory import inspect
from protected_work_repair_candidate import prepare,ProtectedRepairError
from coding_agent_provider import TaskEnvelope,AgentCandidate

def run(*a,cwd=None):return subprocess.check_output(a,cwd=cwd,text=True).strip()

class Good:
 name='fixture-repair'
 def propose(self,*,task,files):
  assert files['protected.txt']=='bad\n'
  return AgentCandidate(provider=self.name,model='fixture',changes={'protected.txt':'good\n'},confidence=1.0,rationale='repair protected file')

with tempfile.TemporaryDirectory() as td:
 root=pathlib.Path(td);repo=root/'repo';repo.mkdir()
 run('git','init','-q',cwd=repo);run('git','config','user.email','t@example.com',cwd=repo);run('git','config','user.name','T',cwd=repo)
 (repo/'base.txt').write_text('old\n');(repo/'protected.txt').write_text('p0\n');run('git','add','base.txt','protected.txt',cwd=repo);run('git','commit','-qm','base',cwd=repo);sha=run('git','rev-parse','HEAD',cwd=repo)
 (repo/'protected.txt').write_text('bad\n');inv=inspect(repo)
 deferred={'state':'VERIFIED_DEFERRED_CANDIDATE','source_sha':sha,'item_id':'base-fix','changed_paths':['base.txt'],'diff_sha256':'x','patch':'''diff --git a/base.txt b/base.txt
index 3367afd..3e75765 100644
--- a/base.txt
+++ b/base.txt
@@ -1 +1 @@
-old
+new
'''}
 task=TaskEnvelope(project='P',item_id='repair-1',source_sha=sha,goal='repair protected file',allowed_paths=('protected.txt',),verification_argv=(sys.executable,'-c',"assert open('base.txt').read()=='new\\n';assert open('protected.txt').read()=='good\\n'"),context={'failure':'fixture'})
 before=run('git','status','--porcelain=v1','--branch',cwd=repo)
 out=prepare(repo,inv,deferred,task,Good(),verification_timeout=20)
 after=run('git','status','--porcelain=v1','--branch',cwd=repo)
 assert out['state']=='VERIFIED_PROTECTED_REPAIR_CANDIDATE' and out['convergence_authorized'] is False and before==after
 assert out['changes']['protected.txt']=='good\n' and out['composed_verification']['state']=='PASS'
 assert out['prior_repair_paths']==[] and out['combined_repair_paths']==['protected.txt']
 badtask=TaskEnvelope(project='P',item_id='repair-2',source_sha=sha,goal='bad surface',allowed_paths=('outside.txt',),verification_argv=(sys.executable,'-c','print(1)'),context={})
 try:prepare(repo,inv,deferred,badtask,Good(),verification_timeout=20);raise AssertionError()
 except ProtectedRepairError as e:assert str(e)=='ALLOWED_PATH_OUTSIDE_PROTECTED_WORK'
print('7 protected-work-repair-candidate invariants passed')
