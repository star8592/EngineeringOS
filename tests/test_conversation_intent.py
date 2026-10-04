import sys
sys.path.insert(0,'src/engineeringos')
from conversation_intent import new_turn,reduce_intent,task_effect
c='c1';i='wechat-parent'
a=new_turn(c,'DESIRE','给家长加微信登录',intent_id=i)
b=new_turn(c,'CORRECTION','不是所有人，只给家长',intent_id=i,supersedes=a.id)
speech=new_turn(c,'INTERRUPTION','行了别念了',intent_id=i,affects_task=False)
assert task_effect(speech)=='KEEP_TASK_YIELD_CONVERSATION'
assert reduce_intent([a,b,speech],i)['active']
assert reduce_intent([a,b,speech],i)['generation']==2
rev=new_turn(c,'REVERSAL','这个功能还是不要了',intent_id=i,supersedes=b.id)
state=reduce_intent([a,b,speech,rev],i)
assert not state['active'];assert state['generation']==3;assert state['latest_direction']['kind']=='REVERSAL'
fb=new_turn(c,'FEEDBACK','这里太挤了',intent_id='home',artifact_ref='preview:home:17')
assert reduce_intent([fb],'home')['feedback'][0]['artifact_ref']=='preview:home:17'
assert task_effect(rev)=='RECONCILE_IN_FLIGHT_TASK'
print('8 conversation-intent invariants passed')
