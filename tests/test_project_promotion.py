import pathlib,sys,tempfile,json
sys.path.insert(0,'src/engineeringos')
from project_promotion import assess,assess_registered

base={'state':'CLEAN_CONNECTED','origin':'https://example/P.git','branch':'main','upstream':'origin/main','ahead':0,'behind':0,'head':'abc','verification_entrypoints':['verify:public']}
cfg={'name':'P','display_name':'产品P','repo':'/tmp/P','management_target':'A2_MANAGED','expected_origin':'https://example/P.git','managed_branch':'main','a2_verification_entrypoint':'verify:public','max_assurance':'A2','workspace_root':'/tmp/ws'}
assert assess({**cfg,'management_target':'CONNECTED_READ_ONLY'},base)['state']=='NOT_REQUESTED'
assert assess(cfg,{**base,'state':'PROTECTED_EXISTING_WORK'})['reason']=='PROTECTED_EXISTING_WORK'
assert assess(cfg,{**base,'origin':'https://evil/P.git'})['reason']=='ORIGIN_DRIFT'
assert assess(cfg,{**base,'branch':'dev'})['reason']=='BRANCH_DRIFT'
assert assess(cfg,{**base,'behind':1})['reason']=='UPSTREAM_DIVERGENCE'
assert assess({**cfg,'a2_verification_entrypoint':'verify:missing'},base)['reason']=='A2_VERIFICATION_ENTRYPOINT_DRIFT'
assert assess({**cfg,'max_assurance':'A3'},base)['reason']=='SAFE_ASSURANCE_CEILING_REQUIRED'
assert assess({k:v for k,v in cfg.items() if k!='workspace_root'},base)['reason']=='WORKSPACE_ROOT_REQUIRED'
ok=assess(cfg,base);assert ok['state']=='ELIGIBLE_FOR_A2' and ok['eligible'] and ok['baseline_head']=='abc'
with tempfile.TemporaryDirectory() as td:
 r=pathlib.Path(td);reg=r/'registry.json';rt=r/'rt';(rt/'projects'/'P').mkdir(parents=True)
 reg.write_text(json.dumps({'schema_version':1,'projects':[cfg]}));(rt/'projects'/'P'/'baseline.json').write_text(json.dumps(base))
 out=assess_registered(reg,rt);assert out['projects'][0]['eligible']
print('11 project-promotion invariants passed')
