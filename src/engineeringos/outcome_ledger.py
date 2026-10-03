from __future__ import annotations
import json,pathlib,datetime,fcntl,os

ALLOWED={'TRUE_POSITIVE','FALSE_POSITIVE','FALSE_NEGATIVE','TRUE_NEGATIVE','SEMANTIC_CORRECTION'}
class OutcomeError(ValueError): pass

def append_outcome(path, *, outcome_id, item_id, label, evidence_refs, note=''):
    if label not in ALLOWED: raise OutcomeError('UNKNOWN_OUTCOME_LABEL')
    if not evidence_refs: raise OutcomeError('EVIDENCE_REQUIRED')
    p=pathlib.Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    row={'schema_version':1,'outcome_id':outcome_id,'item_id':item_id,'label':label,'evidence_refs':list(evidence_refs),'note':note,'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    with open(p,'a+',encoding='utf-8') as f:
        fcntl.flock(f.fileno(),fcntl.LOCK_EX);f.seek(0)
        old=[json.loads(x) for x in f if x.strip()]
        if any(x['outcome_id']==outcome_id for x in old): raise OutcomeError('DUPLICATE_OUTCOME_ID')
        f.seek(0,os.SEEK_END);f.write(json.dumps(row,sort_keys=True,ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno());fcntl.flock(f.fileno(),fcntl.LOCK_UN)
    return row

def read_outcomes(path):
    p=pathlib.Path(path)
    return [json.loads(x) for x in p.read_text().splitlines() if x.strip()] if p.exists() else []
