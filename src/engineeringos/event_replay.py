from __future__ import annotations

class ReplayError(ValueError): pass

def _apply(state,e):
    typ=e['type']; p=e.get('payload') or {}
    if typ=='WORK_DISCOVERED':
        if state: raise ReplayError('WORK_ALREADY_EXISTS')
        return {'id':p['id'],'state':'DISCOVERED','owner':None,'lease':None,'closure_evidence_refs':[],'resolution_evidence_refs':[],'resolved_by':None}
    if not state: raise ReplayError('WORK_NOT_CREATED')
    state=dict(state)
    if typ=='LEASE_CLAIMED':
        state['state']='IN_PROGRESS'; state['owner']=p['owner']; state['lease']={'owner':p['owner'],'acquired_at':p['acquired_at'],'expires_at':p['expires_at']}
    elif typ=='LEASE_RENEWED':
        if not state.get('lease') or state['lease']['owner']!=p['owner']: raise ReplayError('LEASE_NOT_OWNED')
        state['lease']=dict(state['lease']); state['lease']['expires_at']=p['expires_at']
    elif typ=='RESOLUTION_REQUESTED':
        if not p.get('evidence_refs'): raise ReplayError('EVIDENCE_REQUIRED')
        state['state']='PENDING_RESOLUTION'; state['closure_evidence_refs']=list(p['evidence_refs'])
    elif typ=='WORK_RESOLVED':
        refs=list(dict.fromkeys(state.get('closure_evidence_refs',[])+list(p.get('evidence_refs') or [])))
        if not refs: raise ReplayError('EVIDENCE_REQUIRED')
        state['state']='RESOLVED'; state['resolved_by']=p['verifier']; state['resolution_evidence_refs']=refs; state['lease']=None
    elif typ=='WORK_REOPENED':
        state['state']='REOPENED'; state['resolved_by']=None; state['resolution_evidence_refs']=[]
    else: raise ReplayError('UNKNOWN_EVENT_TYPE')
    return state

def replay_from(base_state,last_seq,events,seen_event_ids=None):
    state=dict(base_state or {}); expected=last_seq+1; seen_ids=set(seen_event_ids or [])
    for e in events:
        seq=e['seq']; eid=e['event_id']
        if eid in seen_ids: raise ReplayError('DUPLICATE_EVENT_ID')
        if seq!=expected: raise ReplayError('SEQUENCE_GAP_OR_REORDER')
        seen_ids.add(eid); expected+=1; state=_apply(state,e)
    return state

def replay(events):
    return replay_from({},0,events)
