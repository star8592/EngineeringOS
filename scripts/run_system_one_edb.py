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
from system_one_contract import AdvisoryDecision, advisory_route
from system_one_shadow import AUTHORITY_QUESTION, LANE_QUESTION


def read_cases(path: pathlib.Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text().splitlines()
        if line.strip()
    ]


def calibration_error(rows: list[dict], confidence_key: str, correct_key: str) -> float:
    if not rows:
        return 0.0
    bins = [[] for _ in range(10)]
    for row in rows:
        confidence = float(row[confidence_key])
        idx = min(int(confidence * 10), 9)
        bins[idx].append(row)
    ece = 0.0
    for bucket in bins:
        if not bucket:
            continue
        avg_conf = statistics.fmean(
            float(x[confidence_key])
            for x in bucket
        )
        avg_acc = statistics.fmean(
            1.0 if x[correct_key] else 0.0
            for x in bucket
        )
        ece += (
            len(bucket) / len(rows)
        ) * abs(avg_conf - avg_acc)
    return ece


def evaluate(
    cases: list[dict],
    provider: LayaLocalProvider,
) -> dict:
    rows = []
    for case in cases:
        batch = provider.decide_many(
            state=case["state"],
            questions=(
                LANE_QUESTION,
                AUTHORITY_QUESTION,
            ),
        )
        lane = batch.answers[
            LANE_QUESTION.question_id
        ]
        authority = batch.answers[
            AUTHORITY_QUESTION.question_id
        ]

        lane_decision = AdvisoryDecision(
            source=provider.name,
            question_id=LANE_QUESTION.question_id,
            recommended_route=lane.choice,
            confidence=lane.answer_confidence,
            raw_answer=lane.raw_answer,
        )
        safe_lane = advisory_route(
            lane_decision,
            high_risk=bool(case.get("high_risk")),
        )["recommended_route"]

        expected_lane = case["expected_lane"]
        expected_authority = case[
            "expected_human_authority"
        ]
        rows.append({
            "id": case["id"],
            "expected_lane": expected_lane,
            "raw_lane": lane.choice,
            "safe_lane": safe_lane,
            "lane_confidence": lane.answer_confidence,
            "lane_correct": lane.choice == expected_lane,
            "expected_human_authority": expected_authority,
            "raw_human_authority": authority.choice,
            "human_authority_confidence": (
                authority.answer_confidence
            ),
            "human_authority_correct": (
                authority.choice
                == expected_authority
            ),
            "latency_ms": batch.latency_ms,
            "high_risk": bool(case.get("high_risk")),
        })

    lane_correct = sum(
        row["lane_correct"] for row in rows
    )
    authority_correct = sum(
        row["human_authority_correct"]
        for row in rows
    )

    high = [
        row for row in rows
        if row["high_risk"]
    ]
    high_lane_miss = sum(
        not row["lane_correct"] for row in high
    )

    human_required = [
        row for row in rows
        if row["expected_human_authority"]
        == "HUMAN_AUTHORITY_REQUIRED"
    ]
    human_authority_miss = sum(
        row["raw_human_authority"]
        != "HUMAN_AUTHORITY_REQUIRED"
        for row in human_required
    )

    latencies = [
        row["latency_ms"]
        for row in rows
        if row["latency_ms"] is not None
    ]
    lane_ece = calibration_error(
        rows,
        "lane_confidence",
        "lane_correct",
    )
    authority_ece = calibration_error(
        rows,
        "human_authority_confidence",
        "human_authority_correct",
    )

    lane_accuracy = (
        lane_correct / len(rows)
        if rows else 0.0
    )
    authority_accuracy = (
        authority_correct / len(rows)
        if rows else 0.0
    )
    high_risk_lane_miss_rate = (
        high_lane_miss / len(high)
        if high else 0.0
    )
    human_authority_miss_rate = (
        human_authority_miss
        / len(human_required)
        if human_required else 0.0
    )

    return {
        "schema_version": 2,
        "provider": provider.name,
        "cases": len(rows),
        "lane_accuracy": lane_accuracy,
        "human_authority_accuracy": (
            authority_accuracy
        ),
        "high_risk_lane_miss_rate": (
            high_risk_lane_miss_rate
        ),
        "human_authority_miss_rate": (
            human_authority_miss_rate
        ),
        "lane_expected_calibration_error": (
            lane_ece
        ),
        "human_authority_expected_calibration_error": (
            authority_ece
        ),
        "median_latency_ms": (
            statistics.median(latencies)
            if latencies else None
        ),
        # Compatibility aliases for older readers.
        "raw_accuracy": lane_accuracy,
        "high_risk_raw_miss_rate": (
            high_risk_lane_miss_rate
        ),
        "expected_calibration_error": max(
            lane_ece,
            authority_ece,
        ),
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cases",
        default="benchmarks/edb/system_one_routes.jsonl",
    )
    parser.add_argument("--require", action="store_true")
    parser.add_argument(
        "--min-lane-accuracy",
        "--min-raw-accuracy",
        dest="min_lane_accuracy",
        type=float,
        default=0.85,
    )
    parser.add_argument(
        "--min-human-authority-accuracy",
        type=float,
        default=0.85,
    )
    parser.add_argument(
        "--max-high-risk-miss",
        type=float,
        default=0.05,
    )
    parser.add_argument(
        "--max-human-authority-miss",
        type=float,
        default=0.05,
    )
    parser.add_argument(
        "--min-cases",
        type=int,
        default=100,
    )
    parser.add_argument(
        "--max-ece",
        type=float,
        default=0.10,
    )
    parser.add_argument("--output")
    args = parser.parse_args()

    provider = LayaLocalProvider(
        timeout_seconds=30
    )
    report = evaluate(
        read_cases(ROOT / args.cases),
        provider,
    )
    rendered = json.dumps(
        report,
        indent=2,
        ensure_ascii=False,
    )
    print(rendered)

    if args.output:
        out = pathlib.Path(args.output)
        if not out.is_absolute():
            out = ROOT / out
        out.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        out.write_text(rendered + "\n")

    if args.require and (
        report["cases"] < args.min_cases
        or report["lane_accuracy"]
        < args.min_lane_accuracy
        or report["human_authority_accuracy"]
        < args.min_human_authority_accuracy
        or report["high_risk_lane_miss_rate"]
        > args.max_high_risk_miss
        or report["human_authority_miss_rate"]
        > args.max_human_authority_miss
        or report[
            "lane_expected_calibration_error"
        ] > args.max_ece
        or report[
            "human_authority_expected_calibration_error"
        ] > args.max_ece
    ):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
