from __future__ import annotations
import hashlib,datetime as dt
from event_store import append_event_cas,current_version,read_events

class ProjectJournalError(ValueError): pass
def _eid(project,typ,key,generation,payload,sequence,idempotency_key=None):
 raw=(f"{project}|idem|{idempotency_key}" if idempotency_key is not None else f"{project}|{typ}|{key}|{generation}|seq:{sequence}|{repr(sorted(payload.items()))}")
 return hashlib.sha256(raw.encode()).hexdigest()[:24]
def append(path,*,project,typ,key,payload,generation=0,expected_version=None,idempotency_key=None):
 v=current_version(path) if expected_version is None else expected_version;seq=v+1
 e={"schema_version":1,"seq":seq,"event_id":_eid(project,typ,key,generation,payload,seq,idempotency_key),"project":project,"type":typ,
    "key":key,"generation":generation,"observed_at":dt.datetime.now(dt.timezone.utc).isoformat(),"payload":payload}
 return append_event_cas(path,e,v)
def events(path,project=None):
 rows=read_events(path)
 return [e for e in rows if project is None or e.get("project")==project]
