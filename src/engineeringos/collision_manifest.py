from __future__ import annotations
import json,pathlib

def load(path):
 d=json.load(open(path)); assert d.get('schema_version')==1
 return d

def semantic_paths(manifest, domains):
 out=set()
 for d in domains: out.update(manifest.get('domains',{}).get(d,{}).get('paths',[]))
 return out
