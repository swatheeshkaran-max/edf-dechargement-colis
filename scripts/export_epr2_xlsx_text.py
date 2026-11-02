#!/usr/bin/env python3
"""Read-only export of existing XLSX worksheets to CSV for EPR2 consolidation.
Uses Python standard library, never rewrites source workbooks.
"""
import csv, json, posixpath, re, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/"epr2_exports"
OUT.mkdir(exist_ok=True)
FILES=[
"convois_epr2.xlsx","vertom_convois_epr2.xlsx","sal_convois_epr2.xlsx",
"classification_familles_epr2.xlsx","selection_navires_epr2.xlsx",
"casper_convois_epr2.xlsx"
]
MAIN="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG="http://schemas.openxmlformats.org/package/2006/relationships"
def tag(local):return "{"+MAIN+"}"+local
def xlcol(a):
    n=0
    for c in a:n=n*26+ord(c)-64
    return n-1
def get_text(elem):
    return "".join(x.text or "" for x in elem.iter(tag("t")))
def export(path):
    out=[]
    with zipfile.ZipFile(path) as z:
        paths=set(z.namelist())
        ss=[]
        if "xl/sharedStrings.xml" in paths:
            root=ET.fromstring(z.read("xl/sharedStrings.xml"))
            ss=[get_text(si) for si in root.findall(tag("si"))]
        book=ET.fromstring(z.read("xl/workbook.xml"))
        rels=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        relmap={x.attrib.get("Id"):x.attrib.get("Target") for x in rels.findall("{"+PKG+"}Relationship")}
        for idx,sh in enumerate(book.find(tag("sheets")),1):
            name=sh.get("name")
            rid=sh.attrib.get("{"+REL+"}id")
            target=relmap.get(rid,"")
            xp=posixpath.normpath(posixpath.join("xl",target.lstrip("/"))) if not target.startswith("/") else target.lstrip("/")
            if xp not in paths:
                xp=posixpath.normpath(target.lstrip("/"))
            if xp not in paths:continue
            root=ET.fromstring(z.read(xp))
            data=root.find(tag("sheetData"))
            if data is None:continue
            rows=[]
            for row in data.findall(tag("row")):
                vals={}
                for c in row.findall(tag("c")):
                    ref=c.get("r","")
                    m=re.match(r"([A-Z]+)",ref)
                    if not m:continue
                    col=xlcol(m.group(1))
                    t=c.get("t")
                    v=c.find(tag("v"))
                    f=c.find(tag("f"))
                    inline=c.find(tag("is"))
                    if t=="s" and v is not None and v.text is not None:
                        try:val=ss[int(v.text)]
                        except:val=v.text
                    elif t=="inlineStr" and inline is not None:
                        val=get_text(inline)
                    elif v is not None and v.text is not None: val=v.text
                    elif f is not None:val="="+(f.text or "")
                    else:val=""
                    vals[col]=val
                if vals:
                    count=min(max(vals)+1,100)
                    rows.append([vals.get(i,"") for i in range(count)])
            if not rows:continue
            maxc=max(len(x) for x in rows)
            safe=re.sub(r"[^A-Za-z0-9_-]","_",name)[:40]
            dest=OUT/(path.stem+"__"+str(idx)+"_"+safe+".csv")
            with dest.open("w",encoding="utf-8-sig",newline="") as f:
                w=csv.writer(f);w.writerows(rows)
            out.append({"file":path.name,"sheet":name,"csv":dest.name,"rows":len(rows),"cols":maxc,
                        "samples":rows[:3]})
    return out
manifest=[]
for item in FILES:
    try:manifest+=export(ROOT/item)
    except Exception as e:manifest.append({"file":item,"error":str(e)})
(OUT/"MANIFEST.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
print(json.dumps([{k:r.get(k) for k in ("file","sheet","csv","rows","cols","error")} for r in manifest],indent=2))
