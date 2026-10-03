import sys,json,subprocess
sys.path.insert(0,'src/engineeringos')
from queue_model import claim,renew,request_resolution,resolve
from datetime import datetime,timezone,timedelta
n=datetime.fromtimestamp(0,timezone.utc);x={'state':'DISCOVERED'}
claim(x,'agent-a',60,n);renew(x,'agent-a',60,n+timedelta(seconds=30));claim(x,'agent-b',60,n+timedelta(seconds=91));request_resolution(x,'agent-b',['ci:123']);resolve(x,'manager',['runtime:456'])
py={'state':x['state'],'owner':x.get('owner'),'lease':x.get('lease'),'resolved_by':x.get('resolved_by'),'resolution_evidence_refs':x.get('resolution_evidence_refs')}
rust=json.loads(subprocess.check_output(['cargo','run','--quiet','--manifest-path','rust/eos-core/Cargo.toml','--bin','parity'],text=True))
assert py['state']==rust['state'];assert py['owner']==rust['owner'];assert py['lease'] is None and rust['lease'] is None
assert py['resolved_by']==rust['resolved_by'];assert py['resolution_evidence_refs']==rust['resolution_evidence_refs']
print('5 Python↔Rust parity assertions passed')
