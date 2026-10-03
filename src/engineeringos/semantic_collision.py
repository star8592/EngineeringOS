from __future__ import annotations
from collision_manifest import semantic_paths

def assess(planned_paths,active_paths,planned_domains,manifest):
 p=set(planned_paths); a=set(active_paths); exact=sorted(p&a); semantic=[]
 for d in planned_domains:
  touched=sorted(a & semantic_paths(manifest,[d]))
  if touched: semantic.append({'domain':d,'active_paths':touched})
 state='BLOCKED_BY_SEMANTIC_COLLISION' if semantic else ('BLOCKED_BY_ACTIVE_LINE' if exact else 'CLEAR')
 return {'state':state,'exact_overlap':exact,'semantic_overlap':semantic,'required_action':'ISOLATE_OR_WAIT' if state!='CLEAR' else None}
