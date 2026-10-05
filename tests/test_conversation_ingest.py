import sys,tempfile,pathlib
sys.path.insert(0,'src/engineeringos')
from conversation_ingest import *
from durable_supervisor_runtime import discover_work
with tempfile.TemporaryDirectory() as td:
 s=ingest(td,project="P",command_id="m1",conversation_id="c",kind="DESIRE",text="给家长加微信登录",intent_id="wechat",required_capabilities=["parent wechat login"])
 assert s["intents"]["wechat"]["generation"]==1 and s["intents"]["wechat"]["active"] and len(s["conversation_turns"])==1
 first=[x for x in s["work_items"].values() if x["kind"]=="CAPABILITY_PLANNING"];assert len(first)==1 and first[0]["state"]=="DISCOVERED" and "allowed_paths" not in first[0]
 discover_work(td,"P",{"id":"old","project":"P","intent_id":"wechat","intent_generation":1,"kind":"CAPABILITY_GAP","state":"DISCOVERED"})
 discover_work(td,"P",{"id":"busy","project":"P","intent_id":"wechat","intent_generation":1,"kind":"CAPABILITY_GAP","state":"IN_PROGRESS","safe_to_supersede":False})
 # replay starts discovered; persist an in-flight observation for the protected case.
 from project_journal import append
 from durable_supervisor_runtime import journal_path
 append(journal_path(td,"P"),project="P",typ="WORK_STARTED",key="busy",generation=1,payload={})
 s=ingest(td,project="P",command_id="m2",conversation_id="c",kind="CORRECTION",text="只给家长",intent_id="wechat")
 assert s["intents"]["wechat"]["generation"]==2 and s["intents"]["wechat"]["required_capabilities"]==["parent wechat login"]
 assert s["work_items"]["old"]["state"]=="SUPERSEDED"
 assert s["work_items"]["busy"]["state"]=="PROTECT"
 s=ingest(td,project="P",command_id="m3",conversation_id="c",kind="FEEDBACK",text="这里太挤了",intent_id="wechat",artifact_ref="preview:17")
 assert s["intents"]["wechat"]["generation"]==2 and s["conversation_turns"][-1]["artifact_ref"]=="preview:17"
 before=len(s["conversation_turns"])
 retry=ingest(td,project="P",command_id="m3",conversation_id="c",kind="FEEDBACK",text="这里太挤了",intent_id="wechat",artifact_ref="preview:17")
 assert len(retry["conversation_turns"])==before
 try:ingest(td,project="P",command_id="m3",conversation_id="c",kind="FEEDBACK",text="不同内容",intent_id="wechat",artifact_ref="preview:17");raise AssertionError()
 except ConversationCommandError as e:assert str(e)=="IDEMPOTENCY_CONFLICT"
 s=ingest(td,project="P",command_id="m4",conversation_id="c",kind="REVERSAL",text="这个功能不要了",intent_id="wechat")
 assert s["intents"]["wechat"]["generation"]==3 and not s["intents"]["wechat"]["active"]
 s=ingest(td,project="P",command_id="m5",conversation_id="c",kind="APPROVAL",text="这个效果可以",intent_id="wechat")
 assert s["conversation_turns"][-1]["approval_scope"]=="PRODUCT_FEEDBACK_ONLY"
 assert "execution_approval" not in s["conversation_turns"][-1]
 print("18 conversation-ingest invariants passed")
