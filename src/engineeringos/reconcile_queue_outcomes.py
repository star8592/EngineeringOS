#!/usr/bin/env python3
from __future__ import annotations
import json,pathlib
from queue_model import resolve
from outcome_ledger import read_outcomes
from state_paths import runtime,OUTCOME_LEDGER

Q=runtime('work-queue.json');L=OUTCOME_LEDGER;E=pathlib.Path('artifacts/evidence-plane.json')

def authoritative_ci_refs(evidence):
    if not evidence or (evidence.get('current_head_evidence') or {}).get('ci')!='SUCCESS': return []
    origin=evidence.get('origin_main');runs=(evidence.get('current_head_evidence') or {}).get('runs') or []
    success=[r for r in runs if r.get('workflowName')=='DevControl 3 CI' and r.get('headSha')==origin and r.get('status')=='completed' and r.get('conclusion')=='success']
    if not success:return []
    latest=sorted(success,key=lambda x:x.get('createdAt',''),reverse=True)[0]
    return [f"github-actions:{latest['url']}",f"source-sha:{origin}"]

def reconcile(q,outcomes,evidence):
    by={x['item_id']:x for x in outcomes};changed=[]
    ci_refs=authoritative_ci_refs(evidence)
    for item in q['items']:
        if item.get('state')!='PENDING_RESOLUTION': continue
        o=by.get(item['id'])
        if o and o['label'] in {'FALSE_POSITIVE','SEMANTIC_CORRECTION'}:
            resolve(item,'engineeringos-outcome-reconciler',o['evidence_refs']+[f"outcome:{o['outcome_id']}"])
            item['outcome_label']=o['label'];changed.append({'id':item['id'],'reason':'OUTCOME_LEDGER'})
            continue
        if item.get('kind')=='RESOLVE_MAIN_QUALIFICATION' and ci_refs:
            resolve(item,'engineeringos-authoritative-ci-reconciler',ci_refs)
            item['closure_kind']='AUTHORITATIVE_CI_SUCCESS';changed.append({'id':item['id'],'reason':'AUTHORITATIVE_CI_SUCCESS'})
    return changed

def main():
    q=json.load(open(Q));outcomes=read_outcomes(L);evidence=json.load(open(E)) if E.exists() else {}
    changed=reconcile(q,outcomes,evidence)
    Q.write_text(json.dumps(q,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'resolved':changed},indent=2));return 0
if __name__=='__main__': raise SystemExit(main())
