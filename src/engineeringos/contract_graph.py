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

def validate(m):
 errs=[]
 for name,d in m.get('domains',{}).items():
  for c in d.get('components',[]):
   if c not in m.get('components',{}): errs.append(('MISSING_COMPONENT',name,c))
 return errs
