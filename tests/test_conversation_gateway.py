import json,pathlib,sys,tempfile
sys.path.insert(0,'src/engineeringos')
from conversation_gateway import submit
from conversation_ingest import ConversationCommandError
from project_journal import events

with tempfile.TemporaryDirectory() as td:
 root=pathlib.Path(td);runtime=root/'runtime';reg=runtime/'projects'/'registry.json';reg.parent.mkdir(parents=True)
 reg.write_text(json.dumps({'schema_version':1,'projects':[
  {'name':'EngineeringOS','display_name':'AI开发经理','aliases':['开发经理'],'repo':'/e','autopilot_enabled':False},
  {'name':'KangarooMath','display_name':'袋鼠数学','aliases':['袋鼠','Math Kangaroo'],'repo':'/k','autopilot_enabled':False}
 ]},ensure_ascii=False))
 a=submit(reg,runtime,command_id='m1',conversation_id='chat-1',text='袋鼠数学，计算训练入口还是不明显',kind='DESIRE')
 assert a['state']=='ACCEPTED' and a['project']=='KangarooMath' and a['intent_id'].startswith('intent-') and a['durable_write']
 st=a['project_state'];assert len(st['intents'])==1 and len(st['work_items'])==1
 intent=a['intent_id'];work=list(st['work_items'].values())[0]
 assert work['requirement']=='袋鼠数学，计算训练入口还是不明显'
 # An identical network retry is idempotent: no journal growth.
 before=len(events(runtime/'projects'/'KangarooMath'/'journal.jsonl'))
 retry=submit(reg,runtime,command_id='m1',conversation_id='chat-1',text='袋鼠数学，计算训练入口还是不明显',kind='DESIRE')
 after=len(events(runtime/'projects'/'KangarooMath'/'journal.jsonl'))
 assert retry['state']=='ACCEPTED' and before==after
 try:
  submit(reg,runtime,command_id='m1',conversation_id='chat-1',text='袋鼠数学，换一个需求',kind='DESIRE')
  raise AssertionError()
 except ConversationCommandError as e:assert str(e)=='IDEMPOTENCY_CONFLICT'
 # Follow-up correction binds to the recent intent and same durable project.
 b=submit(reg,runtime,command_id='m2',conversation_id='chat-1',text='不是放大按钮，是让孩子一眼知道从哪里开始',kind='CORRECTION')
 assert b['project']=='KangarooMath' and b['intent_id']==intent and b['project_state']['intents'][intent]['generation']==2
 # Process control never creates a product turn.
 before=len(events(runtime/'projects'/'KangarooMath'/'journal.jsonl'))
 c=submit(reg,runtime,command_id='m3',conversation_id='chat-1',text='继续',kind=None)
 after=len(events(runtime/'projects'/'KangarooMath'/'journal.jsonl'))
 assert c['state']=='CONTINUE_EXISTING_WORK' and not c['durable_write'] and before==after
 # A new unbound multi-project utterance does not guess.
 d=submit(reg,runtime,command_id='m4',conversation_id='chat-2',text='这个首页再简单点',kind='DESIRE')
 assert d['state']=='NEEDS_PROJECT_SELECTION' and not d['durable_write']
 # Explicit current project resolves ordinary contextual language.
 e=submit(reg,runtime,command_id='m5',conversation_id='chat-2',current_project='EngineeringOS',text='这个首页再简单点',kind='DESIRE')
 assert e['state']=='ACCEPTED' and e['project']=='EngineeringOS'
 print('18 conversation-gateway invariants passed')
