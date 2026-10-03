import json,pathlib,tempfile,sys
sys.path.insert(0,'src/engineeringos')
from supervisor import build_action_brief,make_timeseries_row,make_timeseries_summary,append_jsonl_once
snapshot={'run_id':'r1','observed_at':'2026-10-04T00:00:00+00:00','content_sha256':'abc','source_head':'deadbeef','manager_summary':{'qualification':'PASS'},'debt_counts':{'dirty_workspace':10,'overlap':4},'dispatchable_count':2}
queue={'items':[
 {'id':'b','priority':2,'kind':'B','state':'DISCOVERED','reason':'second','required_assurance':'A1','automation':'REVIEW'},
 {'id':'a','priority':1,'kind':'A','state':'DISCOVERED','reason':'first','required_assurance':'A2','automation':'REVIEW'},
 {'id':'z','priority':0,'kind':'DONE','state':'RESOLVED','reason':'done','required_assurance':'A1','automation':'REVIEW'}]}
dispatch={'items':[{'id':'a','schedule_state':'DISPATCHABLE','lane':'REASONING_REVIEW'},{'id':'b','schedule_state':'BLOCKED'}]}
loop={'summary':{'items':2,'succeeded':1,'blocked':1}}
brief=build_action_brief(queue,dispatch,snapshot)
assert [x['id'] if 'id' in x else x['item_id'] for x in brief['actions']]==['a','b']
assert brief['active_work_items']==2 and brief['actions'][0]['priority']==1
row=make_timeseries_row(snapshot,queue,dispatch,loop)
assert row['queue_states']=={'DISCOVERED':2,'RESOLVED':1}
assert row['schedule_states']=={'BLOCKED':1,'DISPATCHABLE':1}
row2=dict(row);row2['run_id']='r2';row2['observed_at']='2026-10-04T00:05:00+00:00';row2['debt_counts']={'dirty_workspace':8,'overlap':5}
summary=make_timeseries_summary([row,row2])
assert summary['debt_delta']=={'dirty_workspace':-2,'overlap':1}
with tempfile.TemporaryDirectory() as d:
 p=pathlib.Path(d)/'series.jsonl'
 assert append_jsonl_once(p,row,'run_id') is True
 assert append_jsonl_once(p,row,'run_id') is False
 assert len(p.read_text().splitlines())==1
print('8 supervisor invariants passed')
