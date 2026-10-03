# Contract-level invariants documented as executable assertions over the committed schema.
import json, pathlib
p=pathlib.Path('.engineeringos/work-queue.json')
q=json.load(open(p))
ids=[x['id'] for x in q['items']]
assert len(ids)==len(set(ids))
assert all(x['state'] in {'DISCOVERED','REOPENED','PENDING_RESOLUTION','RESOLVED','SUPERSEDED','BLOCKED','IN_PROGRESS'} for x in q['items'])
assert all('required_assurance' in x and 'automation' in x for x in q['items'])
print('3 work-queue invariants passed')
