#!/usr/bin/env python3
"""Extract dimensional data explicitly stated in EPR2 source PDFs.
No guessing where source values are absent. Does not modify PDFs.
"""
import csv, pathlib, re, fitz
ROOT=pathlib.Path(__file__).resolve().parent.parent
OUT=ROOT/'epr2_exports'
pdfs=sorted([*ROOT.glob('briese_pdf/*.pdf'),*ROOT.glob('vertom_pdf/*.pdf'),*ROOT.glob('casper_pdf/*.pdf'),*ROOT.glob('sal_pdf/*.pdf')])
def number(tx,patterns):
 for pt in patterns:
  m=re.search(pt,tx,re.I)
  if m:
   try:return float(m.group(1))
   except:return None
 return None
def dims(tx,pat):
 matches=re.findall(pat,tx,re.I)
 return ';'.join('x'.join(str(float(v)) for v in group) for group in matches)
with (OUT/'PDF_DIMENSION_INDEX.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.writer(f)
 w.writerow(['pdf_path','source_LOA_m','source_beam_m','hold_LxWxH','hatch_LxW','source_draft_m','document_type','parse_caution'])
 for p in pdfs:
  name=p.parts[-2]
  doc=fitz.open(p)
  tx='\n'.join(doc[i].get_text('text',sort=True) for i in range(min(3,len(doc))))
  if name=='briese_pdf':
   loa=number(tx,[r'Length\s*o\.?a\.?\s*(?:abt\.?\s*)?([\d.]+)\s*m'])
   beam=number(tx,[r'\bBeam\s*(?:abt\.?\s*)?([\d.]+)\s*m'])
   draft=number(tx,[r'Max\.?\s*draft\s*\(summer\)\s*([\d. ]+)\s*m'])
   hold='';hatch='';caution='Hold and hatch dimensions not explicitly verified from PDF machine text; GA image review needed'
  elif name=='vertom_pdf':
   loa=number(tx,[r'L\.O\.A\.\s*([\d.]+)\s*mtrs'])
   beam=number(tx,[r'\bBeam\s*([\d.]+)\s*mtrs'])
   draft=number(tx,[r'Summer\s*SW\s*draft\s*([\d.]+)\s*mtrs'])
   hold=dims(tx,r'Hold\s*dim\.?\s*hold(?:\s*\d+)?\s*LxWxH\s*([\d.]+)\s*x\s*([\d.]+)\s*x\s*([\d.]+)')
   hatch='';caution='Hold dimensions are not necessarily hatch opening dimensions; exact hatch positions unavailable'
  elif name=='casper_pdf':
   loa=number(tx,[r'Length\s*O\.A\.\s*\(LOA\)\s*([\d.]+)\s*m'])
   beam=number(tx,[r'Beam\s*O\.A\.\s*\(BOA\)\s*([\d.]+)\s*m'])
   draft=number(tx,[r'Draft\s*.\s*Summer\s*([\d.]+)\s*m'])
   hold=dims(tx,r'Hold\s*Dimensions\s*([\d.]+)\s*[xX]\s*([\d.]+)\s*[xX]\s*([\d.]+)')
   hatch=dims(tx,r'Hatch\s*Dimensions\s*([\d.]+)\s*[xX]\s*([\d.]+)')
   caution='Published hatch dimension but exact longitudinal offset and usable clearance remain unverified'
  else:
   loa=beam=draft=None;hold=hatch=''
   caution='SAL fleet list is a multi-vessel summary; individual record must be matched to the correct family'
  w.writerow([str(p.relative_to(ROOT)),loa,beam,hold,hatch,draft,name,caution])
print('Wrote dimension index',len(pdfs))
