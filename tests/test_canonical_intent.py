import sys,tempfile,pathlib
sys.path.insert(0,'src/engineeringos')
from canonical_intent import load_canonical_statements,search_statements
with tempfile.TemporaryDirectory() as td:
 p=pathlib.Path(td);(p/'docs/product').mkdir(parents=True);(p/'docs/roadmap').mkdir(parents=True)
 (p/'VISION.md').write_text('# V\n> Human owns intent. System owns engineering.\n')
 (p/'docs/product/CONVERSATIONAL_INTERFACE.md').write_text('# C\nEngineeringOS is conversation-first, not dashboard-first.\nEngineering details are optional and never required homework.\n')
 s=load_canonical_statements(td)
 assert any('conversation-first' in x['statement'] for x in s)
 assert search_statements(s,['conversation-first'])
 assert all(x['authority']=='CURRENT_ACCEPTED_INTENT' for x in s)
print('3 canonical-intent invariants passed')
