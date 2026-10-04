import sys
sys.path.insert(0,'src/engineeringos')
from intent_revision import *
items=[
 {"id":"old-safe","intent_id":"home","intent_generation":1,"state":"DISCOVERED"},
 {"id":"old-flight","intent_id":"home","intent_generation":1,"state":"IN_PROGRESS"},
 {"id":"old-proven-safe","intent_id":"home","intent_generation":1,"state":"IN_PROGRESS","safe_to_supersede":True},
 {"id":"other","intent_id":"login","intent_generation":1,"state":"DISCOVERED"}]
r=reconcile_revision(intent_id="home",generation=2,active=True,latest_direction="move button below",work_items=items,evidence_ref="turn:t2")
assert set(r["superseded"])=={"old-safe","old-proven-safe"}
assert r["protected"]==["old-flight"] and items[1]["state"]=="PROTECT"
assert items[3]["state"]=="DISCOVERED"
n=make_revision_work(project="EngineeringOS",intent_id="home",generation=2,statement="move button below",requirement="home preview")
assert n["intent_generation"]==2 and n["state"]=="DISCOVERED"
assert n["id"]==make_revision_work(project="EngineeringOS",intent_id="home",generation=2,statement="move button below",requirement="home preview")["id"]
print('8 intent-revision invariants passed')
