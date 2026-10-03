import sys,tempfile,pathlib,json,os
sys.path.insert(0,'src/engineeringos')
from dashboard_projector import atomic_copy_json
with tempfile.TemporaryDirectory() as d:
 d=pathlib.Path(d);a=d/'a.json';b=d/'nested'/'b.json';a.write_text(json.dumps({'x':1}))
 x=atomic_copy_json(a,b);assert x=={'x':1} and json.load(open(b))=={'x':1}
 assert not list(b.parent.glob('*.tmp'))
print('2 dashboard-projector invariants passed')
