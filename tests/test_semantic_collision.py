import sys;sys.path.insert(0,'src/engineeringos')
from semantic_collision import assess
M={'domains':{'release_identity':{'paths':['VERSION']}}}
assert assess(['x'],['VERSION'],['release_identity'],M)['state']=='BLOCKED_BY_SEMANTIC_COLLISION'
assert assess(['x'],['unrelated'],['release_identity'],M)['state']=='CLEAR'
assert assess(['scripts/deploy_production.sh'],['scripts/deploy_production.sh'],[],M)['state']=='BLOCKED_BY_ACTIVE_LINE'
print('3 semantic-collision invariants passed')
