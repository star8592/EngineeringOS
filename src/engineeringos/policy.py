from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any

@dataclass(frozen=True)
class PolicyDecision:
    policy: str
    state: str
    severity: str
    reason: str
    evidence: dict[str, Any]
    def to_dict(self): return asdict(self)

def source_production_drift(source_version:str, production_version:str, release_resolved:bool, runtime_consistent:bool)->PolicyDecision:
    if not runtime_consistent:
        return PolicyDecision('source-production-drift','BLOCK','critical','production identity endpoints disagree',{'source':source_version,'production':production_version})
    if source_version == production_version:
        return PolicyDecision('source-production-drift','OK','info','source and production versions agree',{'source':source_version,'production':production_version})
    if not release_resolved:
        return PolicyDecision('source-production-drift','REVIEW','high','production differs from source and provenance is unresolved',{'source':source_version,'production':production_version})
    return PolicyDecision('source-production-drift','ACCEPTABLE_DRIFT','info','production is evidenced and source is ahead; release cadence policy may decide whether action is due',{'source':source_version,'production':production_version})
