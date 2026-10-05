from __future__ import annotations
import json,re

class HostSurfaceAdapterError(ValueError):
    pass

def _tool_description_and_signature(raw:str)->tuple[str,str]:
    marker="\n\n```ts\n"
    if marker not in raw:
        raise HostSurfaceAdapterError("HOST_SIGNATURE_MISSING")
    description,rest=raw.split(marker,1)
    if "\n```" not in rest:
        raise HostSurfaceAdapterError("HOST_SIGNATURE_FENCE_INVALID")
    signature=rest.split("\n```",1)[0].strip()
    if not description.strip() or not signature:
        raise HostSurfaceAdapterError("HOST_DESCRIPTOR_INVALID")
    return description.strip(),signature

def _constraint(comment:str,entry:dict)->None:
    for key in ("minimum","maximum","minItems"):
        m=re.search(rf"\b{key}:\s*(\d+)",comment)
        if m:entry[key]=int(m.group(1))

def _parse_property(chunk:str,pending_description:str|None)->tuple[str,dict]:
    before,*comment_parts=chunk.split("//",1)
    before=before.strip().rstrip(",").strip()
    comment=comment_parts[0].strip() if comment_parts else ""
    m=re.fullmatch(r'([A-Za-z_][A-Za-z0-9_]*)(\?)?:\s*(.+)',before)
    if not m:
        raise HostSurfaceAdapterError("HOST_PROPERTY_SIGNATURE_INVALID:"+before)
    name,optional,typ=m.groups();entry={"required":not bool(optional)}
    typ=typ.strip()
    if typ.endswith("[]"):
        entry["type"]="array";entry["itemsType"]=typ[:-2].strip()
    elif "|" in typ and all(re.fullmatch(r'"[^"]*"',x.strip()) for x in typ.split("|")):
        vals=[x.strip()[1:-1] for x in typ.split("|")]
        entry["type"]="string";entry["enum"]=vals
    elif typ in {"string","integer","boolean","number","object","array"}:
        entry["type"]=typ
    elif typ=="any":
        entry["type"]="any"
    else:
        raise HostSurfaceAdapterError("HOST_PROPERTY_TYPE_UNSUPPORTED:"+typ)
    if pending_description:entry["description"]=pending_description
    _constraint(comment,entry)
    return name,entry

def parse_input_contract(signature:str)->dict:
    if re.search(r"\bargs:\s*object\b",signature):
        return {"properties":{}}
    m=re.search(r"\bargs:\s*\{(.*?)\}\):\s*Promise",signature,re.S)
    if not m:
        raise HostSurfaceAdapterError("HOST_ARGS_OBJECT_MISSING")
    body=m.group(1).strip()
    if not body:return {"properties":{}}
    # Rendered signatures put one property per line when comments/complexity exist,
    # otherwise they may be a compact comma-separated object.
    logical=[];pending=[]
    for raw_line in body.splitlines():
        line=raw_line.strip()
        if not line:continue
        if line.startswith("//"):
            pending.append(line[2:].strip());continue
        if "\n" not in body and "," in line:
            logical.extend((part.strip(),None) for part in line.split(",") if part.strip())
        else:
            logical.append((line," ".join(pending) if pending else None));pending=[]
    if pending:raise HostSurfaceAdapterError("ORPHAN_HOST_PROPERTY_DESCRIPTION")
    props={}
    for chunk,desc in logical:
        name,entry=_parse_property(chunk,desc)
        if name in props:raise HostSurfaceAdapterError("DUPLICATE_HOST_PROPERTY:"+name)
        props[name]=entry
    return {"properties":dict(sorted(props.items()))}

def adapt(document:dict)->dict:
    tools=document.get("tools") if isinstance(document,dict) else None
    if not isinstance(tools,list):raise HostSurfaceAdapterError("HOST_TOOL_ARRAY_REQUIRED")
    out=[]
    seen=set()
    for row in tools:
        if not isinstance(row,dict) or not isinstance(row.get("name"),str) or not isinstance(row.get("description"),str):
            raise HostSurfaceAdapterError("HOST_TOOL_DESCRIPTOR_INVALID")
        name=row["name"]
        if name in seen:raise HostSurfaceAdapterError("DUPLICATE_HOST_TOOL:"+name)
        seen.add(name)
        description,signature=_tool_description_and_signature(row["description"])
        out.append({"name":name,"description":description,"input_contract":parse_input_contract(signature)})
    return {"schema":"devcontrol.chatgpt-host-surface.v2","capture_source":"chatgpt-host-runtime","tools":sorted(out,key=lambda x:x["name"])}
