import pathlib,subprocess,sys,tempfile
sys.path.insert(0,'src/engineeringos')
from protected_work_inventory import inspect
from protected_work_composed_verifier import verify_composed,ProtectedCompositionError

def run(*a,cwd=None):return subprocess.check_output(a,cwd=cwd,text=True).strip()

with tempfile.TemporaryDirectory() as td:
 root=pathlib.Path(td);repo=root/'repo';repo.mkdir()
 run('git','init','-q',cwd=repo);run('git','config','user.email','t@example.com',cwd=repo);run('git','config','user.name','T',cwd=repo)
 (repo/'base.txt').write_text('old\n');(repo/'protected.txt').write_text('p0\n');run('git','add','. ',cwd=repo) if False else None
 run('git','add','base.txt','protected.txt',cwd=repo);run('git','commit','-qm','base',cwd=repo);sha=run('git','rev-parse','HEAD',cwd=repo)
 (repo/'protected.txt').write_text('p1\n');inv=inspect(repo)
 patch='''diff --git a/base.txt b/base.txt
index 3367afd..3e75765 100644
--- a/base.txt
+++ b/base.txt
@@ -1 +1 @@
-old
+new
'''
 cand={'state':'VERIFIED_DEFERRED_CANDIDATE','source_sha':sha,'item_id':'c1','changed_paths':['base.txt'],'diff_sha256':'x','patch':patch}
 before=run('git','status','--porcelain=v1','--branch',cwd=repo)
 out=verify_composed(repo,inv,cand,[sys.executable,'-c',"assert open('base.txt').read()=='new\\n';assert open('protected.txt').read()=='p1\\n'"],timeout_seconds=20)
 after=run('git','status','--porcelain=v1','--branch',cwd=repo)
 assert out['state']=='PASS' and out['source_unchanged'] and before==after and out['protected_path_count']==1
 bad={**cand,'changed_paths':['protected.txt']}
 try:verify_composed(repo,inv,bad,[sys.executable,'-c','print(1)'],timeout_seconds=20);raise AssertionError()
 except ProtectedCompositionError as e:assert str(e).startswith('CANDIDATE_PROTECTED_PATH_OVERLAP:')
 stale={**cand,'source_sha':'deadbeef'}
 try:verify_composed(repo,inv,stale,[sys.executable,'-c','print(1)'],timeout_seconds=20);raise AssertionError()
 except ProtectedCompositionError as e:assert str(e)=='SOURCE_SHA_DRIFT'
 fail=verify_composed(repo,inv,cand,[sys.executable,'-c','import sys;sys.exit(9)'],timeout_seconds=20)
 assert fail['state']=='FAIL' and fail['exit_code']==9 and fail['source_unchanged']
print('9 protected-work-composed-verifier invariants passed')
