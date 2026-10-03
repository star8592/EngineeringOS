import sys; sys.path.insert(0,'src/engineeringos')
from queue_model import *
from datetime import datetime,timezone,timedelta
n=datetime(2026,10,3,tzinfo=timezone.utc)
a={'state':'DISCOVERED'}; claim(a,'agent-a',60,n)
try: claim(a,'agent-b',60,n); raise AssertionError('double claim allowed')
except ValueError as e: assert str(e)=='LEASE_HELD'
claim(a,'agent-b',60,n+timedelta(seconds=61)); assert a['owner']=='agent-b'
try: request_resolution(a,'agent-b',[]); raise AssertionError('closed without evidence')
except ValueError as e: assert str(e)=='EVIDENCE_REQUIRED'
request_resolution(a,'agent-b',['ci:123']); resolve(a,'manager',['runtime:456']); assert a['state']=='RESOLVED' and 'lease' not in a
print('4 lease/closure invariants passed')
