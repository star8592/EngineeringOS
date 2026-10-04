#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
import statistics
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/engineeringos"))

from authority_policy import decide_authority, validate_policy
from decis_provider import DecisProvider
from laya_provider import LayaLocalProvider
from system_one_provider import SystemOneProvider
from system_one_contract import advisory_route
from system_one_shadow import LANE_QUESTION


DEFAULT_AUTHORITY_POLICY = (
    ROOT
    / "project_profiles/devcontrol/system-one-authority-policy.json"
)


def read_cases(path: pathlib.Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text().splitlines()
        if line.strip()
    ]


def read_authority_policy(path: pathlib.Path) -> dict:
    policy = json.loads(path.read_text())
    validate_policy(policy)
    return policy


def calibration_error(
    rows: list[dict],
    confidence_key: str,
    correct_key: str,
) -> float:
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
    provider: SystemOneProvider,
    authority_policy: dict,
) -> dict:
    rows = []
    for case in cases:
        result = provider.decide(
            state=case["state"],
            question=LANE_QUESTION,
        )
        raw_lane = (
            result.decision.recommended_route
        )
        safe_lane = advisory_route(
            result.decision,
            high_risk=bool(case.get("high_risk")),
        )["recommended_route"]

        authority = decide_authority(
            authority_policy,
            {"kind": case["state"].get("kind")},
        )
        expected_lane = case["expected_lane"]
        expected_authority = case[
            "expected_human_authority"
        ]

        rows.append({
            "id": case["id"],
            "model": result.model,
            "expected_lane": expected_lane,
            "raw_lane": raw_lane,
            "safe_lane": safe_lane,
            "lane_confidence": result.answer_confidence,
            "lane_correct": raw_lane == expected_lane,
            "expected_human_authority": expected_authority,
            "human_authority_decision": authority.decision,
            "human_authority_rule": authority.rule,
            "human_authority_source": authority.source,
            "human_authority_correct": (
                authority.decision
                == expected_authority
            ),
            "human_authority_unresolved": (
                authority.decision
                == "AUTHORITY_POLICY_UNRESOLVED"
            ),
            "latency_ms": result.latency_ms,
            "high_risk": bool(case.get("high_risk")),
        })

    lane_correct = sum(
        row["lane_correct"] for row in rows
    )
    high = [
        row for row in rows
        if row["high_risk"]
    ]
    high_lane_miss = sum(
        not row["lane_correct"] for row in high
    )
    authority_unresolved = sum(
        row["human_authority_unresolved"]
        for row in rows
    )
    authority_mismatches = sum(
        not row["human_authority_correct"]
        for row in rows
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

    lane_accuracy = (
        lane_correct / len(rows)
        if rows else 0.0
    )
    high_risk_lane_miss_rate = (
        high_lane_miss / len(high)
        if high else 0.0
    )
    authority_policy_accuracy = (
        (len(rows) - authority_mismatches)
        / len(rows)
        if rows else 0.0
    )

    return {
        "schema_version": 2,
        "routing_contract": (
            "processing-lane+authority-policy/v2"
        ),
        "provider": provider.name,
        "models": sorted({row["model"] for row in rows}),
        "cases": len(rows),
        "lane_accuracy": lane_accuracy,
        "high_risk_lane_miss_rate": (
            high_risk_lane_miss_rate
        ),
        "lane_expected_calibration_error": (
            lane_ece
        ),
        "authority_policy_accuracy": (
            authority_policy_accuracy
        ),
        "authority_policy_unresolved": (
            authority_unresolved
        ),
        "authority_policy_mismatches": (
            authority_mismatches
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
        "expected_calibration_error": lane_ece,
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cases",
        default="benchmarks/edb/system_one_routes.jsonl",
    )
    parser.add_argument(
        "--backend",
        choices=("laya", "decis"),
        default="laya",
    )
    parser.add_argument("--base-url")
    parser.add_argument("--model")
    parser.add_argument("--api-key")
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    parser.add_argument(
        "--authority-policy",
        default=str(
            DEFAULT_AUTHORITY_POLICY.relative_to(ROOT)
        ),
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
        "--max-high-risk-miss",
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

    policy_path = pathlib.Path(
        args.authority_policy
    )
    if not policy_path.is_absolute():
        policy_path = ROOT / policy_path

    if args.backend == "decis":
        provider = DecisProvider(
            base_url=args.base_url,
            model=args.model,
            api_key=args.api_key,
            timeout_seconds=args.timeout_seconds,
        )
    else:
        provider = LayaLocalProvider(
            base_url=args.base_url,
            model=args.model,
            api_key=args.api_key,
            timeout_seconds=args.timeout_seconds,
        )
    report = evaluate(
        read_cases(ROOT / args.cases),
        provider,
        read_authority_policy(policy_path),
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
        or report["high_risk_lane_miss_rate"]
        > args.max_high_risk_miss
        or report[
            "lane_expected_calibration_error"
        ] > args.max_ece
        or report["authority_policy_unresolved"] != 0
        or report["authority_policy_mismatches"] != 0
    ):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
