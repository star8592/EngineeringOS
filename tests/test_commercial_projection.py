import sys,tempfile,pathlib,json
sys.path.insert(0,'src/engineeringos')
from commercial_projection import build
from project_journal import append
with tempfile.TemporaryDirectory() as td:
 root=pathlib.Path(td);runtime=root/'runtime';reg=runtime/'projects'/'registry.json';reg.parent.mkdir(parents=True)
 reg.write_text(json.dumps({'schema_version':1,'projects':[{'name':'Kangaroo','repo':'/secret/repo','workspace_root':'/secret/ws','autopilot_enabled':True,'max_assurance':'A2'}]}))
 j=runtime/'projects'/'Kangaroo'/'journal.jsonl'
 append(j,project='Kangaroo',typ='INTENT_RECORDED',key='i',generation=1,payload={'statement':'make training clearer','required_capabilities':['clear training']})
 append(j,project='Kangaroo',typ='WORK_DISCOVERED',key='w1',generation=1,payload={'project':'Kangaroo','kind':'CAPABILITY_PLANNING','intent_id':'i','expected_outcome':'让孩子一眼找到开始训练','requirement':'clear training'})
 a=build(reg,runtime);p=a['products'][0]
 assert p['name']=='Kangaroo' and p['status']=='WORKING' and p['active_work'][0]['text']=='让孩子一眼找到开始训练'
 raw=json.dumps(a,ensure_ascii=False)
 for secret in ('/secret/repo','/secret/ws','source_sha','allowed_paths','verification_argv'):assert secret not in raw
 append(j,project='Kangaroo',typ='WORK_COMMITTED',key='w1',generation=1,payload={'commit_receipt':{},'capability_evidence':['e']})
 append(j,project='Kangaroo',typ='WORK_RESOLVED',key='w1',generation=1,payload={'verifier':'v','resolution_evidence_refs':['e'],'requirement':'clear training'})
 b=build(reg,runtime)['products'][0];assert b['status']=='HEALTHY' and b['recent_completed'][0]['text']=='让孩子一眼找到开始训练'
print('9 commercial-projection invariants passed')
