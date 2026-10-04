#!/usr/bin/env python3
import argparse,json,sys,pathlib
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"src"/"engineeringos"))
from project_doctor import inspect_project,render_plain
p=argparse.ArgumentParser();p.add_argument("project");p.add_argument("--name");p.add_argument("--json",action="store_true");a=p.parse_args()
r=inspect_project(a.project,a.name);print(json.dumps(r,ensure_ascii=False,indent=2) if a.json else render_plain(r))
