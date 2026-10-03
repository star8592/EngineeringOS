import sys;sys.path.insert(0,'src/engineeringos')
from event_replay import replay,ReplayError
E=[
 {'seq':1,'event_id':'e1','type':'WORK_DISCOVERED','payload':{'id':'w1'}},
 {'seq':2,'event_id':'e2','type':'LEASE_CLAIMED','payload':{'owner':'a','acquired_at':'2026-10-03T00:00:00+00:00','expires_at':'2026-10-03T00:01:00+00:00'}},
 {'seq':3,'event_id':'e3','type':'LEASE_RENEWED','payload':{'owner':'a','expires_at':'2026-10-03T00:02:00+00:00'}},
 {'seq':4,'event_id':'e4','type':'RESOLUTION_REQUESTED','payload':{'evidence_refs':['ci:1']}},
 {'seq':5,'event_id':'e5','type':'WORK_RESOLVED','payload':{'verifier':'manager','evidence_refs':['runtime:2']}},
]
x=replay(E); assert x['state']=='RESOLVED' and x['lease'] is None and x['resolution_evidence_refs']==['ci:1','runtime:2']
for bad,msg in [([E[0],E[2]],'SEQUENCE_GAP_OR_REORDER'),([E[0],dict(E[1],event_id='e1')],'DUPLICATE_EVENT_ID')]:
 try: replay(bad); raise AssertionError(msg)
 except ReplayError as e: assert str(e)==msg
assert replay(E+[{'seq':6,'event_id':'e6','type':'WORK_REOPENED','payload':{}}])['state']=='REOPENED'
print('4 replay invariants passed')
