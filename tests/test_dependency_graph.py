import sys;sys.path.insert(0,'src/engineeringos')
from dependency_graph import validate,readiness
a={'id':'a','state':'DISCOVERED','depends_on':['b']}; b={'id':'b','state':'DISCOVERED'}
assert validate([a,b])==[]; assert readiness(a,{'a':a,'b':b})['state']=='BLOCKED'
b['state']='RESOLVED'; assert readiness(a,{'a':a,'b':b})['state']=='READY'
c={'id':'c','state':'DISCOVERED','depends_on':['d']}; d={'id':'d','state':'DISCOVERED','depends_on':['c']}
assert any(x[0]=='DEPENDENCY_CYCLE' for x in validate([c,d]))
assert any(x[0]=='MISSING_DEPENDENCY' for x in validate([{'id':'x','depends_on':['z']}]))
print('4 dependency invariants passed')
