from __future__ import annotations
import hashlib,datetime as dt
from event_store import append_event_cas,current_version,read_events

class ProjectJournalError(ValueError): pass
def _eid(project,typ,key,generation,payload):
 raw=f"{project}|{typ}|{key}|{generation}|{repr(sorted(payload.items()))}"
 return hashlib.sha256(raw.encode()).hexdigest()[:24]
def append(path,*,project,typ,key,payload,generation=0,expected_version=None):
 v=current_version(path) if expected_version is None else expected_version
 e={"schema_version":1,"seq":v+1,"event_id":_eid(project,typ,key,generation,payload),"project":project,"type":typ,
    "key":key,"generation":generation,"observed_at":dt.datetime.now(dt.timezone.utc).isoformat(),"payload":payload}
 return append_event_cas(path,e,v)
def events(path,project=None):
 rows=read_events(path)
 return [e for e in rows if project is None or e.get("project")==project]
