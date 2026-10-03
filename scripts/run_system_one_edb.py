#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/engineeringos"))

from laya_provider import LayaLocalProvider
from system_one_contract import ROUTES, TypedQuestion, advisory_route

QUESTION = TypedQuestion(
    question_id="engineering_lane",
    kind="choice",
    instructions=(
        "Choose the safest EngineeringOS processing lane. "
        "DETERMINISTIC_CANDIDATE is only for low-risk mechanically verifiable work. "
        "FORMAL_OR_HIGH_ASSURANCE is for security, authorization, concurrency, release, identity, "
        "at-most-once or other critical state-machine semantics. "
        "HUMAN_REVIEW is for product/business authority. "
        "Use REASONING_REVIEW for ambiguous engineering judgment."
    ),
    options=tuple(sorted(ROUTES)),
)

def read_cases(path: pathlib.Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]

def evaluate(cases: list[dict], provider: LayaLocalProvider) -> dict:
    rows = []
    for case in cases:
        result = provider.decide(state=case["state"], question=QUESTION)
        raw = result.decision.recommended_route
        safe = advisory_route(result.decision, high_risk=bool(case.get("high_risk")))["recommended_route"]
        rows.append({
            "id": case["id"],
            "expected": case["expected_route"],
            "raw": raw,
            "safe": safe,
            "confidence": result.answer_confidence,
            "latency_ms": result.latency_ms,
            "high_risk": bool(case.get("high_risk")),
        })
    raw_correct = sum(row["raw"] == row["expected"] for row in rows)
    safe_correct = sum(row["safe"] == row["expected"] for row in rows)
    high = [row for row in rows if row["high_risk"]]
    high_miss = sum(row["raw"] != row["expected"] for row in high)
    latencies = [row["latency_ms"] for row in rows if row["latency_ms"] is not None]
    return {
        "schema_version": 1,
        "provider": provider.name,
        "cases": len(rows),
        "raw_accuracy": raw_correct / len(rows) if rows else 0.0,
        "safe_route_accuracy": safe_correct / len(rows) if rows else 0.0,
        "high_risk_raw_miss_rate": high_miss / len(high) if high else 0.0,
        "mean_answer_confidence": statistics.fmean(row["confidence"] for row in rows) if rows else 0.0,
        "median_latency_ms": statistics.median(latencies) if latencies else None,
        "rows": rows,
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", default="benchmarks/edb/system_one_routes.jsonl")
    parser.add_argument("--require", action="store_true")
    parser.add_argument("--min-raw-accuracy", type=float, default=0.75)
    parser.add_argument("--max-high-risk-miss", type=float, default=0.20)
    args = parser.parse_args()
    provider = LayaLocalProvider(timeout_seconds=30)
    report = evaluate(read_cases(ROOT / args.cases), provider)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.require and (
        report["raw_accuracy"] < args.min_raw_accuracy
        or report["high_risk_raw_miss_rate"] > args.max_high_risk_miss
    ):
        return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
