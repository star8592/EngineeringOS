import sys,tempfile,pathlib
sys.path.insert(0,'src/engineeringos')
from outcome_ledger import *
with tempfile.TemporaryDirectory() as d:
 p=pathlib.Path(d)/'o.jsonl'
 append_outcome(p,outcome_id='o1',item_id='w1',label='FALSE_POSITIVE',evidence_refs=['exp:1'])
 assert read_outcomes(p)[0]['label']=='FALSE_POSITIVE'
 try: append_outcome(p,outcome_id='o1',item_id='w1',label='FALSE_POSITIVE',evidence_refs=['exp:1']);raise AssertionError()
 except OutcomeError as e: assert str(e)=='DUPLICATE_OUTCOME_ID'
 try: append_outcome(p,outcome_id='o2',item_id='w1',label='FALSE_POSITIVE',evidence_refs=[]);raise AssertionError()
 except OutcomeError as e: assert str(e)=='EVIDENCE_REQUIRED'
print('3 outcome-ledger invariants passed')
