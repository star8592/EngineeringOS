import json,pathlib,sys,tempfile
sys.path.insert(0,'src/engineeringos')
from durable_run import arm_run,read_run
from external_wakeup import record_external_wait,wake

with tempfile.TemporaryDirectory() as td:
 root=pathlib.Path(td);arm_run(root,'P',intent_id='i',conversation_id='c',command_id='m')
 cp=root/'projects'/'P'/'continuous.json';cp.write_text(json.dumps({'next_eligible_at':9999999999,'last_result':'MACHINE_FAILURE'}))
 record_external_wait(root,'P',kind='GITHUB_CI',correlation_id='run-42')
 assert read_run(root,'P')['state']=='WAITING_EXTERNAL'
 out=wake(root,'P',kind='GITHUB_CI',correlation_id='run-42',detail={'conclusion':'success'})
 assert out['state']=='WOKEN' and read_run(root,'P')['state']=='ARMED'
 assert json.loads(cp.read_text())['next_eligible_at']==0
 lines=(root/'projects'/'P'/'wake-events.jsonl').read_text().splitlines()
 assert [json.loads(x)['type'] for x in lines]==['WAIT','WAKE']
 print('external wakeup invariants passed')
