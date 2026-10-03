import sys;sys.path.insert(0,'src/engineeringos')
from reconcile_queue_outcomes import reconcile,authoritative_ci_refs
q={'items':[{'id':'w','kind':'RESOLVE_MAIN_QUALIFICATION','state':'PENDING_RESOLUTION'}]}
ev={'origin_main':'abc','current_head_evidence':{'ci':'SUCCESS','runs':[{'workflowName':'DevControl 3 CI','headSha':'abc','status':'completed','conclusion':'success','createdAt':'2026-10-04T00:00:00Z','url':'https://example/run/1'}]}}
refs=authoritative_ci_refs(ev);assert refs==['github-actions:https://example/run/1','source-sha:abc']
r=reconcile(q,[],ev);assert r==[{'id':'w','reason':'AUTHORITATIVE_CI_SUCCESS'}]
x=q['items'][0];assert x['state']=='RESOLVED' and x['resolved_by']=='engineeringos-authoritative-ci-reconciler' and x['closure_kind']=='AUTHORITATIVE_CI_SUCCESS'
q2={'items':[{'id':'w','kind':'RESOLVE_MAIN_QUALIFICATION','state':'PENDING_RESOLUTION'}]};ev2={'origin_main':'abc','current_head_evidence':{'ci':'IN_PROGRESS','runs':[]}}
assert reconcile(q2,[],ev2)==[] and q2['items'][0]['state']=='PENDING_RESOLUTION'
print('5 authoritative-evidence queue reconciliation invariants passed')
