import sys;sys.path.insert(0,'src/engineeringos')
from scheduler import schedule
items=[{'id':'a','state':'DISCOVERED','depends_on':[],'automation':'DETERMINISTIC','required_assurance':'A1'}, {'id':'b','state':'DISCOVERED','depends_on':['a'],'automation':'REVIEW','required_assurance':'A2'}]
r={x['id']:x for x in schedule(items)}
assert r['a']['schedule_state']=='DISPATCHABLE' and r['a']['lane']=='DETERMINISTIC'
assert r['b']['schedule_state']=='BLOCKED'
items[0]['state']='RESOLVED'; r={x['id']:x for x in schedule(items)}; assert r['b']['schedule_state']=='DISPATCHABLE' and r['b']['lane']=='REASONING_REVIEW'
print('3 scheduler invariants passed')
