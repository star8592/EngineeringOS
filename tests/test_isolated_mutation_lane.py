import sys,tempfile,pathlib,subprocess
sys.path.insert(0,'src/engineeringos')
from isolated_mutation_lane import *
def run(*a,cwd=None): return subprocess.check_output(a,cwd=cwd,text=True).strip()
with tempfile.TemporaryDirectory() as td:
 repo=pathlib.Path(td)/"repo";repo.mkdir();run("git","init","-q",cwd=repo);run("git","config","user.email","t@example.com",cwd=repo);run("git","config","user.name","T",cwd=repo)
 (repo/"app.txt").write_text("old\n");run("git","add","app.txt",cwd=repo);run("git","commit","-qm","base",cwd=repo);sha=run("git","rev-parse","HEAD",cwd=repo)
 root=pathlib.Path(td)/"workspaces";w=create_workspace(str(repo),project="P",item_id="i",source_sha=sha,root=str(root))
 assert pathlib.Path(w["path"]).exists() and not w["reused"]
 w2=create_workspace(str(repo),project="P",item_id="i",source_sha=sha,root=str(root));assert w2["reused"]
 out=apply_file_changes(w["path"],changes={"app.txt":"new\n"},allowed_paths=["app.txt"])
 assert out["changed_paths"]==["app.txt"] and "new" in out["diff"]
 try: apply_file_changes(w["path"],changes={"secret.txt":"x"},allowed_paths=["app.txt"]);raise AssertionError()
 except MutationLaneError as e: assert "PATH_OUTSIDE" in str(e)
 try: validate_paths([".git/config"],[".git/config"]);raise AssertionError()
 except MutationLaneError as e: assert str(e)=="PROTECTED_PATH"
 cleanup_workspace(str(repo),w["path"]);assert not pathlib.Path(w["path"]).exists()
print("7 isolated-mutation-lane invariants passed")
