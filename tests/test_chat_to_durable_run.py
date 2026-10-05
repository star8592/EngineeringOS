import json,pathlib,sys,tempfile
sys.path.insert(0,'src/engineeringos')
from conversation_gateway import submit
from durable_run import read_run,reconcile_run

with tempfile.TemporaryDirectory() as td:
 root=pathlib.Path(td);runtime=root/'runtime';reg=runtime/'projects'/'registry.json';reg.parent.mkdir(parents=True)
 reg.write_text(json.dumps({'schema_version':1,'projects':[{'name':'P','display_name':'项目P','aliases':['项目P'],'repo':'/p','autopilot_enabled':True,'workspace_root':'/tmp/p-ws','max_assurance':'A2'}]},ensure_ascii=False))
 out=submit(reg,runtime,command_id='m1',conversation_id='c1',current_project='P',text='把项目推进到可以交付',kind='DESIRE')
 run=read_run(runtime,'P')
 assert out['state']=='ACCEPTED' and run['state']=='ARMED' and run['intent_id']==out['intent_id']
 # “继续” must not be the mechanism that advances work or create another run.
 again=submit(reg,runtime,command_id='m2',conversation_id='c1',current_project='P',text='继续',kind=None)
 assert again['state']=='CONTINUE_EXISTING_WORK' and read_run(runtime,'P')['run_id']==run['run_id']
 st=out['project_state'];wid=next(iter(st['work_items']))
 st['work_items'][wid]['state']='RESOLVED'
 done=reconcile_run(runtime,'P',st,{'action':'OBSERVE'})
 assert done['state']=='ACCEPTED' and done['last_action']=='ACCEPTANCE_CONTRACT_SATISFIED'
 print('chat-to-durable-run acceptance invariants passed')
