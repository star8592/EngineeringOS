import sys,tempfile,pathlib
sys.path.insert(0,'src/engineeringos')
from project_journal import append,events
from project_replay import replay_project
from event_store import EventStoreError
with tempfile.TemporaryDirectory() as td:
 p=pathlib.Path(td)/"p.jsonl"
 append(p,project="P",typ="INTENT_RECORDED",key="i",generation=1,payload={"statement":"make chat","required_capabilities":["chat"]})
 append(p,project="P",typ="WORK_DISCOVERED",key="gap-a",generation=1,payload={"kind":"CAPABILITY_GAP","intent_id":"i","requirement":"chat"})
 append(p,project="P",typ="WORK_WAITING_PROVIDER",key="gap-a",generation=1,payload={"reason":"WAITING_PROVIDER"})
 append(p,project="P",typ="INTENT_REVISED",key="i",generation=2,payload={"statement":"voice first","required_capabilities":["voice"]})
 append(p,project="P",typ="WORK_SUPERSEDED",key="gap-a",generation=2,payload={"superseded_by":"i@2"})
 s=replay_project(events(p));assert s["last_seq"]==5;assert s["intents"]["i"]["generation"]==2;assert s["intents"]["i"]["statement"]=="voice first";assert s["work_items"]["gap-a"]["state"]=="SUPERSEDED"
 try: append(p,project="P",typ="WORK_DISCOVERED",key="x",payload={},expected_version=2);raise AssertionError()
 except EventStoreError as e: assert str(e)=="VERSION_CONFLICT"
 s2=replay_project(events(p));assert s2==s
 print("8 project-journal invariants passed")
