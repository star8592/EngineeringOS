from __future__ import annotations
from dataclasses import dataclass,asdict

TERMINAL={'SUCCEEDED','FAILED','CANCELLED'}
NONTERMINAL={'PLANNED','DISPATCHED','ACCEPTED','RUNNING','LOST_CONTACT','UNKNOWN_COMPLETION'}
ALL=TERMINAL|NONTERMINAL

class ExecutionError(ValueError): pass

@dataclass
class ExecutionReceipt:
    execution_id:str
    idempotency_key:str
    action_kind:str
    state:str='PLANNED'
    side_effecting:bool=True
    evidence_refs:list[str]|None=None
    last_transport_state:str|None=None

    def __post_init__(self):
        if self.state not in ALL: raise ExecutionError('UNKNOWN_EXECUTION_STATE')
        if self.evidence_refs is None:self.evidence_refs=[]

TRANSITIONS={
 'PLANNED':{'DISPATCHED','CANCELLED'},
 'DISPATCHED':{'ACCEPTED','FAILED','LOST_CONTACT'},
 'ACCEPTED':{'RUNNING','SUCCEEDED','FAILED','LOST_CONTACT','UNKNOWN_COMPLETION'},
 'RUNNING':{'SUCCEEDED','FAILED','LOST_CONTACT','UNKNOWN_COMPLETION'},
 'LOST_CONTACT':{'SUCCEEDED','FAILED','UNKNOWN_COMPLETION'},
 'UNKNOWN_COMPLETION':{'SUCCEEDED','FAILED'},
}

def transition(r:ExecutionReceipt,new_state:str,evidence_refs=(),transport_state=None):
    if new_state not in ALL: raise ExecutionError('UNKNOWN_EXECUTION_STATE')
    if r.state in TERMINAL: raise ExecutionError('TERMINAL_EXECUTION')
    if new_state not in TRANSITIONS.get(r.state,set()): raise ExecutionError('INVALID_EXECUTION_TRANSITION')
    refs=list(evidence_refs)
    if new_state=='SUCCEEDED' and not (r.evidence_refs or refs): raise ExecutionError('SUCCESS_EVIDENCE_REQUIRED')
    # Validate the entire transition before mutating durable state.
    r.state=new_state
    for ref in refs:
        if ref not in r.evidence_refs:r.evidence_refs.append(ref)
    if transport_state is not None:r.last_transport_state=transport_state
    return r

def retry_decision(r:ExecutionReceipt, outcome_probe=None):
    if not r.side_effecting:
        return 'RETRY_ALLOWED'
    if r.state in {'PLANNED','FAILED','CANCELLED'}:
        return 'RETRY_ALLOWED'
    if r.state=='SUCCEEDED':
        return 'DO_NOT_RETRY'
    # Once a side-effecting action may have crossed the execution boundary,
    # absence of completion evidence is not permission to repeat it.
    if outcome_probe=='PROVEN_NOT_APPLIED':
        return 'RETRY_ALLOWED'
    if outcome_probe=='PROVEN_APPLIED':
        return 'DO_NOT_RETRY'
    return 'PROBE_REQUIRED'
