#!/usr/bin/env python3
"""Read-only audit of canonical runbook anchors in project root AGENTS.md.

Usage:
  python3 scripts/audit_access_runbook_links.py /mnt/disk1/Code
  python3 scripts/audit_access_runbook_links.py /path/to/repo1 /path/to/repo2
  python3 scripts/audit_access_runbook_links.py --json /path/to/projects

This script never reads SSH configs, secrets or dot-env files and never mutates
project files. A passing anchor check proves only that a link exists; it does
not prove that a future agent read it, connected to a server, or passed auth.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

CANONICAL = (
    "github.com/star8592/EngineeringOS/"
    "blob/main/docs/operations/CROSS_PROJECT_ACCESS_AND_AUTH_LESSONS.md"
)

def find_projects(paths: list[Path]) -> list[Path]:
    repos: dict[str, Path] = {}
    for root in paths:
        if (root / ".git").exists():
            repos[str(root.resolve())] = root
            continue
        if not root.is_dir():
            repos[str(root)] = root
            continue
        # One directory deep: a workspace may hold many isolated projects.
        for entry in root.iterdir():
            if entry.is_dir() and (entry / ".git").exists():
                repos[str(entry.resolve())] = entry
    return list(repos.values())

def examine(repo: Path) -> dict[str, str]:
    if not (repo / ".git").exists():
        return {"project": str(repo), "status": "NOT_A_REPOSITORY"}
    agents = repo / "AGENTS.md"
    if not agents.is_file():
        return {"project": str(repo), "status": "MISSING_AGENTS"}
    try:
        text = agents.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return {"project": str(repo), "status": "UNREADABLE_AGENTS"}
    if CANONICAL not in text:
        return {"project": str(repo), "status": "MISSING_CANONICAL_ANCHOR"}
    return {"project": str(repo), "status": "LINK_PRESENT_NOT_READ_VERIFIED"}

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("roots", nargs="+", type=Path)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    results = [examine(p) for p in find_projects(args.roots)]
    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        for result in results:
            print(result["status"], result["project"])
    missing = sum(x["status"] != "LINK_PRESENT_NOT_READ_VERIFIED" for x in results)
    print(f"RUNBOOK_ANCHOR_AUDIT projects={len(results)} missing_or_unknown={missing}")
    print("Read-only link check only; not proof of reading, login, runtime or authorization.")
    return 0 if results and missing == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
