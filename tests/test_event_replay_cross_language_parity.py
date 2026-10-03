import sys,json,subprocess
sys.path.insert(0,'src/engineeringos')
from event_replay import replay
E=[
 {'seq':1,'event_id':'e1','type':'WORK_DISCOVERED','payload':{'id':'w1'}},
 {'seq':2,'event_id':'e2','type':'LEASE_CLAIMED','payload':{'owner':'a','acquired_at':'2026-10-03T00:00:00+00:00','expires_at':'2026-10-03T00:01:00+00:00'}},
 {'seq':3,'event_id':'e3','type':'LEASE_RENEWED','payload':{'owner':'a','expires_at':'2026-10-03T00:02:00+00:00'}},
 {'seq':4,'event_id':'e4','type':'RESOLUTION_REQUESTED','payload':{'evidence_refs':['ci:1']}},
 {'seq':5,'event_id':'e5','type':'WORK_RESOLVED','payload':{'verifier':'manager','evidence_refs':['runtime:2']}},
]
py=replay(E)
r=subprocess.run(['cargo','run','--quiet','--manifest-path','rust/eos-core/Cargo.toml','--bin','event_replay_parity'],input=json.dumps(E),text=True,capture_output=True,check=True)
rs=json.loads(r.stdout)
for k in ('id','state','owner','lease','closure_evidence_refs','resolution_evidence_refs','resolved_by'): assert py.get(k)==rs.get(k),(k,py.get(k),rs.get(k))
print('7 event-replay Python↔Rust parity assertions passed')
