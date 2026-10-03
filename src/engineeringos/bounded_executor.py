#!/usr/bin/env python3
from __future__ import annotations
import argparse,datetime as dt,hashlib,json,os,pathlib,shutil,subprocess,tempfile
from command_processor import Command,record_intent,append_command_event,replay_command
from event_store import read_events,current_version
from g3_admission import load_policy,assess
from state_paths import runtime

ROOT=pathlib.Path(__file__).resolve().parents[2]
STATE=runtime('g3')

class BoundedExecutionError(ValueError): pass

def utcnow(): return dt.datetime.now(dt.timezone.utc).isoformat()
def load_json(path): return json.load(open(path))
def atomic_json(path,obj):
 p=pathlib.Path(path);p.parent.mkdir(parents=True,exist_ok=True)
 raw=(json.dumps(obj,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode()
 fd,tmp=tempfile.mkstemp(prefix=p.name+'.',suffix='.tmp',dir=p.parent)
 try:
  with os.fdopen(fd,'wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
  os.replace(tmp,p)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)
def sha256_json(obj): return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def git(repo,*args): return subprocess.check_output(['git','-C',repo,*args],text=True).strip()
def tail(s,n=12000): return s[-n:]

def resolve_action(work_item,actions):
 matches=[(name,spec) for name,spec in actions['actions'].items() if work_item['kind'] in spec.get('work_kinds',[])]
 if len(matches)!=1: raise BoundedExecutionError('ACTION_MAPPING_NOT_UNIQUE')
 return matches[0]

def execute(*,item_id, queue_path=None, dispatch_path=None, policy_path='project_profiles/devcontrol/g3-tool-policy.json', actions_path='project_profiles/devcontrol/g3-actions.json'):
 queue_path=pathlib.Path(queue_path or runtime('work-queue.json'));dispatch_path=pathlib.Path(dispatch_path or ROOT/'artifacts/dispatch-plan.json')
 queue=load_json(queue_path);dispatch=load_json(dispatch_path);by={x['id']:x for x in queue['items']};sd={x['id']:x for x in dispatch['items']}.get(item_id)
 if item_id not in by: raise BoundedExecutionError('WORK_ITEM_NOT_FOUND')
 item=by[item_id]
 if not sd or sd.get('schedule_state')!='DISPATCHABLE': raise BoundedExecutionError('WORK_ITEM_NOT_DISPATCHABLE')
 actions=load_json(actions_path);name,spec=resolve_action(item,actions);policy=load_policy(policy_path)
 decision=assess(policy,action=spec['admission_action'],backend='DevControl',declared_annotations={'read_only_hint':True},runtime_contracts=())
 if decision['decision']!='ALLOW': raise BoundedExecutionError('G3_ADMISSION_DENIED:'+decision.get('reason','UNKNOWN'))
 if spec.get('target_mutation') is not False or spec.get('snapshot_mode')!='git_archive': raise BoundedExecutionError('UNSAFE_ACTION_SPEC')
 repo=spec['repository'];source_sha=git(repo,'rev-parse',spec['source_ref']);spec_hash=sha256_json(spec)
 command_id=hashlib.sha256(f'g3|{item_id}|{source_sha}|{spec_hash}'.encode()).hexdigest()[:24]
 cmd=Command(command_id=command_id,idempotency_key=f'g3:{item_id}:{source_sha}:{spec_hash}',action_kind=f'G3:{name}',side_effecting=False,policy_decision='ALLOW')
 event_path=STATE/'events.jsonl';events=read_events(event_path);state=replay_command(events,command_id)
 if state and state['state']=='SUCCEEDED':
  ep=STATE/'evidence'/f'{command_id}.json';return load_json(ep)
 if state is None:
  record_intent(event_path,cmd,current_version(event_path));state=replay_command(read_events(event_path),command_id)
 if state['state']=='INTENT_RECORDED':
  append_command_event(event_path,cmd,'COMMAND_DISPATCHED',expected_version=current_version(event_path))
 started=utcnow()
 with tempfile.TemporaryDirectory(prefix='engineeringos-g3-') as td:
  archive=subprocess.Popen(['git','-C',repo,'archive',source_sha],stdout=subprocess.PIPE)
  extract=subprocess.run(['tar','-x','-C',td],stdin=archive.stdout,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  archive.stdout.close();arc_rc=archive.wait()
  if arc_rc or extract.returncode: raise BoundedExecutionError('SNAPSHOT_EXPORT_FAILED')
  try:
   proc=subprocess.run(spec['argv'],cwd=td,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=int(spec['timeout_seconds']),env={**os.environ,'CI':'1'})
   exit_code=proc.returncode;stdout=tail(proc.stdout);stderr=tail(proc.stderr);timed_out=False
  except subprocess.TimeoutExpired as exc:
   exit_code=124;stdout=tail(exc.stdout or '');stderr=tail(exc.stderr or '');timed_out=True
 completed=utcnow();passed=(exit_code==0 and not timed_out)
 evidence={'schema_version':1,'mode':'G3_BOUNDED','project':'DevControl','item_id':item_id,'work_kind':item['kind'],'action':name,'command_id':command_id,'source_ref':spec['source_ref'],'source_sha':source_sha,'action_spec_sha256':spec_hash,'argv':spec['argv'],'snapshot_mode':'git_archive','target_mutation_authorized':False,'started_at':started,'completed_at':completed,'exit_code':exit_code,'timed_out':timed_out,'check_result':'PASS' if passed else 'FAIL','stdout_tail':stdout,'stderr_tail':stderr}
 ep=STATE/'evidence'/f'{command_id}.json';atomic_json(ep,evidence);eref=f'file:{ep}#sha256:{sha256_json(evidence)}'
 append_command_event(event_path,cmd,'COMMAND_EFFECT_CONFIRMED',{'evidence_refs':[eref]},expected_version=current_version(event_path))
 projection={'schema_version':1,'latest':evidence,'evidence_ref':eref,'execution_state':'SUCCEEDED','check_result':evidence['check_result'],'target_mutation_authorized':False};atomic_json(STATE/'projection.json',projection)
 return evidence

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--item-id',required=True);a=ap.parse_args();out=execute(item_id=a.item_id);print(json.dumps(out,indent=2,ensure_ascii=False));return 0 if out['check_result']=='PASS' else 1
if __name__=='__main__': raise SystemExit(main())
