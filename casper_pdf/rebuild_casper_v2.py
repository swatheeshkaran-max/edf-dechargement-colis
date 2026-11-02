#!/usr/bin/env python3
"""Generate two-sheet EPR2 / Casper vessel workbook.
Full source URLs and nominal specifications are in CASPER_SOURCES.csv.
The 0.5 m all-around screening is preliminary, not a loading approval.
"""
import csv
import math
from pathlib import Path
import build_casper as core
from xml.sax.saxutils import escape

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
rows=list(csv.DictReader((HERE/"CASPER_SOURCES.csv").open(encoding="utf-8")))
CARGO=[("CE",20.0,9.0,8.0,110.0),("PP",48.0,2.8,3.807,154.0),("GV",24.9,6.46,6.6,580.0)]
CLEAR=0.5
OVERHEAD=0.5
DWCC={"9582855":3746.39,"9582867":3600,"9369514":3550,"9195731":3550,
"9387322":3876,"1029053":3798,"9472012":3850,"9195834":4950,
"9195901":4950,"9967548":5000}
TANKTOP={"9582855":15,"9582867":None,"9369514":15,"9195731":15,
"9387322":15,"1029053":15,"9472012":15,"9195834":19,
"9195901":19,"9967548":15}
NOTES={
"9582855":"DWCC and call sign discrepancies between website and PDF.",
"9582867":"Published tanktop strength not verified.",
"9387322":"Published hatch width differs from hold width; confirm hatch geometry.",
"1029053":"Published LOA differs between fleet page and specification.",
"9472012":"CE height insufficient when 0.5 m overhead clearance is applied.",
"9195834":"Confirm removal/position of movable bulkheads.",
"9195901":"Source draft shows invalid values/units; no draft substituted."}
# Override only the OOXML serialization of spreadsheet HYPERLINK formulas;
# all ordinary values still use the existing generator.
_original_cell=core.cell
def hyperlink_cell(value,ref,sty=0):
    if isinstance(value,str) and value.startswith("=HYPERLINK("):
        formula=value[1:]
        st=f' s="{sty}"' if sty else ""
        return f'<c r="{ref}" t="str"{st}><f>{escape(formula)}</f><v>OPEN PDF</v></c>'
    return _original_cell(value,ref,sty)
core.cell=hyperlink_cell

heads=["Vessel","IMO","Colis type","Vessel class","Cargo L (m)","Cargo W (m)","Cargo H (m)",
"Mass / colis (t)","LOA (m)","Beam (m)","Summer draft (m)","DWCC (t)",
"Hold L (m)","Hold W (m)","Hold H (m)","Hatch L (m)","Hatch W (m)",
"Tanktop (t/m2)","Tween deck?","Tween dimensions (m)","Clearance (m)",
"Colis along","Colis across","MAX COLIS","Total load (t)","Berth filter",
"Hold + hatch filter","Classification","Verification / restrictions","PDF (GitHub)"]
classification=[heads]
for s in rows:
    imo=s["imo"]
    loa,beam,draft=(core.num(s[k]) for k in ("loa_m","beam_m","summer_draft_m"))
    hL,hW,hH=(core.num(s[k]) for k in ("hold_length_m","hold_width_m","hold_height_m"))
    aL,aW=(core.num(s[k]) for k in ("hatch_length_m","hatch_width_m"))
    dwcc=DWCC.get(imo)
    berth="FAIL" if loa>154 or beam>39 or (draft is not None and draft>12) else ("VERIFY" if draft is None else ("CAUTION" if draft>7 else "PASS"))
    src=f'https://github.com/swatheeshkaran-max/edf-dechargement-colis/blob/main/casper_pdf/{s["slug"]}.pdf'
    urlformula='=HYPERLINK("'+src+'","OPEN PDF")'
    for typ,L,W,H,mass in CARGO:
        along=max(0,math.floor(hL/(L+2*CLEAR)))
        across=max(0,math.floor(hW/(W+2*CLEAR)))
        hold_ok=(hL>=L+2*CLEAR and hW>=W+2*CLEAR and hH>=H+OVERHEAD
                 and aL>=L+2*CLEAR and aW>=W+2*CLEAR)
        fit="PASS" if hold_ok else "FAIL"
        quantity=min(along*across,math.floor(dwcc/mass)) if hold_ok and berth!="FAIL" and dwcc else 0
        stat="CONDITIONAL" if quantity>0 else "REJECT"
        reasons=[]
        if not hold_ok: reasons.append("0.50 m all-around envelope fails hold, overhead or hatch criteria")
        if typ=="CE": reasons.append("Required clear height 8.50 m")
        if typ=="PP": reasons.append("48 m contiguous free bay and bulkhead removal/position to verify")
        if typ=="GV": reasons.append("580 t concentrated loading / tanktop strengthening to verify")
        if draft is None:reasons.append("Summer draft unverified")
        if TANKTOP.get(imo) is None:reasons.append("Tanktop allowable load not documented")
        if imo in NOTES:reasons.append(NOTES[imo])
        reasons.append("Tween deck not documented; crane, support, stability and actual loading to verify")
        classification.append([s["vessel"],imo,typ,"NC (shore crane)",L,W,H,mass,
        loa,beam,draft,dwcc,hL,hW,hH,aL,aW,TANKTOP.get(imo),"NOT DOCUMENTED",
        "NOT DOCUMENTED",CLEAR,along,across,quantity,quantity*mass,berth,fit,stat,
        "; ".join(reasons),urlformula])
method=[
["Parameter","Value","Unit","Meaning / screening rule"],
["LOA maximum",154,"m","Reject above 154 m"],
["Beam maximum",39,"m","Reject above 39 m"],
["Summer draft maximum",12,"m","Reject above 12 m; invalid/missing draft flagged for verification"],
["Draft caution threshold",7,"m","Flag caution above 7 m"],
["Side / fore / aft clearance",CLEAR,"m","0.5 m every horizontal side of each colis; adjacent colis have 1.0 m space"],
["Free overhead",OVERHEAD,"m","0.5 m unobstructed height above each colis; tanktop support below, no bottom gap"],
["Cargo","Length m","Width m","Height m","Mass t"],
*[[a,b,c,d,e] for (a,b,c,d,e) in CARGO],
["Packing orientation","Lengthwise","Widthwise","","No rotation, no stacking; tanktop only"],
["Along count","INT(hold L / (colis L + 1 m))","","",""],
["Across count","INT(hold W / (colis W + 1 m))","","",""],
["MAX COLIS","MIN(along × across, INT(DWCC / colis weight))","","","Requires hatch and free-height criteria"],
["Hatch and hold criteria","Each ≥ colis dimension + 1 m (L/W)","","","Plus 0.5 m overhead; exact entry route unverified"],
["Tween deck","NOT DOCUMENTED","","","No verified tween dimensions; movable bulkheads are NOT tween decks"],
["Class NC","No certified onboard crane data","","","Shore/floating lifting required; review crane load/radius"],
["CONDITIONAL","Geometric fit only","","","Not evidence of approved voyage or terminal unloading"],
["REJECT","No underdeck fit under stated clearance","","","Deck cargo or alternate stowage unassessed"],
["Source PDF","GitHub blob link in Classification","","","All ten specification PDFs deposited in casper_pdf/"],
["NOTE","Nominal 2D rectangular packing","","","Cribbing, corner clearances, hatch entrance, stability and cargo lashing not approved"],
]
core.xlsx(ROOT/"casper_convois_epr2.xlsx",[("Classification",classification),("Méthode",method)])
print("Wrote 2-sheet Casper EPR2 workbook (10 vessels x 3 cargoes).")
