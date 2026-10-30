#!/usr/bin/env python3
"""Sanitized advisory SSH-alias preflight. Does not initiate an SSH connection.

Only run with a trusted local SSH config: OpenSSH may evaluate 'Match exec'
while resolving configuration. Never run this with untrusted config files.
No key bytes, resolved IP, username, key file path or SSH stdout are printed.
This tool does not verify server authorization, trust or production identity.
"""
from __future__ import annotations

import argparse
import ipaddress
import json
import re
import subprocess
from pathlib import Path

CANONICAL = "CROSS_PROJECT_ACCESS_AND_AUTH_LESSONS.md"


def evaluate(alias: str, ssh_config_output: str, project_root: Path | None = None) -> dict:
    """Examine only metadata; never echo resolved sensitive configuration."""
    data: dict[str, list[str]] = {}
    for line in ssh_config_output.splitlines():
        k, _, v = line.partition(" ")
        if k and v:
            data.setdefault(k.lower(), []).append(v.strip())
    first = lambda k: data.get(k, [""])[0].lower()
    findings: list[str] = []
    try:
        ipaddress.ip_address(alias.strip("[]"))
        findings.append("RAW_IP_INPUT_REVIEW_PROJECT_ALIAS")
    except ValueError:
        pass
    hostname = first("hostname")
    if not hostname:
        findings.append("HOSTNAME_NOT_RESOLVED")
    if first("identitiesonly") != "yes":
        findings.append("SSH_AGENT_CAN_OFFER_EXTRA_IDENTITIES")
    key_count = len(data.get("identityfile", []))
    if key_count == 0:
        findings.append("NO_IDENTITY_FILE_IN_CONFIG")
    if key_count > 1:
        findings.append("MULTIPLE_IDENTITY_CANDIDATES_REVIEW")
    if first("stricthostkeychecking") in {"no", "off", "false"}:
        findings.append("HOST_KEY_VERIFICATION_DISABLED")
    if project_root is not None:
        agents = project_root / "AGENTS.md"
        try:
            if CANONICAL not in agents.read_text(encoding="utf-8"):
                findings.append("PROJECT_CANONICAL_RUNBOOK_LINK_MISSING")
        except (OSError, UnicodeError):
            findings.append("PROJECT_AGENTS_UNREADABLE")
    return {
        "status": "REVIEW" if findings else "CONFIG_PREFLIGHT_OK_NOT_CONNECTED",
        "findings": findings,
        "alias_supplied": bool(alias),
        "alias_resolves_to_distinct_hostname": bool(hostname and hostname != alias.lower()),
        "configured_identity_candidates": key_count,
        "identities_only": first("identitiesonly") == "yes",
        "host_key_verification_disabled": first("stricthostkeychecking") in {"no", "off", "false"},
        "ssh_network_connection_attempted": False,
        "remote_execution_attempted": False,
        "meaning": "Configuration observations only. Verify project target, host key and authorization separately.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("alias", help="Project-verified SSH Host alias, not a guessed IP")
    parser.add_argument("--project-root", type=Path, default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not re.fullmatch(r"[a-zA-Z0-9_.:\-\[\]]{1,255}", args.alias) or args.alias.startswith("-"):
        parser.error("Invalid SSH alias; check the project's deployment docs")
    try:
        result = subprocess.run(
            ["ssh", "-G", args.alias],
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        print(json.dumps({"status": "SSH_G_UNAVAILABLE", "findings": ["LOCAL_CONFIG_UNREADABLE"]}))
        return 2
    if result.returncode != 0:
        print(json.dumps({"status": "SSH_G_FAILED", "findings": ["LOCAL_CONFIG_ERROR"]}))
        return 2
    report = evaluate(args.alias, result.stdout, args.project_root)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(report["status"])
        for finding in report["findings"]:
            print(" -", finding)
        print("NO CONNECTION ATTEMPTED; actual server identity and authorization still unknown.")
    # Advisory only. REVIEW is not a permission grant or production release gate.
    return 0 if report["status"] == "CONFIG_PREFLIGHT_OK_NOT_CONNECTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
