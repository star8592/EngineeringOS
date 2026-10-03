from __future__ import annotations

def normalize(paths): return {p.strip().lstrip('./') for p in paths if p and p.strip()}
def overlap(planned, active):
    p,a=normalize(planned),normalize(active); common=sorted(p&a)
    return {'planned_count':len(p),'active_count':len(a),'overlap_count':len(common),'overlap_paths':common,'collision':bool(common)}
def dispatch_collision_decision(planned, active, active_dirty=True):
    o=overlap(planned,active)
    if active_dirty and o['collision']:
        return {**o,'state':'BLOCKED_BY_ACTIVE_LINE','required_action':'ISOLATE_OR_WAIT'}
    return {**o,'state':'CLEAR','required_action':None}
