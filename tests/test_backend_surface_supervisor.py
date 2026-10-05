import json,pathlib,sys,tempfile
sys.path.insert(0,'src/engineeringos')
from supervisor import run_backend_surface_lane

with tempfile.TemporaryDirectory() as td:
 root=pathlib.Path(td);state=root/'state';profile=root/'profile.json';profile.write_text(json.dumps({'schema_version':1}))
 calls=[]
 def fake(p,e):
  calls.append((p,e));return {'state':'CONVERGED','reason':'CURRENT','schema_version':1}
 a=run_backend_surface_lane(profile_path=profile,state_root=state,now=1000,refresh_seconds=900,reconcile_fn=fake)
 assert a['state']=='CONVERGED' and a['cached'] is False and len(calls)==1
 f=state/'backends'/'DevControl'/'freshness.json';assert f.exists()
 # Force cache mtime and prove second call does not hit backend.
 import os;os.utime(f,(1000,1000))
 b=run_backend_surface_lane(profile_path=profile,state_root=state,now=1100,refresh_seconds=900,reconcile_fn=lambda *_:(_ for _ in ()).throw(AssertionError()))
 assert b['state']=='CONVERGED' and b['cached'] is True
 c=run_backend_surface_lane(profile_path=root/'missing.json',state_root=state,now=2000,reconcile_fn=fake)
 assert c['state']=='NOT_CONFIGURED'
 def bad(p,e):raise RuntimeError('boom')
 d=run_backend_surface_lane(profile_path=profile,state_root=state,now=3000,refresh_seconds=1,reconcile_fn=bad)
 assert d['health']=='DEGRADED' and d['state']=='MONITOR_FAILED'
 print('8 backend-surface-supervisor invariants passed')
