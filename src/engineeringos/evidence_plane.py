#!/usr/bin/env python3
from __future__ import annotations

import datetime
import json
import pathlib
import subprocess

from production_evidence_semantics import interpret
from workflow_evidence import classify_workflow_runs


TARGET = "/mnt/disk1/Code/DevControl2"
OUT = pathlib.Path("artifacts/evidence-plane.json")


def cmd(args):
    process = subprocess.run(
        args,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return process.stdout.strip(), process.returncode, process.stderr.strip()


def git(*args):
    return cmd(["git", "-C", TARGET, *args])[0]


def gh(*args):
    return cmd(["gh", *args])


def legacy_state(evidence: dict) -> str:
    state = evidence.get("state")
    if state == "PASS":
        return "SUCCESS"
    if state == "FAIL":
        conclusion = str(
            evidence.get("conclusion") or "failure"
        ).upper()
        return conclusion
    if state == "RUNNING":
        status = str(
            evidence.get("status") or "in_progress"
        ).upper()
        return status
    return "UNKNOWN"


def main() -> dict:
    OUT.parent.mkdir(parents=True, exist_ok=True)

    origin = git("rev-parse", "origin/main")
    version = git("show", "origin/main:VERSION")

    runs_raw, runs_rc, runs_error = gh(
        "run",
        "list",
        "--repo",
        "star8592/DevControl2",
        "--branch",
        "main",
        "--limit",
        "50",
        "--json",
        (
            "databaseId,headSha,workflowName,status,"
            "conclusion,createdAt,updatedAt,url"
        ),
    )
    if runs_rc == 0:
        runs = json.loads(runs_raw or "[]")
        workflow_query = {
            "state": "OK",
            "returncode": 0,
        }
    else:
        runs = []
        workflow_query = {
            "state": "ERROR",
            "returncode": runs_rc,
            "error": runs_error[:500],
        }

    by_sha = {}
    for row in runs:
        by_sha.setdefault(row["headSha"], []).append(row)
    head_runs = by_sha.get(origin, [])

    if workflow_query["state"] == "OK":
        ci_evidence = classify_workflow_runs(
            head_runs,
            workflow_name="DevControl 3 CI",
        )
        smoke_evidence = classify_workflow_runs(
            head_runs,
            workflow_name="Production Smoke",
        )
        spec_evidence = classify_workflow_runs(
            head_runs,
            workflow_name="External Spec Drift",
        )
    else:
        # Transport/query failure is not evidence that a workflow is absent.
        ci_evidence = {
            "state": "NO_RUN",
            "workflow_name": "DevControl 3 CI",
            "latest_run": None,
            "classification_suppressed": True,
        }
        smoke_evidence = {
            "state": "NO_RUN",
            "workflow_name": "Production Smoke",
            "latest_run": None,
            "classification_suppressed": True,
        }
        spec_evidence = {
            "state": "NO_RUN",
            "workflow_name": "External Spec Drift",
            "latest_run": None,
            "classification_suppressed": True,
        }

    success_smokes = [
        row
        for row in runs
        if row["workflowName"] == "Production Smoke"
        and row["conclusion"] == "success"
    ]
    latest_smoke = (
        sorted(
            success_smokes,
            key=lambda row: row["createdAt"],
            reverse=True,
        )[0]
        if success_smokes
        else None
    )
    smoke_reachable = None
    if latest_smoke:
        smoke_reachable = (
            subprocess.run(
                [
                    "git",
                    "-C",
                    TARGET,
                    "merge-base",
                    "--is-ancestor",
                    latest_smoke["headSha"],
                    "origin/main",
                ]
            ).returncode
            == 0
        )

    release_path = pathlib.Path(
        "artifacts/devcontrol-release-evidence.json"
    )
    release_evidence = (
        json.loads(release_path.read_text())
        if release_path.exists()
        else {}
    )

    if workflow_query["state"] == "OK":
        interpretation = interpret(
            source_ci=legacy_state(ci_evidence),
            source_head_smoke=legacy_state(smoke_evidence),
            source_ci_evidence=ci_evidence,
            release_evidence=release_evidence,
        )
    else:
        interpretation = interpret(
            source_ci="UNKNOWN",
            source_head_smoke="UNKNOWN",
            release_evidence=release_evidence,
        )
        interpretation["qualification_evidence_state"] = (
            "QUERY_ERROR"
        )
        interpretation["qualification_reason"] = (
            "WORKFLOW_QUERY_ERROR"
        )

    release_list, release_rc, release_error = gh(
        "release",
        "list",
        "--repo",
        "star8592/DevControl2",
        "--limit",
        "5",
    )

    report = {
        "generated_at": datetime.datetime.now(
            datetime.timezone.utc
        ).isoformat(),
        "repository": "star8592/DevControl2",
        "origin_main": origin,
        "version": version,
        "workflow_query": workflow_query,
        "current_head_evidence": {
            # Legacy compatibility fields.
            "ci": legacy_state(ci_evidence),
            "production_smoke": legacy_state(smoke_evidence),
            "external_spec_drift": legacy_state(spec_evidence),
            # Explicit qualification evidence.
            "ci_evidence": ci_evidence,
            "production_smoke_evidence": smoke_evidence,
            "external_spec_drift_evidence": spec_evidence,
            "runs": head_runs,
        },
        "latest_successful_production_smoke": latest_smoke,
        "latest_smoke_reachable_from_current_main": smoke_reachable,
        "live_release_evidence": release_evidence,
        "release_api": {
            "status": (
                "ERROR"
                if release_rc != 0
                else ("EMPTY" if not release_list else "PRESENT")
            ),
            "error": (
                release_error[:500]
                if release_rc != 0
                else None
            ),
        },
        "interpretation": interpretation,
        "guardrail": (
            "Source-head qualification, source-head production smoke, "
            "and live-production qualification are distinct. NO_RUN means "
            "the workflow query succeeded and no qualifying run exists for "
            "the current source head; query failure is reported separately."
        ),
    }
    OUT.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    )
    print(
        json.dumps(
            report["current_head_evidence"],
            indent=2,
            ensure_ascii=False,
        )
    )
    print("interpretation", report["interpretation"])
    print(
        "latest successful smoke",
        latest_smoke["headSha"] if latest_smoke else None,
        "reachable=",
        smoke_reachable,
    )
    return report


if __name__ == "__main__":
    main()
