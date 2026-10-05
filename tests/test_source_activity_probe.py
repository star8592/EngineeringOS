import os,pathlib,sys,tempfile
sys.path.insert(0,'src/engineeringos')
from source_activity_probe import probe

with tempfile.TemporaryDirectory() as td:
 root=pathlib.Path(td);repo=root/'repo';repo.mkdir();proc=root/'proc';proc.mkdir()
 # Self + ancestor are ignored.
 for pid,ppid in [(100,50),(50,1)]:
  p=proc/str(pid);p.mkdir();(p/'stat').write_text(f'{pid} (x) S {ppid} 0 0 0');(p/'cmdline').write_bytes(b'python\0');(p/'fd').mkdir();(p/'fdinfo').mkdir()
 # Another process referencing repo is blocked.
 p=proc/'200';p.mkdir();(p/'stat').write_text('200 (x) S 1 0 0 0');(p/'cmdline').write_bytes(('tool '+str(repo)).encode());(p/'fd').mkdir();(p/'fdinfo').mkdir()
 out=probe(repo,proc_root=proc,self_pid=100)
 assert out['state']=='ACTIVE_REFERENCES' and out['active_reference_count']==1 and out['references'][0]['pid']==200
 (p/'cmdline').write_bytes(b'other\0')
 out2=probe(repo,proc_root=proc,self_pid=100)
 assert out2['state']=='QUIET' and out2['active_reference_count']==0
print('5 source-activity-probe invariants passed')
