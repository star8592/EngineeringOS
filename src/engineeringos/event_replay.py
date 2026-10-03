from __future__ import annotations

class ReplayError(ValueError): pass

def replay(events):
    state={}
    expected=1
    seen_ids=set()
    for e in events:
        seq=e['seq']; eid=e['event_id']; typ=e['type']; p=e.get('payload') or {}
        if eid in seen_ids: raise ReplayError('DUPLICATE_EVENT_ID')
        if seq!=expected: raise ReplayError('SEQUENCE_GAP_OR_REORDER')
        seen_ids.add(eid); expected+=1
        if typ=='WORK_DISCOVERED':
            if state: raise ReplayError('WORK_ALREADY_EXISTS')
            state={'id':p['id'],'state':'DISCOVERED','owner':None,'lease':None,'closure_evidence_refs':[],'resolution_evidence_refs':[],'resolved_by':None}
        elif not state:
            raise ReplayError('WORK_NOT_CREATED')
        elif typ=='LEASE_CLAIMED':
            state['state']='IN_PROGRESS'; state['owner']=p['owner']; state['lease']={'owner':p['owner'],'acquired_at':p['acquired_at'],'expires_at':p['expires_at']}
        elif typ=='LEASE_RENEWED':
            if not state.get('lease') or state['lease']['owner']!=p['owner']: raise ReplayError('LEASE_NOT_OWNED')
            state['lease']['expires_at']=p['expires_at']
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
