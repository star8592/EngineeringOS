from __future__ import annotations
import pathlib,subprocess,hashlib,json
from dataclasses import dataclass,asdict
from typing import Optional
MANIFESTS={"package.json":"JavaScript/TypeScript","pyproject.toml":"Python","requirements.txt":"Python","Cargo.toml":"Rust","go.mod":"Go","pom.xml":"Java","build.gradle":"Java/Kotlin","Gemfile":"Ruby","composer.json":"PHP"}
def understand_project(root):
    purpose=None; caps=[]; runs=[]; checks=[]
    pkg=root/"package.json"
    if pkg.exists():
        try:
            data=json.loads(pkg.read_text()); purpose=data.get("description"); scripts=data.get("scripts",{})
            runs=[k for k in ("dev","start","serve") if k in scripts]
            checks=[k for k in scripts if k=="test" or k.startswith("test:") or k.startswith("verify:") or k in ("lint","build")]
        except Exception: pass
    purpose_evidence=[]
    if purpose: purpose_evidence.append("package.json:description")
    if not purpose:
        readmes=sorted(root.glob("README*"))
        for rp in readmes[:1]:
            lines=[x.strip().lstrip("#>*- ").strip() for x in rp.read_text(errors="ignore")[:10000].splitlines()]
            candidates=[x for x in lines if 30 <= len(x) <= 240 and not x.startswith(("http","[!","```"))]
            if candidates:
                purpose=candidates[0]; purpose_evidence.append(rp.name+":prose"); break
    app=root/"src"/"app"
    if app.is_dir():
        hidden={"api","admin","privacy","terms","verification","login","result","report"}
        for page in app.rglob("page.tsx"):
            rel=page.parent.relative_to(app)
            if not rel.parts: caps.append("home")
            elif rel.parts[0] not in hidden and not any(x.startswith("[") for x in rel.parts): caps.append("/".join(rel.parts))
    if not caps:
        for c,label in (("src","application"),("scripts","automation"),("docs","documentation")):
            if (root/c).exists(): caps.append(label)
    return {"purpose":purpose,"purpose_evidence":purpose_evidence,"purpose_is_inferred":bool(purpose and "package.json:description" not in purpose_evidence),"visible_capabilities":sorted(set(caps))[:24],"run_commands":runs,"verification_commands":checks[:40]}

@dataclass
class Finding:
 id:str; severity:str; title:str; explanation:str; system_can_handle:bool; needs_user_intent:bool=False; evidence:tuple[str,...]=()
def _run(cwd,*args): return subprocess.run(args,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
def inspect_project(path:str,name:Optional[str]=None)->dict:
 root=pathlib.Path(path).expanduser().resolve()
 if not root.is_dir(): raise ValueError("project input must be a directory")
 manifests=[p.name for p in root.iterdir() if p.is_file() and p.name in MANIFESTS]; stacks=sorted({MANIFESTS[m] for m in manifests}); understanding=understand_project(root)
 has_git=(root/".git").exists(); git={}; findings=[]
 if has_git:
  def g(*a):
   p=_run(root,"git",*a); return p.stdout.strip() if p.returncode==0 else None
  git={"head":g("rev-parse","HEAD"),"branch":g("branch","--show-current") or "detached","dirty":bool(g("status","--porcelain")),"branches":(g("for-each-ref","--format=%(refname:short)","refs/heads") or "").splitlines(),"origin_main":g("rev-parse","origin/main")}
  if git["dirty"]: findings.append(Finding("unsaved-work","attention","There is work that has not been safely consolidated yet.","I will protect it before attempting cleanup or consolidation.",True,evidence=("git-status",)))
  if git["origin_main"] and git["head"]!=git["origin_main"]: findings.append(Finding("source-drift","attention","The copy being worked on differs from the shared main version.","I can determine whether this is active work, already-replaced work, or work that should be consolidated.",True,evidence=("git-head","origin-main")))
  if len(git["branches"])>8: findings.append(Finding("many-work-lines","attention","This project has many parallel or leftover lines of work.","I can classify which work is active, already included, obsolete, or must be protected.",True,evidence=("git-branches",)))
 else: findings.append(Finding("no-history","info","This project is not connected to a recoverable change history.","I can still diagnose it now and can create protected history later without requiring you to learn version control.",True))
 tests=[r for r in ("tests","test","__tests__","pytest.ini","vitest.config.ts","jest.config.js","jest.config.ts") if (root/r).exists()] + understanding["verification_commands"]
 if (root/"package.json").exists():
  try:
   import json
   scripts=json.loads((root/"package.json").read_text()).get("scripts",{})
   tests += [f"package.json:{k}" for k in scripts if k=="test" or k.startswith("test:") or k.startswith("verify:")]
  except Exception:
   pass
 if not tests: findings.append(Finding("verification-gap","attention","I could not find an obvious automated verification setup.","Before making autonomous changes, I should establish a way to prove important behavior still works.",True))
 ci=[r for r in (".github/workflows",".gitlab-ci.yml","Jenkinsfile") if (root/r).exists()]
 if not ci: findings.append(Finding("automation-gap","info","I could not find an obvious automatic build/check pipeline.","This does not stop diagnosis. I can add appropriate verification automation before taking higher-autonomy actions.",True))
 score=max(0,100-15*sum(f.severity=="attention" for f in findings)-5*sum(f.severity=="info" for f in findings))
 status="NEEDS_INTENT" if any(f.needs_user_intent for f in findings) else ("AT_RISK" if any(f.severity=="critical" for f in findings) else ("WORKING" if findings else "HEALTHY"))
 fingerprint=hashlib.sha256((str(root)+"|"+str(manifests)+"|"+str(git.get("head"))).encode()).hexdigest()[:16]
 summary="Your software looks healthy from the evidence I can inspect. You do not need to manage engineering details." if status=="HEALTHY" else f"I found {sum(f.severity=='attention' for f in findings)} engineering issues worth handling. You do not need to understand the underlying tools; I can protect the project and work through them."
 return {"schema_version":2,"project_id":fingerprint,"project_name":name or root.name,"input_kind":"folder","status":status,"health_score":score,"plain_summary":summary,"software_understanding":understanding,"detected":{"stacks":stacks,"manifests":manifests,"has_change_history":has_git,"has_automated_tests":bool(tests),"has_automation_pipeline":bool(ci)},"engineering_details":{"git":git,"test_signals":tests,"ci_signals":ci},"findings":[asdict(f) for f in findings],"user_engineering_burden":{"required_engineering_actions":0,"required_intent_decisions":sum(f.needs_user_intent for f in findings)}}
def render_plain(r):
 lines=[r["project_name"],f'Health: {r["health_score"]}/100 · {r["status"]}',r["plain_summary"],""]
 for f in r["findings"]: lines += [f'• {f["title"]}',f'  {f["explanation"]}']
 return "\n".join(lines+["",f'What you need to do: {r["user_engineering_burden"]["required_engineering_actions"]} engineering tasks'])
