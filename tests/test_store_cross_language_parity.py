import json,pathlib,subprocess,sys,tempfile
sys.path.insert(0,'src/engineeringos')
from event_store import append_event_cas,read_events,write_snapshot,read_snapshot,state_digest
BIN=['cargo','run','--quiet','--manifest-path','rust/eos-core/Cargo.toml','--bin','store_parity','--']

def rust(*args): return subprocess.check_output(BIN+list(args),text=True).strip()

with tempfile.TemporaryDirectory() as d:
    d=pathlib.Path(d); p=d/'events.jsonl'; s=d/'snap.json'
    e1={'seq':1,'event_id':'e1','type':'WORK_DISCOVERED','payload':{'id':'w1'}}
    append_event_cas(p,e1,0)
    assert json.loads(rust('read',str(p)))==[e1]

    e2={'seq':2,'event_id':'e2','type':'LEASE_CLAIMED','payload':{'owner':'a','acquired_at':'t0','expires_at':'t1'}}
    assert rust('append',str(p),'1',json.dumps(e2,separators=(',',':')))=='OK'
    assert read_events(p)==[e1,e2]

    state={'id':'w1','state':'IN_PROGRESS','owner':'a','lease':{'owner':'a','acquired_at':'t0','expires_at':'t1'}}
    py=write_snapshot(s,2,state); rs=json.loads(rust('snapshot-read',str(s)))
    assert rs['last_seq']==2 and rs['state']==state and rs['state_sha256']==py['state_sha256']==state_digest(state)

    s2=d/'snap-rust.json'; rbody=json.loads(rust('snapshot-write',str(s2),'2',json.dumps(state,separators=(',',':')))); pbody=read_snapshot(s2)
    assert pbody==rbody and pbody['state_sha256']==state_digest(state)

    with open(p,'ab') as f:f.write(b'{"seq":3,"event_id":"partial"')
    assert read_events(p)==[e1,e2] and json.loads(rust('read',str(p)))==[e1,e2]

    # Cross-language race: Python process and Rust process both believe version=2.
    p2=d/'race.jsonl'; append_event_cas(p2,e1,0); append_event_cas(p2,e2,1)
    ev_py={'seq':3,'event_id':'e3p','type':'WORK_REOPENED','payload':{}}
    ev_rs={'seq':3,'event_id':'e3r','type':'WORK_REOPENED','payload':{}}
    pycode=("import sys,json;sys.path.insert(0,'src/engineeringos');from event_store import append_event_cas;"
            "p=sys.argv[1];e=json.loads(sys.argv[2]);"
            "\ntry:\n append_event_cas(p,e,2);print('OK')\nexcept Exception as x:\n print(str(x));raise SystemExit(3)")
    a=subprocess.Popen([sys.executable,'-c',pycode,str(p2),json.dumps(ev_py,separators=(',',':'))],cwd='.',text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    b=subprocess.Popen(BIN+['append',str(p2),'2',json.dumps(ev_rs,separators=(',',':'))],cwd='.',text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    ao,ae=a.communicate(); bo,be=b.communicate()
    results=sorted([(a.returncode,(ao+ae).strip()),(b.returncode,(bo+be).strip())])
    oks=sum(code==0 and 'OK' in text for code,text in results)
    conflicts=sum(code==3 and 'VERSION_CONFLICT' in text for code,text in results)
    assert oks==1 and conflicts==1, results
    assert len(read_events(p2))==3
print('8 storage Python↔Rust/concurrency parity assertions passed')
