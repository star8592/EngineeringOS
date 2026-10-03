from __future__ import annotations
import os,pathlib

REPO_ROOT=pathlib.Path(__file__).resolve().parents[2]
# Mutable live state must never dirty the repository. Tests/operators may override it.
RUNTIME_ROOT=pathlib.Path(os.environ.get('ENGINEERINGOS_RUNTIME_ROOT', REPO_ROOT/'.engineeringos/runtime'))
BASELINE_ROOT=REPO_ROOT/'.engineeringos'
OUTCOME_LEDGER=BASELINE_ROOT/'outcomes.jsonl'

def runtime(*parts: str) -> pathlib.Path:
    return RUNTIME_ROOT.joinpath(*parts)
