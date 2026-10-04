from __future__ import annotations

import datetime as dt
import fcntl
import hashlib
import json
import os
import pathlib
import statistics
import tempfile

from state_paths import runtime

STATE=runtime()

def utcnow() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()

def atomic_json(path: pathlib.Path, obj: dict) -> None:
    path.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=False)+"\n").encode()
    fd,tmp=tempfile.mkstemp(prefix=path.name+".",suffix=".tmp",dir=path.parent)
    try:
        with os.fdopen(fd,"wb") as h:
            h.write(raw); h.flush(); os.fsync(h.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def append_once(path: pathlib.Path,row: dict) -> bool:
    path.parent.mkdir(parents=True,exist_ok=True)
    with open(path,"a+",encoding="utf-8") as h:
        fcntl.flock(h.fileno(),fcntl.LOCK_EX)
        h.seek(0)
        for line in h:
            if line.strip() and json.loads(line).get("observation_id")==row["observation_id"]:
                fcntl.flock(h.fileno(),fcntl.LOCK_UN)
                return False
        h.seek(0,os.SEEK_END)
        h.write(json.dumps(row,sort_keys=True,ensure_ascii=False)+"\n")
        h.flush(); os.fsync(h.fileno())
        fcntl.flock(h.fileno(),fcntl.LOCK_UN)
    return True

def read_jsonl(path: pathlib.Path) -> list[dict]:
    if not path.exists(): return []
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]

def make_observation(snapshot: dict, action: dict, item: dict, revision: str | None, routing_contract: str = "legacy-single-axis/v1") -> dict:
    key="|".join([str(snapshot.get("content_sha256","")),str(item.get("item_id","")),str(revision or "unknown"),str(routing_contract)])
    obs_id=hashlib.sha256(key.encode()).hexdigest()[:24]
    scheduler=item.get("scheduler_lane")
    model=item.get("model_recommendation")
    return {
        "schema_version":1,
        "observation_id":obs_id,
        "observed_at":utcnow(),
        "snapshot_content_sha256":snapshot.get("content_sha256"),
        "source_head":snapshot.get("source_head"),
        "item_id":item.get("item_id"),
        "kind":item.get("kind"),
        "required_assurance":action.get("required_assurance"),
        "automation":action.get("automation"),
        "scheduler_lane":scheduler,
        "model_recommendation":model,
        "advisory_route":item.get("advisory_route"),
        "answer_confidence":item.get("answer_confidence"),
        "probabilities":item.get("probabilities"),
        "human_authority_decision":item.get("human_authority_decision"),
        "human_authority_required":item.get("human_authority_required"),
        "human_authority_unresolved":item.get("human_authority_unresolved"),
        "human_authority_source":item.get("human_authority_source"),
        "human_authority_rule":item.get("human_authority_rule"),
        "latency_ms":item.get("latency_ms"),
        "model":item.get("model"),
        "model_revision":revision,
        "routing_contract":routing_contract,
        "comparable":scheduler is not None,
        "agrees_with_scheduler": scheduler == model if scheduler is not None else None,
        "label_strength":"WEAK_SCHEDULER_REFERENCE",
        "edb_gold":False,
        "authorization":"UNAVAILABLE",
    }

def summarize(rows: list[dict]) -> dict:
    comparable=[r for r in rows if r.get("comparable")]
    agreements=[r for r in comparable if r.get("agrees_with_scheduler") is True]
    high=[r for r in comparable if r.get("required_assurance") in {"A3","A4","A5"}]
    high_disagree=[r for r in high if r.get("agrees_with_scheduler") is False]
    conf=[float(r["answer_confidence"]) for r in rows if r.get("answer_confidence") is not None]
    lat=[float(r["latency_ms"]) for r in rows if r.get("latency_ms") is not None]
    authority_required=[r for r in rows if r.get("human_authority_required") is True]
    authority_unresolved=[r for r in rows if r.get("human_authority_unresolved") is True]
    return {
        "schema_version":1,
        "generated_at":utcnow(),
        "observations":len(rows),
        "comparable_observations":len(comparable),
        "scheduler_agreement_rate":len(agreements)/len(comparable) if comparable else None,
        "high_assurance_comparable":len(high),
        "high_assurance_disagreements":len(high_disagree),
        "median_answer_confidence":statistics.median(conf) if conf else None,
        "median_latency_ms":statistics.median(lat) if lat else None,
        "human_authority_required_decisions":len(authority_required),
        "human_authority_unresolved":len(authority_unresolved),
        "label_strength":"WEAK_SCHEDULER_REFERENCE",
        "edb_gold_observations":0,
    }

def run() -> dict:
    projection_path=STATE/"system-one/projection.json"
    brief_path=STATE/"action-brief.json"
    snapshot_path=STATE/"shadow/latest.json"
    if not (projection_path.exists() and brief_path.exists() and snapshot_path.exists()):
        summary=summarize(read_jsonl(STATE/"system-one/observations.jsonl"))
        atomic_json(STATE/"system-one/observation-summary.json",summary)
        return summary
    projection=json.loads(projection_path.read_text())
    brief=json.loads(brief_path.read_text())
    snapshot=json.loads(snapshot_path.read_text())
    by_action={x.get("item_id"):x for x in brief.get("actions",[])}
    revisions=((projection.get("provider_health") or {}).get("body") or {}).get("revisions") or {}
    revision=revisions.get("typed-decisions")
    routing_contract=projection.get("routing_contract","legacy-single-axis/v1")
    path=STATE/"system-one/observations.jsonl"
    appended=0
    for item in projection.get("items",[]):
        action=by_action.get(item.get("item_id"),{})
        if append_once(path,make_observation(snapshot,action,item,revision,routing_contract)): appended+=1
    rows=read_jsonl(path)
    summary=summarize(rows)
    summary["appended_this_cycle"]=appended
    summary["model_revision"]=revision
    summary["routing_contract"]=routing_contract
    atomic_json(STATE/"system-one/observation-summary.json",summary)
    return summary

if __name__=="__main__":
    print(json.dumps(run(),indent=2,ensure_ascii=False))
