#!/usr/bin/env python3
from __future__ import annotations
import json,pathlib,hashlib,tempfile,os
from command_processor import Command,record_intent,append_command_event,replay_command
from event_store import read_events,current_version


def _atomic_json(path,obj):
    p=pathlib.Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(obj,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode()
    fd,tmp=tempfile.mkstemp(prefix=p.name+'.',suffix='.tmp',dir=p.parent)
    try:
        with os.fdopen(fd,'wb') as f:
            f.write(raw);f.flush();os.fsync(f.fileno())
        os.replace(tmp,p)
        dfd=os.open(p.parent,os.O_DIRECTORY)
        try:os.fsync(dfd)
        finally:os.close(dfd)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
    return hashlib.sha256(raw).hexdigest()


def shadow_policy(item,schedule_decision):
    if schedule_decision.get('schedule_state')!='DISPATCHABLE':
        return {'decision':'DENY','reason':'NOT_DISPATCHABLE'}
    return {'decision':'ALLOW','reason':'SHADOW_EVALUATION_ONLY','target_mutation_authorized':False}


def _ids(snapshot_hash,item_id):
    base=f'shadow|{snapshot_hash}|{item_id}'
    h=hashlib.sha256(base.encode()).hexdigest()
    return h[:24],f'shadow:{snapshot_hash}:{item_id}'


def _execute_shadow(evidence_path,*,item,schedule_decision,policy,snapshot_hash,command_id):
    body={
      'schema_version':1,'command_id':command_id,'mode':'SHADOW',
      'target_mutation_authorized':False,'snapshot_content_sha256':snapshot_hash,
      'work_item':item,'schedule_decision':schedule_decision,'policy':policy,
    }
    digest=_atomic_json(evidence_path,body)
    return f'file:{evidence_path}#sha256:{digest}'


def run_loop(*,queue_path,dispatch_path,snapshot_path,event_path,evidence_dir,projection_path):
    queue=json.load(open(queue_path));dispatch=json.load(open(dispatch_path));snap=json.load(open(snapshot_path))
    by_item={x['id']:x for x in queue['items']};snapshot_hash=snap['content_sha256'];rows=[]
    for sd in dispatch['items']:
        item=by_item[sd['id']];policy=shadow_policy(item,sd)
        row={'item_id':item['id'],'kind':item['kind'],'schedule_state':sd['schedule_state'],'policy':policy['decision'],'command_state':None,'evidence_refs':[],'target_mutation_authorized':False}
        if policy['decision']!='ALLOW':rows.append(row);continue
        command_id,idem=_ids(snapshot_hash,item['id'])
        cmd=Command(command_id=command_id,idempotency_key=idem,action_kind=f"SHADOW_EVALUATE:{item['kind']}",side_effecting=False,policy_decision='ALLOW')
        events=read_events(event_path);state=replay_command(events,command_id)
        if state is None:
            record_intent(event_path,cmd,current_version(event_path));state=replay_command(read_events(event_path),command_id)
        if state['state']=='INTENT_RECORDED':
            append_command_event(event_path,cmd,'COMMAND_DISPATCHED',expected_version=current_version(event_path));state=replay_command(read_events(event_path),command_id)
        evidence_path=pathlib.Path(evidence_dir)/f'{command_id}.json'
        if state['state']=='DISPATCHED':
            # Local deterministic shadow execution is safe to replay after a crash.
            ref=_execute_shadow(evidence_path,item=item,schedule_decision=sd,policy=policy,snapshot_hash=snapshot_hash,command_id=command_id)
            append_command_event(event_path,cmd,'COMMAND_EFFECT_CONFIRMED',{'evidence_refs':[ref]},expected_version=current_version(event_path));state=replay_command(read_events(event_path),command_id)
        row.update({'command_id':command_id,'command_state':state['state'],'attempts':state['attempts'],'evidence_refs':state['evidence_refs']})
        rows.append(row)
    projection={
      'schema_version':1,'mode':'SHADOW','target':snap['target'],'snapshot_content_sha256':snapshot_hash,
      'target_mutation_authorized':False,'items':rows,
      'summary':{'items':len(rows),'succeeded':sum(x.get('command_state')=='SUCCEEDED' for x in rows),'blocked':sum(x['policy']=='DENY' for x in rows)},
    }
    _atomic_json(projection_path,projection)
    return projection


def main():
    out=run_loop(queue_path='.engineeringos/work-queue.json',dispatch_path='artifacts/dispatch-plan.json',snapshot_path='.engineeringos/shadow/latest.json',event_path='.engineeringos/control-loop/events.jsonl',evidence_dir='.engineeringos/control-loop/evidence',projection_path='.engineeringos/control-loop/projection.json')
    print(json.dumps(out,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
