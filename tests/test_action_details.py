import sys
sys.path.insert(0,'src/engineeringos')
from action_details import build_action_details
brief={'project':'DevControl','snapshot_content_sha256':'s','actions':[
 {'item_id':'a','kind':'TRIAGE_DIRTY_WORKSPACES','priority':2},
 {'item_id':'b','kind':'REVIEW_OVERLAPPING_LINES','priority':2},
 {'item_id':'c','kind':'CLOSE_ARTIFACT_IDENTITY_GAP','priority':2},
]}
debt={'dimensions':{
 'dirty_workspace':{'evidence':[{'branch':'x','change_count':3,'changed_paths':['a','b','c']}]},
 'overlap':{'evidence':[{'a':'x','b':'y','path_overlap':.5,'shared_paths':['f']}]}}}
release={'artifact_identity_state':'UNKNOWN','release_evidence_file':'e.json','production':{'release_id':'abc'},'reasoning':{'artifact_identity':'missing digest'}}
x=build_action_details(brief,debt,release)
assert len(x['items'])==3 and x['target_mutation_authorized'] is False
assert x['items'][0]['evidence'][0]['change_count']==3
assert x['items'][1]['evidence'][0]['shared_paths']==['f']
assert x['items'][2]['evidence'][0]['artifact_identity_state']=='UNKNOWN'
assert all(i['suggested_resolution'] for i in x['items'])
print('7 action-detail invariants passed')
