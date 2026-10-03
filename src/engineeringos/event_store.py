from __future__ import annotations
import json,os,pathlib,fcntl,tempfile,hashlib

class EventStoreError(ValueError): pass

def _decode_complete_lines(data: bytes):
    events=[]; lines=data.splitlines(keepends=True)
    for i,line in enumerate(lines):
        complete=line.endswith(b'\n') or line.endswith(b'\r')
        if not complete and i==len(lines)-1: break
        raw=line.strip()
        if not raw: continue
        try: events.append(json.loads(raw))
        except json.JSONDecodeError as e: raise EventStoreError('CORRUPT_COMPLETE_RECORD') from e
    return events

def read_events(path):
    p=pathlib.Path(path)
    if not p.exists(): return []
    return _decode_complete_lines(p.read_bytes())

def _append_locked(f,event,expected_version=None):
    f.seek(0); events=_decode_complete_lines(f.read()); current=(events[-1]['seq'] if events else 0)
    if expected_version is not None and expected_version!=current: raise EventStoreError('VERSION_CONFLICT')
    expected=current+1
    if event.get('seq')!=expected: raise EventStoreError('SEQUENCE_MISMATCH')
    if any(x.get('event_id')==event.get('event_id') for x in events): raise EventStoreError('DUPLICATE_EVENT_ID')
    f.seek(0,os.SEEK_END); payload=(json.dumps(event,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode(); f.write(payload); os.fsync(f.fileno())
    return event

def append_event(path,event):
    return append_event_cas(path,event,None)

def append_event_cas(path,event,expected_version):
    p=pathlib.Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    with open(p,'a+b',buffering=0) as f:
        fcntl.flock(f.fileno(),fcntl.LOCK_EX)
        try:return _append_locked(f,event,expected_version)
        finally:fcntl.flock(f.fileno(),fcntl.LOCK_UN)

def current_version(path):
    events=read_events(path); return events[-1]['seq'] if events else 0

def state_digest(state):
    raw=json.dumps(state,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode(); return hashlib.sha256(raw).hexdigest()

def write_snapshot(path,last_seq,state):
    p=pathlib.Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    body={'schema_version':1,'last_seq':last_seq,'state':state,'state_sha256':state_digest(state)}
    fd,tmp=tempfile.mkstemp(prefix=p.name+'.',suffix='.tmp',dir=p.parent)
    try:
        with os.fdopen(fd,'w') as f: json.dump(body,f,sort_keys=True,separators=(',',':'),ensure_ascii=False); f.write('\n'); f.flush(); os.fsync(f.fileno())
        os.replace(tmp,p)
        dfd=os.open(p.parent,os.O_DIRECTORY)
        try: os.fsync(dfd)
        finally: os.close(dfd)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
    return body

def read_snapshot(path):
    p=pathlib.Path(path)
    if not p.exists(): return None
    try: body=json.loads(p.read_text())
    except json.JSONDecodeError as e: raise EventStoreError('CORRUPT_SNAPSHOT') from e
    if body.get('schema_version')!=1: raise EventStoreError('UNSUPPORTED_SNAPSHOT_SCHEMA')
    if body.get('state_sha256')!=state_digest(body.get('state')): raise EventStoreError('SNAPSHOT_DIGEST_MISMATCH')
    return body
