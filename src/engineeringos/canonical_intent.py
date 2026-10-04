from __future__ import annotations
import pathlib,re,hashlib

CANONICAL_FILES=("VISION.md","docs/product/CONVERSATIONAL_INTERFACE.md","docs/product/NO_ENGINEERING_PREREQUISITE.md","docs/roadmap/PRODUCT_PLAN.md","docs/roadmap/SELF_HOSTING_PLAN.md")

def load_canonical_statements(root:str)->list[dict]:
 base=pathlib.Path(root);out=[]
 for rel in CANONICAL_FILES:
  p=base/rel
  if not p.exists(): continue
  text=p.read_text(errors="ignore")
  for line_no,line in enumerate(text.splitlines(),1):
   x=line.strip()
   if not x or x.startswith("#") or len(x)<20: continue
   if x.startswith(("- ","* ","> ")): x=x[2:].strip()
   if any(k in x.lower() for k in ("must ","must not","should ","never ","primary","default","human owns","system owns","conversation-first","not assumed")):
    sid=hashlib.sha256(f"{rel}:{line_no}:{x}".encode()).hexdigest()[:12]
    out.append({"id":"canon-"+sid,"statement":x,"source":rel,"line":line_no,"authority":"CURRENT_ACCEPTED_INTENT"})
 return out

def search_statements(statements:list[dict],terms:list[str])->list[dict]:
 toks=[t.lower() for t in terms]
 return [s for s in statements if all(t in s["statement"].lower() for t in toks)]
