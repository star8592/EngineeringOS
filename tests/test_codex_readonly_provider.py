import sys,tempfile,pathlib,json,os
sys.path.insert(0,'src/engineeringos')
from codex_readonly_provider import CodexReadOnlyProvider
from coding_agent_provider import TaskEnvelope,CodingAgentError
with tempfile.TemporaryDirectory() as td:
 b=pathlib.Path(td)/"codex";b.write_text("#!/usr/bin/env python3\nimport sys,json,pathlib\na=sys.argv\nout=pathlib.Path(a[a.index('-o')+1]);prompt=sys.stdin.read();assert '--sandbox' in a and a[a.index('--sandbox')+1]=='read-only';assert '--ephemeral' in a;out.write_text(json.dumps({'changes':{'x.txt':'new'},'rationale':'ok','confidence':0.8}))\n");b.chmod(0o755)
 t=TaskEnvelope("P","i","sha","change",("x.txt",),("true",),{})
 c=CodexReadOnlyProvider(binary=str(b)).propose(task=t,files={"x.txt":"old"})
 assert c.provider=="codex-cli-readonly" and c.changes=={"x.txt":"new"} and c.confidence==.8
 sleeper=pathlib.Path(td)/"sleepcodex";sleeper.write_text("#!/usr/bin/env python3\nimport time;time.sleep(10)\n");sleeper.chmod(0o755)
 try: CodexReadOnlyProvider(binary=str(sleeper),timeout=1).propose(task=t,files={"x.txt":"old"});raise AssertionError()
 except CodingAgentError as e: assert str(e)=="CODEX_TIMEOUT"
print("5 codex-readonly-provider invariants passed")
