import sys;sys.path.insert(0,'src/engineeringos')
from collision import *
r=dispatch_collision_decision(['a','b'],['b','c'],True);assert r['state']=='BLOCKED_BY_ACTIVE_LINE' and r['overlap_paths']==['b']
assert dispatch_collision_decision(['a'],['b'],True)['state']=='CLEAR'
assert dispatch_collision_decision(['a'],['a'],False)['state']=='CLEAR'
print('3 collision invariants passed')
