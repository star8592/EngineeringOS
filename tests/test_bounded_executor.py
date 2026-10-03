import json,pathlib,tempfile,subprocess,sys,os
sys.path.insert(0,'src/engineeringos')
from bounded_executor import execute,BoundedExecutionError
with tempfile.TemporaryDirectory() as d:
 d=pathlib.Path(d);repo=d/'repo';repo.mkdir();subprocess.check_call(['git','init','-q','-b','main'],cwd=repo);subprocess.check_call(['git','config','user.email','test@example.com'],cwd=repo);subprocess.check_call(['git','config','user.name','Test'],cwd=repo)
 (repo/'check.sh').write_text('#!/bin/sh\ntest ! -e MUTATED && echo CHECK_OK\n');os.chmod(repo/'check.sh',0o755);subprocess.check_call(['git','add','.'],cwd=repo);subprocess.check_call(['git','commit','-qm','init'],cwd=repo)
 q=d/'q.json';dp=d/'dp.json';actions=d/'actions.json';policy=d/'policy.json'
 q.write_text(json.dumps({'items':[{'id':'w','kind':'RESOLVE_MAIN_QUALIFICATION','state':'DISCOVERED'}]}));dp.write_text(json.dumps({'items':[{'id':'w','schedule_state':'DISPATCHABLE'}]}))
 actions.write_text(json.dumps({'schema_version':1,'project':'DevControl','actions':{'x':{'admission_action':'run_deterministic_checks','work_kinds':['RESOLVE_MAIN_QUALIFICATION'],'repository':str(repo),'source_ref':'HEAD','argv':['./check.sh'],'timeout_seconds':10,'target_mutation':False,'snapshot_mode':'git_archive'}}}))
 policy.write_text(json.dumps({'schema_version':1,'project':'DevControl','execution_backend':'DevControl','approval_authority':'HOST_PROTOCOL','actions':{'run_deterministic_checks':{'g3_allowed':True,'side_effecting':False,'destructive':False,'idempotent':True,'reversible':True,'approval_mode':'AUTO'}}}))
 import bounded_executor as b;b.STATE=d/'state'
 out=execute(item_id='w',queue_path=q,dispatch_path=dp,policy_path=policy,actions_path=actions);assert out['check_result']=='PASS' and out['target_mutation_authorized'] is False
 assert not (repo/'MUTATED').exists();first=(d/'state/events.jsonl').read_text().count('\n');out2=execute(item_id='w',queue_path=q,dispatch_path=dp,policy_path=policy,actions_path=actions);assert (d/'state/events.jsonl').read_text().count('\n')==first
 bad=json.loads(actions.read_text());bad['actions']['x']['target_mutation']=True;actions.write_text(json.dumps(bad))
 try: execute(item_id='w',queue_path=q,dispatch_path=dp,policy_path=policy,actions_path=actions);raise AssertionError('unsafe spec accepted')
 except BoundedExecutionError as e: assert 'UNSAFE_ACTION_SPEC' in str(e)
print('7 bounded-executor invariants passed')
