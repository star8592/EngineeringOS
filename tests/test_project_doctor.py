import sys,tempfile,pathlib,subprocess
sys.path.insert(0,'src/engineeringos')
from project_doctor import inspect_project,render_plain
with tempfile.TemporaryDirectory() as td:
 p=pathlib.Path(td)/'my-tool';p.mkdir();(p/'package.json').write_text('{}');r=inspect_project(str(p),'My Tool')
 assert not r['detected']['has_change_history'];assert r['user_engineering_burden']['required_engineering_actions']==0;assert 'Git' not in render_plain(r);assert any(x['id']=='no-history' for x in r['findings'])
with tempfile.TemporaryDirectory() as td:
 p=pathlib.Path(td)/'repo';p.mkdir();subprocess.run(['git','init','-b','main'],cwd=p,check=True,stdout=subprocess.DEVNULL);subprocess.run(['git','config','user.email','doctor@example.invalid'],cwd=p);subprocess.run(['git','config','user.name','Doctor Test'],cwd=p);(p/'pyproject.toml').write_text('[project]\nname="x"\nversion="0.1"\n');subprocess.run(['git','add','.'],cwd=p);subprocess.run(['git','commit','-m','init'],cwd=p,check=True,stdout=subprocess.DEVNULL);(p/'note.txt').write_text('work');r=inspect_project(str(p));assert r['detected']['has_change_history'];assert any(x['id']=='unsaved-work' for x in r['findings']);assert r['user_engineering_burden']['required_engineering_actions']==0
print('8 project-doctor invariants passed')
