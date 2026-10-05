import json,pathlib,sys,tempfile
sys.path.insert(0,'src/engineeringos')
from project_router import route
from project_journal import append

with tempfile.TemporaryDirectory() as td:
 root=pathlib.Path(td);runtime=root/'runtime';reg=runtime/'projects'/'registry.json';reg.parent.mkdir(parents=True)
 reg.write_text(json.dumps({'schema_version':1,'projects':[
  {'name':'EngineeringOS','display_name':'AI开发经理','aliases':['EngineeringOS','开发经理'],'repo':'/e','autopilot_enabled':False},
  {'name':'KangarooMath','display_name':'袋鼠数学','aliases':['袋鼠','Math Kangaroo','Kangaroo'],'repo':'/k','autopilot_enabled':False}
 ]},ensure_ascii=False))
 a=route(reg,runtime,text='袋鼠数学，计算训练入口不明显',conversation_id='c1')
 assert a['state']=='ROUTED' and a['project']=='KangarooMath' and a['evidence']=='EXPLICIT_PROJECT_MENTION'
 b=route(reg,runtime,text='AI开发经理，把产品页再简单一点',conversation_id='c2')
 assert b['project']=='EngineeringOS'
 c=route(reg,runtime,text='这个按钮还是不明显',conversation_id='c3')
 assert c['state']=='NEEDS_PROJECT_SELECTION' and c['reason']=='NO_PROJECT_CONTEXT'
 d=route(reg,runtime,text='这个按钮还是不明显',conversation_id='c3',current_project='KangarooMath')
 assert d['project']=='KangarooMath' and d['evidence']=='EXPLICIT_CURRENT_PROJECT'
 j=runtime/'projects'/'KangarooMath'/'journal.jsonl'
 append(j,project='KangarooMath',typ='CONVERSATION_TURN',key='m1',generation=1,payload={'command_id':'m1','conversation_id':'bound','kind':'DESIRE','text':'x','intent_id':'i','artifact_ref':None,'affects_task':True})
 e=route(reg,runtime,text='这里再简单一点',conversation_id='bound')
 assert e['project']=='KangarooMath' and e['evidence']=='DURABLE_CONVERSATION_BINDING'
 f=route(reg,runtime,text='EngineeringOS 和袋鼠数学都看看',conversation_id='c4')
 assert f['state']=='NEEDS_PROJECT_SELECTION' and f['reason']=='MULTIPLE_PROJECT_MENTIONS'
 g=route(reg,runtime,text='这里改一下',conversation_id='bound',current_project='EngineeringOS')
 assert g['project']=='EngineeringOS' and g['evidence']=='EXPLICIT_CURRENT_PROJECT'
 print('14 project-router invariants passed')
