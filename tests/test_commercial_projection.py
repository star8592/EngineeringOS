import sys,tempfile,pathlib,json
sys.path.insert(0,'src/engineeringos')
from commercial_projection import build
from project_journal import append
with tempfile.TemporaryDirectory() as td:
 root=pathlib.Path(td);runtime=root/'runtime';reg=runtime/'projects'/'registry.json';reg.parent.mkdir(parents=True)
 reg.write_text(json.dumps({'schema_version':1,'projects':[{'name':'Kangaroo','display_name':'袋鼠数学','repo':'/secret/repo','workspace_root':'/secret/ws','autopilot_enabled':True,'max_assurance':'A2'}]}))
 j=runtime/'projects'/'Kangaroo'/'journal.jsonl'
 append(j,project='Kangaroo',typ='INTENT_RECORDED',key='i',generation=1,payload={'statement':'make training clearer','required_capabilities':['clear training']})
 append(j,project='Kangaroo',typ='WORK_DISCOVERED',key='w1',generation=1,payload={'project':'Kangaroo','kind':'CAPABILITY_PLANNING','intent_id':'i','expected_outcome':'让孩子一眼找到开始训练','requirement':'clear training'})
 a=build(reg,runtime);p=a['products'][0]
 assert p['name']=='袋鼠数学' and p['status']=='WORKING' and p['active_work'][0]['text']=='让孩子一眼找到开始训练'
 raw=json.dumps(a,ensure_ascii=False)
 for secret in ('/secret/repo','/secret/ws','source_sha','allowed_paths','verification_argv'):assert secret not in raw
 append(j,project='Kangaroo',typ='WORK_COMMITTED',key='w1',generation=1,payload={'commit_receipt':{},'capability_evidence':['e']})
 append(j,project='Kangaroo',typ='WORK_RESOLVED',key='w1',generation=1,payload={'verifier':'v','resolution_evidence_refs':['e'],'requirement':'clear training'})
 b=build(reg,runtime)['products'][0];assert b['status']=='HEALTHY' and b['recent_completed'][0]['text']=='让孩子一眼找到开始训练'
 reg.write_text(json.dumps({'schema_version':1,'projects':[{'name':'Kangaroo','display_name':'袋鼠数学','repo':'/secret/repo','workspace_root':'/secret/ws','autopilot_enabled':True,'max_assurance':'A2'},{'name':'Other','display_name':'另一个产品','repo':'/secret/other','autopilot_enabled':False}]}))
 c=build(reg,runtime)['products'][1];assert c['name']=='另一个产品' and c['status']=='CONNECTED'
 op=runtime/'projects'/'Other'/'baseline.json';op.parent.mkdir(parents=True,exist_ok=True);op.write_text(json.dumps({'schema_version':1,'project':'Other','state':'PROTECTED_EXISTING_WORK'}))
 c2=build(reg,runtime)['products'][1];assert c2['status']=='PROTECTED' and '不会覆盖' in c2['management_note']
 op.write_text(json.dumps({'schema_version':1,'project':'Other','state':'CLEAN_CONNECTED'}))
 c3=build(reg,runtime)['products'][1];assert c3['status']=='BASELINED' and '安全基线' in c3['management_note']
 # Active work on a disabled clean project is queued, not falsely shown as being developed.
 j2=runtime/'projects'/'Other'/'journal.jsonl'
 append(j2,project='Other',typ='INTENT_RECORDED',key='i2',generation=1,payload={'statement':'queued','required_capabilities':['q']})
 append(j2,project='Other',typ='WORK_DISCOVERED',key='w2',generation=1,payload={'project':'Other','kind':'CAPABILITY_PLANNING','intent_id':'i2','expected_outcome':'待处理需求','requirement':'q'})
 c4=build(reg,runtime)['products'][1];assert c4['status']=='QUEUED' and '尚未生效' in c4['management_note']
 op.write_text(json.dumps({'schema_version':1,'project':'Other','state':'PROTECTED_EXISTING_WORK'}))
 c5=build(reg,runtime)['products'][1];assert c5['status']=='PROTECTED' and '不会覆盖' in c5['management_note']
 # A2 target is the durable authorization goal: promotion evidence makes management effective without a second switch.
 reg.write_text(json.dumps({'schema_version':1,'projects':[{'name':'Kangaroo','display_name':'袋鼠数学','repo':'/secret/repo','workspace_root':'/secret/ws','autopilot_enabled':True,'max_assurance':'A2'},{'name':'Other','display_name':'另一个产品','repo':'/secret/other','autopilot_enabled':False,'management_target':'A2_MANAGED','workspace_root':'/tmp/ws','max_assurance':'A2'}]}))
 op.write_text(json.dumps({'schema_version':1,'project':'Other','state':'CLEAN_CONNECTED'}))
 pp=runtime/'projects'/'Other'/'promotion.json';pp.write_text(json.dumps({'schema_version':1,'project':'Other','state':'ELIGIBLE_FOR_A2','eligible':True}))
 # remove active work by resolving it so effective management becomes user-facing
 append(j2,project='Other',typ='WORK_COMMITTED',key='w2',generation=1,payload={'commit_receipt':{},'capability_evidence':['e2']})
 append(j2,project='Other',typ='WORK_RESOLVED',key='w2',generation=1,payload={'verifier':'v','resolution_evidence_refs':['e2'],'requirement':'q'})
 c6=build(reg,runtime)['products'][1];assert c6['status']=='HEALTHY' and c6['autopilot_enabled'] is True
 pp.write_text(json.dumps({'schema_version':1,'project':'Other','state':'BLOCKED','eligible':False,'reason':'ORIGIN_DRIFT'}))
 c7=build(reg,runtime)['products'][1];assert c7['status']=='MANAGEMENT_BLOCKED' and c7['autopilot_enabled'] is False and '安全门' in c7['management_note']
 print('27 commercial-projection invariants passed')
