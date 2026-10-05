import json,os,pathlib,sys,tempfile
sys.path.insert(0,'src/engineeringos')
import dashboard_projector as dp

with tempfile.TemporaryDirectory() as td:
 root=pathlib.Path(td);rt=root/'runtime';(rt/'projects').mkdir(parents=True)
 (rt/'projects'/'registry.json').write_text(json.dumps({'schema_version':1,'projects':[{'name':'P','display_name':'产品P','repo':'/tmp/P','autopilot_enabled':False}]}))
 b=rt/'backends'/'DevControl';b.mkdir(parents=True)
 (b/'surface-evidence.json').write_text(json.dumps({'state':'TOOL_SURFACE_DRIFT'}))
 (b/'freshness.json').write_text(json.dumps({'state':'HOST_OBSERVATION_STALE'}))
 old_runtime,old_root,old_cwd=dp.runtime,dp.RUNTIME_ROOT,os.getcwd()
 try:
  os.chdir(root);(root/'dashboard'/'runtime').mkdir(parents=True)
  dp.runtime=lambda *parts: rt.joinpath(*parts);dp.RUNTIME_ROOT=rt
  out=dp.project_fast()
  assert out['products']==1 and out['commercial_products']==1
  assert out['devcontrol_surface_state']=='TOOL_SURFACE_DRIFT'
  assert out['devcontrol_surface_freshness']=='HOST_OBSERVATION_STALE'
  assert json.loads((root/'dashboard/runtime/commercial.json').read_text())['products'][0]['name']=='产品P'
  assert not (root/'dashboard/runtime/snapshot.json').exists()
 finally:
  dp.runtime=old_runtime;dp.RUNTIME_ROOT=old_root;os.chdir(old_cwd)
 print('7 fast-dashboard-projection invariants passed')
