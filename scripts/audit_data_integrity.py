#!/usr/bin/env python3
"""Read-only cross-project preflight, never mutates repositories or creates data."""
from __future__ import annotations
import argparse
import json
import re
import subprocess
from pathlib import Path

INCLUDED={".py",".rs",".ts",".tsx",".js",".jsx",".sql",".go",".java",".sh",".yaml",".yml",".html"}
SKIP={".git",".venv","node_modules","dist","target","build","coverage","vendor","__pycache__"}
CHECKS=[
 ("business_price_literal",re.compile(r"(?:price|service_fee|subscription_fee|金额|定价)\s*[:=]\s*[\"']?\d{3,}",re.I)),
 ("business_year_literal",re.compile(r"(?:admission_year|report_year|business_year|招生年份|业务年度)\s*[:=]\s*[\"']?20\d{2}",re.I)),
 ("embedded_connection",re.compile(r"(?:localhost|127\.0\.0\.1):\d{2,5}|(?:DATABASE_URL|DB_URL|DB_DSN)\s*[:=]\s*[\"']?(?:postgres|sqlite|mysql)",re.I)),
 ("fabricated_business_seed",re.compile(r"\b(?:faker|factory_boy|mock_customer|fake_student|seed_demo|fixture_user|fake_order|mock_balance)\b",re.I)),
 ("implicit_local_database",re.compile(r"(?:sqlite3\.connect|DATABASE_URL.*sqlite|DB_URL.*sqlite)",re.I)),
]
def scan(repo:Path):
    hits=[]
    for p in repo.rglob("*"):
        if not p.is_file() or p.suffix not in INCLUDED or any(part in SKIP for part in p.relative_to(repo).parts):continue
        if p.name==Path(__file__).name:continue
        if p.stat().st_size>1_000_000:continue
        try: data=p.read_text(encoding="utf-8")
        except UnicodeError:continue
        for n,line in enumerate(data.splitlines(),1):
            for label,pattern in CHECKS:
                if pattern.search(line):
                    hits.append({"path":str(p.relative_to(repo)),"line":n,"kind":label})
    return hits
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("repo_paths",nargs="+",type=Path)
    ap.add_argument("--json",action="store_true")
    args=ap.parse_args()
    items=[]
    for p in args.repo_paths:
        if not p.is_dir():
            items.append({"repo":str(p),"status":"not_found","findings":[]})
        else:
            findings=scan(p)
            items.append({"repo":str(p),"status":"candidate_findings" if findings else "no_candidates_detected",
                          "findings":findings})
    if args.json:print(json.dumps(items,indent=2,ensure_ascii=False))
    else:
        for it in items:print(it["repo"],it["status"],len(it["findings"]))
    print("NOTE: heuristics identify potential problems; not proof of compliance. No data modified.")
    return 1 if any(it["findings"] or it["status"]=="not_found" for it in items) else 0
if __name__=="__main__":
    raise SystemExit(main())
