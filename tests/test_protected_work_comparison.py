import sys
sys.path.insert(0,'src/engineeringos')
from protected_work_comparison import compare

sig={'failure_stage':'eslint','sha256':'abc'}
base={'state':'PASS','source_head':'s','source_unchanged':True}
dirty={'state':'PASS','source_head':'s','source_unchanged':True}
assert compare(base,dirty)['state']=='DIRTY_VERIFIED'
assert compare(base,{**dirty,'state':'FAIL','diagnostic_signature':sig})['state']=='DIRTY_REGRESSION'
assert compare({**base,'state':'FAIL','diagnostic_signature':sig},dirty)['state']=='DIRTY_IMPROVES_BASELINE'
same=compare({**base,'state':'FAIL','diagnostic_signature':sig},{**dirty,'state':'FAIL','diagnostic_signature':sig})
assert same['state']=='BASELINE_RED_SAME_FAILURE' and same['same_failure_signature'] and not same['dirty_verified'] and not same['dirty_regression_proven']
different=compare({**base,'state':'FAIL','diagnostic_signature':sig},{**dirty,'state':'FAIL','diagnostic_signature':{'failure_stage':'tsc','sha256':'def'}})
assert different['state']=='INCONCLUSIVE_DIFFERENT_FAILURE'
assert compare({**base,'source_unchanged':False},dirty)['state']=='SOURCE_CHANGED_DURING_COMPARISON'
assert compare(base,{**dirty,'source_head':'other'})['state']=='SOURCE_SHA_MISMATCH'
assert compare(None,dirty)['state']=='INCOMPLETE_EVIDENCE'
print('12 protected-work-comparison invariants passed')
