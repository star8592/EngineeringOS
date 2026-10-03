from __future__ import annotations
from datetime import datetime, timezone, timedelta

def utcnow(): return datetime.now(timezone.utc)
def parse(t): return datetime.fromisoformat(t) if t else None

def claim(item, owner, lease_seconds=1800, now=None):
    now=now or utcnow(); cur=item.get('lease')
    if cur and parse(cur.get('expires_at'))>now and cur.get('owner')!=owner:
        raise ValueError('LEASE_HELD')
    item['owner']=owner; item['state']='IN_PROGRESS'
    item['lease']={'owner':owner,'acquired_at':now.isoformat(),'expires_at':(now+timedelta(seconds=lease_seconds)).isoformat()}
    return item

def renew(item, owner, lease_seconds=1800, now=None):
    now=now or utcnow(); cur=item.get('lease') or {}
    if cur.get('owner')!=owner or parse(cur.get('expires_at'))<=now: raise ValueError('LEASE_NOT_OWNED')
    cur['expires_at']=(now+timedelta(seconds=lease_seconds)).isoformat(); item['lease']=cur; return item

def request_resolution(item, owner, evidence_refs):
    if (item.get('lease') or {}).get('owner')!=owner: raise ValueError('LEASE_NOT_OWNED')
    if not evidence_refs: raise ValueError('EVIDENCE_REQUIRED')
    item['state']='PENDING_RESOLUTION'; item['closure_evidence_refs']=list(evidence_refs); return item

def resolve(item, verifier, evidence_refs):
    if item.get('state')!='PENDING_RESOLUTION': raise ValueError('NOT_PENDING_RESOLUTION')
    refs=list(dict.fromkeys((item.get('closure_evidence_refs') or [])+list(evidence_refs or [])))
    if not refs: raise ValueError('EVIDENCE_REQUIRED')
    item['state']='RESOLVED'; item['resolved_by']=verifier; item['resolution_evidence_refs']=refs; item.pop('lease',None); return item
