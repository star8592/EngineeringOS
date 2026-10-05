import copy,sys
sys.path.insert(0,'src/engineeringos')
from protected_work_adoption import assess,inventory_identity

cfg={'name':'K','management_target':'A2_MANAGED','protected_work_policy':'ADOPT_VERIFIED_QUIET','expected_origin':'https://x/K.git','managed_branch':'main','a2_verification_entrypoint':'verify:public'}
base={'state':'PROTECTED_EXISTING_WORK','origin':'https://x/K.git','branch':'main','upstream':'origin/main','ahead':0,'behind':0,'head':'abc'}
inv={'state':'PROTECTED_EXISTING_WORK','head':'abc','paths':[{'path':'a.ts','status':' M','fingerprint':'f1','size':1,'sensitive':False}], 'candidate_packages':[{'id':'g','state':'QUIET'}]}
deferred={'state':'VERIFIED_DEFERRED_CANDIDATE','item_id':'d1','source_sha':'abc','diff_sha256':'dd','changed_paths':['b.ts'],'convergence_authorized':False}
repair={'state':'VERIFIED_PROTECTED_REPAIR_CANDIDATE','item_id':'r1','source_sha':'abc','changes_sha256':'rr','allowed_paths':['a.ts'],'combined_repair_paths':['a.ts'],'verification_argv':['npm','run','verify:public'],'convergence_authorized':False,'composed_verification':{'state':'PASS','source_unchanged':True,'exit_code':0}}
activity={'state':'QUIET','active_reference_count':0}
plan={'schema_version':1,'project':'K','source_sha':'abc','inventory_identity':inventory_identity(inv),'deferred_item_id':'d1','deferred_diff_sha256':'dd','repair_item_id':'r1','repair_changes_sha256':'rr'}
ok=assess(cfg,base,inv,deferred,repair,activity,plan)
assert ok['state']=='ADOPTABLE' and ok['eligible'] and ok['adopted_paths']==['a.ts','b.ts']
assert assess({**cfg,'protected_work_policy':'PROTECT_ONLY'},base,inv,deferred,repair,activity,plan)['reason']=='PROTECTED_WORK_ADOPTION_NOT_AUTHORIZED'
assert assess(cfg,base,{**inv,'candidate_packages':[{'state':'STABLE_RECENT'}]},deferred,repair,activity,plan)['reason']=='PROTECTED_WORK_NOT_QUIET'
assert assess(cfg,base,inv,deferred,repair,{'state':'ACTIVE_REFERENCES','active_reference_count':1},plan)['reason']=='ACTIVE_SOURCE_REFERENCE_PRESENT'
assert assess(cfg,base,inv,deferred,repair,activity,{**plan,'inventory_identity':'bad'})['reason']=='ADOPTION_PLAN_INVENTORY_DRIFT'
assert assess(cfg,base,{**inv,'paths':[{'path':'a.ts','status':' M','fingerprint':'f1','size':1,'sensitive':True}]},deferred,repair,activity,plan)['reason']=='SENSITIVE_PROTECTED_PATH_PRESENT'
assert assess(cfg,base,inv,{**deferred,'changed_paths':['a.ts']},repair,activity,plan)['reason']=='DEFERRED_PROTECTED_PATH_OVERLAP'
badrepair=copy.deepcopy(repair);badrepair['composed_verification']['state']='FAIL'
assert assess(cfg,base,inv,deferred,badrepair,activity,plan)['reason']=='COMPOSED_VERIFICATION_REQUIRED'
print('12 protected-work-adoption invariants passed')
