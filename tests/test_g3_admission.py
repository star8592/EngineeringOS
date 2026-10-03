import sys;sys.path.insert(0,'src/engineeringos')
from g3_admission import load_policy,assess
P=load_policy('project_profiles/devcontrol/g3-tool-policy.json')
def a(action,**kw): return assess(P,action=action,backend=kw.pop('backend','DevControl'),**kw)
assert a('refresh_evidence')['decision']=='ALLOW'
assert a('run_deterministic_checks',declared_annotations={'read_only_hint':True})['decision']=='ALLOW'
req={'lease','collision_clear','idempotency_key','execution_receipt','outcome_probe'}
assert a('create_isolated_worktree',runtime_contracts=req)['decision']=='ALLOW'
assert a('create_isolated_worktree',runtime_contracts={'lease'})['reason']=='MISSING_RUNTIME_CONTRACTS'
assert a('create_isolated_worktree',runtime_contracts=req,declared_annotations={'read_only_hint':True})['reason']=='TOOL_METADATA_CONTRADICTION'
assert a('delete_branch')['reason']=='OUTSIDE_G3_BOUNDARY'
assert a('deploy_production')['reason']=='OUTSIDE_G3_BOUNDARY'
assert a('not_a_tool')['reason']=='UNKNOWN_ACTION'
assert a('refresh_evidence',backend='RemoteDesktopCommander')['reason']=='EXECUTION_BACKEND_DRIFT'
Q=dict(P);Q['approval_authority']='DASHBOARD';assert assess(Q,action='refresh_evidence',backend='DevControl')['reason']=='APPROVAL_AUTHORITY_DRIFT'
print('10 G3 admission/tool-approval invariants passed')
