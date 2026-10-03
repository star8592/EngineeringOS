from __future__ import annotations
from datetime import datetime,timezone
from dependency_graph import readiness

def lease_active(item, now=None):
    now=now or datetime.now(timezone.utc); l=item.get('lease')
    if not l:return False
    return datetime.fromisoformat(l['expires_at'])>now

def schedule(items):
    by={x['id']:x for x in items}; out=[]
    for x in items:
        r=readiness(x,by)
        if r['state']!='READY':
            out.append({'id':x['id'],'schedule_state':r['state'],'blocked_by':r.get('blocked_by',[])})
            continue
        if lease_active(x): out.append({'id':x['id'],'schedule_state':'LEASED','blocked_by':[]}); continue
        automation=x.get('automation','REVIEW'); assurance=x.get('required_assurance','A1')
        if automation=='BLOCK_UNTIL_RESOLVED': lane='POLICY_GATE'
        elif assurance in ('A3','A4','A5'): lane='FORMAL_OR_HIGH_ASSURANCE'
        elif automation=='DETERMINISTIC': lane='DETERMINISTIC'
        else: lane='REASONING_REVIEW'
        out.append({'id':x['id'],'schedule_state':'DISPATCHABLE','lane':lane,'required_assurance':assurance})
    return out
