import sys
sys.path.insert(0,'src/engineeringos')
from intent_capability import Intent,Capability,reconcile,capabilities_from_doctor
caps=[Capability('surface:student','student',('route:student',)),Capability('surface:parent/register','parent register',('route:parent/register',)),Capability('verification:test-arithmetic','arithmetic',('command:test:arithmetic',),1.0,'VERIFIED')]
r=reconcile([Intent('i1','Students can practice',('student',)),Intent('i2','Parents can register',('parent register',)),Intent('i3','Arithmetic works',('arithmetic',)),Intent('i4','Users can pay',('payments',))],caps)
assert r['summary']=={'verified':1,'discovered':2,'unknown':1,'needs_intent':0}
assert r['intents'][1]['state']=='DISCOVERED'
assert r['intents'][3]['requirements'][0]['evidence']==[]
r=reconcile([Intent('i5','',())],caps);assert r['summary']['needs_intent']==1
d={'software_understanding':{'visible_capabilities':['parent/register'],'verification_commands':['test:parent-auth']}}
x=capabilities_from_doctor(d);assert {c.id for c in x}=={'surface:parent/register','verification:test:parent-auth'}
assert reconcile([Intent('x','parent registration',('parent register',))],x)['intents'][0]['state']=='DISCOVERED'
print('9 intent-capability invariants passed')
