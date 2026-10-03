from __future__ import annotations
import json

def load(path):
 d=json.load(open(path)); assert d.get('schema_version')==2; return d

def expand_domain(m, domain):
 d=m.get('domains',{}).get(domain,{})
 components=set(d.get('components',[])); contracts=set(d.get('contracts',[])); paths=set(d.get('paths',[])); artifacts=set(d.get('artifacts',[]))
 for c in components:
  x=m.get('components',{}).get(c,{}); paths.update(x.get('paths',[])); contracts.update(x.get('contracts',[])); artifacts.update(x.get('artifacts',[]))
 return {'components':components,'contracts':contracts,'paths':paths,'artifacts':artifacts}

def assess_domains(m, planned_domains, active_paths):
 a=set(active_paths); hits=[]
 for name in planned_domains:
  x=expand_domain(m,name); touched=sorted(a & x['paths'])
  if touched: hits.append({'domain':name,'paths':touched,'contracts':sorted(x['contracts']),'artifacts':sorted(x['artifacts'])})
 return hits

def edges(m, relation=None):
 es=m.get('edges',[])
 return [e for e in es if relation is None or e.get('relation')==relation]

def impacted_nodes(m, changed_nodes):
 """Forward impact closure across evidence-declared semantic edges."""
 rels={'generates','implements','consumes','depends_on','runtime_binding'}; seen=set(changed_nodes); changed=True
 while changed:
  changed=False
  for e in m.get('edges',[]):
   if e.get('relation') in rels and e.get('from') in seen and e.get('to') not in seen:
    seen.add(e['to']);changed=True
 return seen

def validate(m):
 errs=[]; nodes=set()
 for kind in ('components','contracts','artifacts','runtime_bindings'): nodes.update(f'{kind[:-1]}:{x}' for x in m.get(kind,{}))
 for name,d in m.get('domains',{}).items():
  for c in d.get('components',[]):
   if c not in m.get('components',{}): errs.append(('MISSING_COMPONENT',name,c))
 for e in m.get('edges',[]):
  if e.get('from') not in nodes: errs.append(('MISSING_EDGE_SOURCE',e.get('from')))
  if e.get('to') not in nodes: errs.append(('MISSING_EDGE_TARGET',e.get('to')))
  if e.get('relation') not in {'depends_on','generates','implements','consumes','owns','runtime_binding'}: errs.append(('UNKNOWN_RELATION',e.get('relation')))
 return errs
