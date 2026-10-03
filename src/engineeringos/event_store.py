from __future__ import annotations
import json,os,pathlib,fcntl

class EventStoreError(ValueError): pass

def _decode_complete_lines(data: bytes):
    events=[]
    lines=data.splitlines(keepends=True)
    for i,line in enumerate(lines):
        complete=line.endswith(b'\n') or line.endswith(b'\r')
        if not complete and i==len(lines)-1:
            break  # torn final append: recover durable complete prefix only
        raw=line.strip()
        if not raw: continue
        try: events.append(json.loads(raw))
        except json.JSONDecodeError as e: raise EventStoreError('CORRUPT_COMPLETE_RECORD') from e
    return events

def read_events(path):
    p=pathlib.Path(path)
    if not p.exists(): return []
    return _decode_complete_lines(p.read_bytes())

def append_event(path,event):
    p=pathlib.Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    with open(p,'a+b',buffering=0) as f:
        fcntl.flock(f.fileno(),fcntl.LOCK_EX)
        f.seek(0); events=_decode_complete_lines(f.read())
        expected=(events[-1]['seq']+1) if events else 1
        if event.get('seq')!=expected: raise EventStoreError('SEQUENCE_MISMATCH')
        if any(x.get('event_id')==event.get('event_id') for x in events): raise EventStoreError('DUPLICATE_EVENT_ID')
        f.seek(0,os.SEEK_END)
        payload=(json.dumps(event,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
        f.write(payload); os.fsync(f.fileno())
        fcntl.flock(f.fileno(),fcntl.LOCK_UN)
    return event
