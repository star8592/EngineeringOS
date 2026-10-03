from __future__ import annotations
# Minimal explicit contract domains; later adapters can derive these from manifests/graphs.
DOMAINS={
 'release_identity':{'VERSION','Cargo.toml','Cargo.lock','scripts/deploy_production.sh','scripts/stage_server_package.sh','scripts/stage_agent_package.sh'},
 'release_qualification':{'scripts/deploy_production.sh','scripts/check_release_pipeline_contract.sh','scripts/test_server_package.sh'},
}
def assess(planned_paths,active_paths,planned_domains):
 p=set(planned_paths); a=set(active_paths); exact=sorted(p&a); semantic=[]
 for d in planned_domains:
  touched=sorted(a & DOMAINS.get(d,set()))
  if touched: semantic.append({'domain':d,'active_paths':touched})
 state='BLOCKED_BY_SEMANTIC_COLLISION' if semantic else ('BLOCKED_BY_ACTIVE_LINE' if exact else 'CLEAR')
 return {'state':state,'exact_overlap':exact,'semantic_overlap':semantic,'required_action':'ISOLATE_OR_WAIT' if state!='CLEAR' else None}
