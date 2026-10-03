import sys,json,subprocess
from datetime import datetime,timezone,timedelta
sys.path.insert(0,'src/engineeringos')
from dependency_graph import validate
from scheduler import schedule
NOW=datetime.fromtimestamp(0,timezone.utc)
items=[
 {'id':'done','state':'RESOLVED','depends_on':[],'automation':'REVIEW','required_assurance':'A1'},
 {'id':'det','state':'DISCOVERED','depends_on':['done'],'automation':'DETERMINISTIC','required_assurance':'A1'},
 {'id':'review','state':'REOPENED','depends_on':['done'],'automation':'REVIEW','required_assurance':'A2'},
 {'id':'formal','state':'DISCOVERED','depends_on':[],'automation':'DETERMINISTIC','required_assurance':'A4'},
 {'id':'policy','state':'DISCOVERED','depends_on':[],'automation':'BLOCK_UNTIL_RESOLVED','required_assurance':'A5'},
 {'id':'leased','state':'DISCOVERED','depends_on':[],'automation':'REVIEW','required_assurance':'A1','lease':{'owner':'a','acquired_at':NOW.isoformat(),'expires_at':(NOW+timedelta(seconds=60)).isoformat()}},
 {'id':'blocked','state':'DISCOVERED','depends_on':['open'],'automation':'REVIEW','required_assurance':'A1'},
 {'id':'open','state':'DISCOVERED','depends_on':[],'automation':'REVIEW','required_assurance':'A1'},
 {'id':'missing','state':'DISCOVERED','depends_on':['ghost'],'automation':'REVIEW','required_assurance':'A1'},
 {'id':'c1','state':'DISCOVERED','depends_on':['c2'],'automation':'REVIEW','required_assurance':'A1'},
 {'id':'c2','state':'DISCOVERED','depends_on':['c1'],'automation':'REVIEW','required_assurance':'A1'}]
py_schedule=schedule(items,NOW)
py_errors=[]
for e in validate(items):
 if e[0]=='DEPENDENCY_CYCLE':py_errors.append({'kind':e[0],'path':list(e[1])})
 else:py_errors.append({'kind':e[0],'item':e[1],'dependency':e[2]})
rust=json.loads(subprocess.check_output(['cargo','run','--quiet','--manifest-path','rust/eos-core/Cargo.toml','--bin','scheduler_parity'],input=json.dumps(items),text=True))
# Exact schedule parity after removing omitted-vs-empty optional representation differences.
def norm_schedule(rows):
 out=[]
 for r in rows:
  x={'id':r['id'],'schedule_state':r['schedule_state']}
  if r.get('blocked_by'):x['blocked_by']=r['blocked_by']
  if r.get('lane') is not None:x['lane']=r['lane']
  if r.get('required_assurance') is not None:x['required_assurance']=r['required_assurance']
  out.append(x)
 return out
assert norm_schedule(py_schedule)==norm_schedule(rust['schedule']), (py_schedule,rust['schedule'])
# Validate error kinds and concrete missing-dependency tuple; cycle path should also match current DFS semantics.
def norm_errs(rows):return sorted(rows,key=lambda x:(x['kind'],x.get('item',''),x.get('dependency',''),'/'.join(x.get('path',[]))))
assert norm_errs(py_errors)==norm_errs(rust['errors']), (py_errors,rust['errors'])
by={x['id']:x for x in rust['schedule']}
assert by['det']['lane']=='DETERMINISTIC'
assert by['review']['lane']=='REASONING_REVIEW'
assert by['formal']['lane']=='FORMAL_OR_HIGH_ASSURANCE'
assert by['policy']['lane']=='POLICY_GATE'
assert by['leased']['schedule_state']=='LEASED'
assert by['blocked']['schedule_state']=='BLOCKED'
print('8 scheduler/dependency Python↔Rust parity assertions passed')
