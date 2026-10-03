#!/usr/bin/env python3
from __future__ import annotations
import json,pathlib
from bounded_executor import execute
from state_paths import runtime

ROOT=pathlib.Path(__file__).resolve().parents[2]

def load(path): return json.load(open(path))

def decide(item, evidence):
    if item.get('kind')!='RESOLVE_MAIN_QUALIFICATION': return {'decision':'NO_ACTION','reason':'NO_BOUNDED_MAPPING'}
    ci=(evidence.get('current_head_evidence') or {}).get('ci','UNKNOWN')
    if ci=='SUCCESS': return {'decision':'NO_ACTION','reason':'AUTHORITATIVE_CI_ALREADY_PASS'}
    if ci in {'IN_PROGRESS','QUEUED','PENDING','REQUESTED','WAITING'}:
        return {'decision':'DEFER','reason':'AUTHORITATIVE_CI_IN_PROGRESS'}
    if ci=='FAILURE': return {'decision':'ALLOW','reason':'AUTHORITATIVE_CI_FAILED_DIAGNOSTIC_FALLBACK'}
    return {'decision':'ALLOW','reason':'AUTHORITATIVE_CI_MISSING_DIAGNOSTIC_FALLBACK'}

def run_once():
    q=load(runtime('work-queue.json'));ev=load(ROOT/'artifacts/evidence-plane.json')
    rows=[]
    for item in q.get('items',[]):
        if item.get('state') in {'RESOLVED','SUPERSEDED'}: continue
        d=decide(item,ev);row={'item_id':item['id'],'kind':item['kind'],**d}
        if d['decision']=='ALLOW':
            result=execute(item_id=item['id']);row.update({'execution':'SUCCEEDED','check_result':result['check_result'],'source_sha':result['source_sha'],'command_id':result['command_id']})
        rows.append(row)
    out={'schema_version':1,'mode':'G3_BOUNDED','target_mutation_authorized':False,'decisions':rows}
    p=runtime('g3/controller.json');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    return out
if __name__=='__main__': print(json.dumps(run_once(),indent=2))
