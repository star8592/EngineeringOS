from __future__ import annotations

def validate(items):
    ids={x['id'] for x in items}; errs=[]
    for x in items:
        for d in x.get('depends_on',[]):
            if d not in ids: errs.append(('MISSING_DEPENDENCY',x['id'],d))
            if d==x['id']: errs.append(('SELF_DEPENDENCY',x['id'],d))
    # DFS cycle detection
    g={x['id']:[d for d in x.get('depends_on',[]) if d in ids] for x in items}; visiting=set(); done=set()
    def dfs(n,path):
        if n in visiting: errs.append(('DEPENDENCY_CYCLE',tuple(path+[n]))); return
        if n in done:return
        visiting.add(n)
        for d in g[n]: dfs(d,path+[n])
        visiting.remove(n); done.add(n)
    for n in g: dfs(n,[])
    return errs

def readiness(item, by_id):
    blockers=[]
    for d in item.get('depends_on',[]):
        dep=by_id.get(d)
        if dep is None or dep.get('state') not in ('RESOLVED','SUPERSEDED'): blockers.append(d)
    if blockers:return {'state':'BLOCKED','blocked_by':blockers}
    if item.get('state') in ('DISCOVERED','REOPENED'): return {'state':'READY','blocked_by':[]}
    return {'state':item.get('state','UNKNOWN'),'blocked_by':[]}
