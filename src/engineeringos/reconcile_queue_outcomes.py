#!/usr/bin/env python3
import json
from queue_model import resolve
from outcome_ledger import read_outcomes
from state_paths import runtime,OUTCOME_LEDGER
Q=runtime('work-queue.json');L=OUTCOME_LEDGER
q=json.load(open(Q)); outcomes=read_outcomes(L); by={x['item_id']:x for x in outcomes}
changed=[]
for item in q['items']:
    o=by.get(item['id'])
    if item['state']=='PENDING_RESOLUTION' and o and o['label'] in {'FALSE_POSITIVE','SEMANTIC_CORRECTION'}:
        resolve(item,'engineeringos-outcome-reconciler',o['evidence_refs']+[f"outcome:{o['outcome_id']}"])
        item['outcome_label']=o['label'];changed.append(item['id'])
Q.write_text(json.dumps(q,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'resolved':changed},indent=2))
