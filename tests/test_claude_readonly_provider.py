import sys,tempfile,pathlib
sys.path.insert(0,'src/engineeringos')
from claude_readonly_provider import *
from coding_agent_provider import TaskEnvelope
with tempfile.TemporaryDirectory() as td:
 b=pathlib.Path(td)/"claude";b.write_text("#!/usr/bin/env python3\nimport sys,json\na=sys.argv;assert '-p' in a and a[a.index('--tools')+1]=='' and '--no-session-persistence' in a;sys.stdin.read();print(json.dumps({'structured_output':{'changes':{'x.py':'new'},'rationale':'ok','confidence':1}}))\n");b.chmod(0o755)
 t=TaskEnvelope("P","w","sha","goal",("x.py",),("python3","t.py"),{})
 c=ClaudeReadonlyProvider(binary=str(b)).propose(t,{"x.py":"old"});assert c.changes=={"x.py":"new"} and c.provider=="claude-cli-readonly"
print("5 claude-readonly-provider invariants passed")
