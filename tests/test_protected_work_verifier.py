import pathlib,subprocess,sys,tempfile
sys.path.insert(0,'src/engineeringos')
from protected_work_inventory import inspect
from protected_work_verifier import verify,ProtectedVerificationError

def run(*a,cwd=None):return subprocess.check_output(a,cwd=cwd,text=True).strip()

with tempfile.TemporaryDirectory() as td:
 root=pathlib.Path(td);repo=root/'repo';repo.mkdir()
 run('git','init','-q',cwd=repo);run('git','config','user.email','t@example.com',cwd=repo);run('git','config','user.name','T',cwd=repo)
 (repo/'x.txt').write_text('old\n');run('git','add','x.txt',cwd=repo);run('git','commit','-qm','base',cwd=repo)
 (repo/'x.txt').write_text('new\n');inv=inspect(repo)
 before=run('git','status','--porcelain=v1','--branch',cwd=repo)
 ok=verify(repo,inv,[sys.executable,'-c',"assert open('x.txt').read()=='new\\n'"],timeout_seconds=20)
 after=run('git','status','--porcelain=v1','--branch',cwd=repo)
 assert ok['state']=='PASS' and ok['source_unchanged'] and ok['exit_code']==0 and before==after
 bad=verify(repo,inv,[sys.executable,'-c',"import sys;sys.exit(7)"],timeout_seconds=20)
 assert bad['state']=='FAIL' and bad['exit_code']==7 and bad['source_unchanged'] and bad['diagnostic_signature'] is not None
 (repo/'.env.local').write_text('SECRET=x\n');sensitive=inspect(repo)
 try:verify(repo,sensitive,[sys.executable,'-c','print(1)'],timeout_seconds=20);raise AssertionError()
 except ProtectedVerificationError as e:assert str(e)=='SENSITIVE_DIRTY_PATH_BLOCKED'
 (repo/'.env.local').unlink()
 stale=inspect(repo);run('git','add','x.txt',cwd=repo);run('git','commit','-qm','advance',cwd=repo)
 try:verify(repo,stale,[sys.executable,'-c','print(1)'],timeout_seconds=20);raise AssertionError()
 except ProtectedVerificationError as e:assert str(e)=='INVENTORY_SOURCE_SHA_DRIFT'
print('11 protected-work-verifier invariants passed')
