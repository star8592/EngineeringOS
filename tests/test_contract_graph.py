import sys;sys.path.insert(0,'src/engineeringos')
from contract_graph import *
m=load('project_profiles/devcontrol/contract-graph.json');assert validate(m)==[]
x=expand_domain(m,'release_identity');assert 'VERSION' in x['paths'] and 'artifact-integrity' in x['contracts'] and 'server-package' in x['artifacts']
h=assess_domains(m,['release_identity'],['Cargo.toml','unrelated']);assert h and h[0]['paths']==['Cargo.toml']
assert len(edges(m,'generates'))==5
impact=impacted_nodes(m,{'component:server_packaging'});assert 'artifact:server-package' in impact and 'contract:artifact-integrity' in impact
print('6 contract-graph invariants passed')
