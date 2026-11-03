#!/usr/bin/env python3
"""Read-only PDF evidence extraction for EPR2 dimension verification.
Creates compact source excerpts; does not alter PDFs or source workbooks.
"""
import csv, pathlib, re, json, fitz
ROOT=pathlib.Path(__file__).resolve().parent.parent
OUT=ROOT/"epr2_exports"
OUT.mkdir(exist_ok=True)
LABEL=re.compile(r"(?:\bloa\b|length\s*(?:overall|over\s*all|o\.?\s*a\.?)|length|breadth|\bbeam\b|hold|cargo\s*space|hatch|tween|draft|draught|deck\s*strength|tanktop|tank\s*top|capacity|cargo\s*hold|free\s*height|length\s*x\s*width)",re.I)
pdfs=sorted([*ROOT.glob("briese_pdf/*.pdf"),*ROOT.glob("vertom_pdf/*.pdf"),*ROOT.glob("casper_pdf/*.pdf"),*ROOT.glob("sal_pdf/*.pdf")])
with (OUT/"PDF_TECHNICAL_EVIDENCE.csv").open("w",newline="",encoding="utf-8") as fh:
 w=csv.writer(fh)
 w.writerow(["PDF path","PDF bytes","Extracted characters","First page text / labels","Dimension-related excerpts","Machine text result"])
 for pdf in pdfs:
  try:
   doc=fitz.open(str(pdf))
   tx="\n".join(doc[i].get_text("text",sort=True) for i in range(min(3,len(doc))))
   lines=[re.sub(r"\s+"," ",s).strip() for s in tx.splitlines()]
   lines=[s for s in lines if s]
   snippets=[];seen=set()
   for j,line in enumerate(lines):
     if LABEL.search(line):
       context=" | ".join(lines[max(0,j-1):min(len(lines),j+2)])[:320]
       if context not in seen:snippets.append(context);seen.add(context)
   # first-page samples and 25 most informative contexts
   w.writerow([str(pdf.relative_to(ROOT)),pdf.stat().st_size,len(tx)," \n".join(lines[:40])[:3600]," \n".join(snippets[:45])[:7800],"EXTRACTED" if len(tx.strip())>100 else "SCAN_OR_NO_TEXT"])
  except Exception as e:w.writerow([str(pdf.relative_to(ROOT)),pdf.stat().st_size,0,"","","ERROR: "+str(e)[:150]])
print("Extracted evidence for",len(pdfs),"PDFs")
