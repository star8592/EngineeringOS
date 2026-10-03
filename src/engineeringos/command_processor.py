from __future__ import annotations
from dataclasses import dataclass, asdict
import uuid
from event_store import append_event_cas, read_events, current_version, EventStoreError

class CommandError(ValueError): pass

@dataclass(frozen=True)
class Command:
    command_id: str
    idempotency_key: str
    action_kind: str
    side_effecting: bool = True
    policy_decision: str = 'ALLOW'


def _event(seq, typ, command: Command, payload=None):
    return {
        'seq': seq,
        'event_id': f'cmd-{command.command_id}-{typ.lower()}-{uuid.uuid4().hex}',
        'type': typ,
        'payload': {
            'command_id': command.command_id,
            'idempotency_key': command.idempotency_key,
            'action_kind': command.action_kind,
            'side_effecting': command.side_effecting,
            **(payload or {}),
        },
    }


def replay_command(events, command_id):
    state = None
    for e in events:
        p=e.get('payload') or {}
        if p.get('command_id') != command_id: continue
        t=e['type']
        if t=='COMMAND_INTENT_RECORDED':
            if state is not None: raise CommandError('COMMAND_ALREADY_EXISTS')
            state={'command_id':command_id,'idempotency_key':p['idempotency_key'],'action_kind':p['action_kind'],'side_effecting':p.get('side_effecting',True),'state':'INTENT_RECORDED','attempts':0,'evidence_refs':[],'outcome':None}
        elif state is None:
            raise CommandError('COMMAND_NOT_FOUND')
        elif t=='COMMAND_DISPATCHED':
            state['state']='DISPATCHED';state['attempts']+=1
        elif t=='COMMAND_COMPLETION_UNKNOWN': state['state']='UNKNOWN_COMPLETION'
        elif t=='COMMAND_EFFECT_CONFIRMED':
            refs=list(dict.fromkeys(state['evidence_refs']+list(p.get('evidence_refs') or [])))
            if not refs: raise CommandError('OUTCOME_EVIDENCE_REQUIRED')
            state['state']='SUCCEEDED';state['outcome']='APPLIED';state['evidence_refs']=refs
        elif t=='COMMAND_EFFECT_NOT_APPLIED':
            refs=list(dict.fromkeys(state['evidence_refs']+list(p.get('evidence_refs') or [])))
            if not refs: raise CommandError('OUTCOME_EVIDENCE_REQUIRED')
            state['state']='NOT_APPLIED';state['outcome']='NOT_APPLIED';state['evidence_refs']=refs
        elif t=='COMMAND_FAILED_PRE_EFFECT': state['state']='FAILED_PRE_EFFECT'
        else: raise CommandError('UNKNOWN_COMMAND_EVENT')
    return state


def _assert_idempotency(events, command:Command):
    for e in events:
        p=e.get('payload') or {}
        if e.get('type')=='COMMAND_INTENT_RECORDED' and p.get('idempotency_key')==command.idempotency_key and p.get('command_id')!=command.command_id:
            raise CommandError('IDEMPOTENCY_KEY_CONFLICT')


def record_intent(path, command:Command, expected_version:int):
    if command.policy_decision!='ALLOW': raise CommandError('POLICY_DENIED')
    events=read_events(path);_assert_idempotency(events,command)
    seq=expected_version+1
    return append_event_cas(path,_event(seq,'COMMAND_INTENT_RECORDED',command),expected_version)


def append_command_event(path,command:Command,typ:str,payload=None,expected_version=None):
    version=current_version(path) if expected_version is None else expected_version
    state=replay_command(read_events(path),command.command_id)
    if state is None: raise CommandError('COMMAND_NOT_FOUND')
    allowed={
      'COMMAND_DISPATCHED': {'INTENT_RECORDED','NOT_APPLIED'},
      'COMMAND_COMPLETION_UNKNOWN': {'DISPATCHED'},
      'COMMAND_EFFECT_CONFIRMED': {'DISPATCHED','UNKNOWN_COMPLETION'},
      'COMMAND_EFFECT_NOT_APPLIED': {'DISPATCHED','UNKNOWN_COMPLETION'},
      'COMMAND_FAILED_PRE_EFFECT': {'INTENT_RECORDED'},
    }
    if state['state'] not in allowed.get(typ,set()): raise CommandError('INVALID_COMMAND_TRANSITION')
    if typ in {'COMMAND_EFFECT_CONFIRMED','COMMAND_EFFECT_NOT_APPLIED'} and not (payload or {}).get('evidence_refs'): raise CommandError('OUTCOME_EVIDENCE_REQUIRED')
    return append_event_cas(path,_event(version+1,typ,command,payload),version)


def retry_decision(state):
    if state is None:return 'NO_COMMAND'
    if not state['side_effecting']:
        return 'RETRY_ALLOWED' if state['state']!='SUCCEEDED' else 'DO_NOT_RETRY'
    if state['state'] in {'INTENT_RECORDED','FAILED_PRE_EFFECT','NOT_APPLIED'}: return 'RETRY_ALLOWED'
    if state['state']=='SUCCEEDED': return 'DO_NOT_RETRY'
    if state['state'] in {'DISPATCHED','UNKNOWN_COMPLETION'}: return 'PROBE_REQUIRED'
    return 'PROBE_REQUIRED'
