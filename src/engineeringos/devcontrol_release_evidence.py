#!/usr/bin/env python3
from __future__ import annotations

import datetime
import json
import pathlib
import ssl
import subprocess
import urllib.request

from devcontrol_deployment_observer import observe_deployment


REPO = pathlib.Path("/mnt/disk1/Code/DevControl2")
EVIDENCE_DIR = pathlib.Path.home() / ".local/state/devcontrol3/release-evidence"
OUT = pathlib.Path("artifacts/devcontrol-release-evidence.json")


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(REPO), *args],
        text=True,
    ).strip()


def fetch(url: str) -> dict:
    with urllib.request.urlopen(
        url,
        timeout=8,
        context=ssl._create_unverified_context(),
    ) as response:
        return json.load(response)


def build_release_evidence(
    *,
    ready: dict,
    qualification_evidence: dict | None,
    release_evidence_file: pathlib.Path | None,
    full_source_sha: str | None,
    deployment: dict,
) -> dict:
    qualified = bool(
        qualification_evidence
        and "release_gate_all"
        in qualification_evidence.get("gates", [])
        and "post_deploy"
        in qualification_evidence.get("gates", [])
    )

    deployment_state = deployment.get(
        "deployment_identity_state",
        "PARTIAL",
    )
    has_deployed_digests = bool(
        (deployment.get("server") or {}).get("tree_sha256")
        and (deployment.get("agent") or {}).get("tree_sha256")
    )
    artifact_state = (
        "PARTIAL"
        if has_deployed_digests
        else "UNKNOWN"
    )

    if deployment_state == "RESOLVED":
        deployment_reasoning = (
            "runtime release_id uniquely maps to source and both production "
            "server and local agent current releases match that release with "
            "content-addressed deployed-tree digests"
        )
    else:
        deployment_reasoning = (
            "deployment binding is incomplete: "
            + ",".join(deployment.get("reasons") or ["UNKNOWN"])
        )

    if artifact_state == "PARTIAL":
        artifact_reasoning = (
            "deployed server/agent byte trees have immutable digests, but the "
            "original staged server artifact manifest/tarball digest is not "
            "durably persisted in release evidence"
        )
    else:
        artifact_reasoning = (
            "release evidence records qualification gates but no durable "
            "build artifact manifest or deployed-tree digests"
        )

    return {
        "observed_at": datetime.datetime.now(
            datetime.timezone.utc
        ).isoformat(),
        "production": ready,
        "release_evidence_file": (
            str(release_evidence_file)
            if release_evidence_file
            else None
        ),
        "qualification_evidence": qualification_evidence,
        "full_source_sha": full_source_sha,
        "source_identity_state": (
            "RESOLVED"
            if full_source_sha
            else "UNKNOWN"
        ),
        "qualification_state": (
            "RESOLVED"
            if qualified
            else "UNKNOWN"
        ),
        "artifact_identity_state": artifact_state,
        "deployment_identity_state": deployment_state,
        "deployment_binding_sha256": deployment.get(
            "deployment_binding_sha256"
        ),
        "deployment_observation": deployment,
        "reasoning": {
            "artifact_identity": artifact_reasoning,
            "deployment_identity": deployment_reasoning,
        },
    }


def run() -> dict:
    ready = fetch("https://mcp.devcontrol.dev/readyz")
    release_id = ready["release_id"]
    evidence_file = EVIDENCE_DIR / f"{release_id}.json"
    qualification_evidence = (
        json.loads(evidence_file.read_text())
        if evidence_file.exists()
        else None
    )

    matches = [
        sha
        for sha in git("rev-list", "--all").splitlines()
        if sha.startswith(release_id)
    ]
    full_source_sha = (
        matches[0]
        if len(matches) == 1
        else None
    )
    deployment = observe_deployment(
        release_id=release_id,
        full_source_sha=full_source_sha,
    )
    out = build_release_evidence(
        ready=ready,
        qualification_evidence=qualification_evidence,
        release_evidence_file=(
            evidence_file
            if evidence_file.exists()
            else None
        ),
        full_source_sha=full_source_sha,
        deployment=deployment,
    )
    OUT.write_text(
        json.dumps(
            out,
            indent=2,
            ensure_ascii=False,
        )
        + "\n"
    )
    print(
        json.dumps(
            out,
            indent=2,
            ensure_ascii=False,
        )
    )
    return out


if __name__ == "__main__":
    run()
