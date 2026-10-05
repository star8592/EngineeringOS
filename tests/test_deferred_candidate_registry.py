import json,pathlib,sys,tempfile
sys.path.insert(0,'src/engineeringos')
from deferred_candidate_registry import assess,summarize

candidate={'item_id':'m1','state':'VERIFIED_DEFERRED_CANDIDATE','source_sha':'abc'}
assert assess(candidate,None)['state']=='BASELINE_MISSING'
assert assess(candidate,{'state':'PROTECTED_EXISTING_WORK','head':'abc'})['state']=='WAITING_PROTECTED_WORK'
assert assess(candidate,{'state':'CLEAN_CONNECTED','head':'def'})['state']=='STALE_SOURCE_REPLAN_REQUIRED'
assert assess(candidate,{'state':'CLEAN_CONNECTED','head':'abc'})['state']=='READY_FOR_REVALIDATION'
assert assess({**candidate,'state':'VERIFICATION_FAILED'},{'state':'CLEAN_CONNECTED','head':'abc'})['state']=='NOT_VERIFIED'
with tempfile.TemporaryDirectory() as td:
 root=pathlib.Path(td);(root/'deferred-candidates').mkdir()
 (root/'baseline.json').write_text(json.dumps({'state':'PROTECTED_EXISTING_WORK','head':'abc'}))
 (root/'deferred-candidates'/'m1.json').write_text(json.dumps(candidate))
 out=summarize(root)
 assert out['verified_candidates']==1 and out['counts']['WAITING_PROTECTED_WORK']==1 and out['items'][0]['file']=='m1.json'
print('8 deferred-candidate-registry invariants passed')
