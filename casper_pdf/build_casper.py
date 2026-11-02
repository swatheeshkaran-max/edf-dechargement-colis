#!/usr/bin/env python3
"""Download official Casper technical PDFs and create an EPR2 screening workbook.
Uses only the Python standard library. Source: CASPER_SOURCES.csv.
The 6 classes and dimensional criteria mirror the repository EPR2 README.
All dimensionally passing configurations remain CONDITIONAL pending engineering approval.
"""
import csv, io, os, pathlib, time, urllib.request, zipfile, xml.sax.saxutils as sax
HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parent
rows=list(csv.DictReader((HERE/"CASPER_SOURCES.csv").open(encoding="utf-8-sig")))
CARGOS=[("CE",20.0,9.0,8.0,110.0),("PP",48.0,2.8,3.807,154.0),("GV",24.9,6.46,6.60,580.0)]
def num(s):
    try:return float(s)
    except (TypeError,ValueError):return None
def screening(s,c):
    typ,L,W,H,mass=c
    loa,beam,draft=num(s["loa_m"]),num(s["beam_m"]),num(s["summer_draft_m"])
    hL,hW,hH=num(s["hold_length_m"]),num(s["hold_width_m"]),num(s["hold_height_m"])
    aL,aW=num(s["hatch_length_m"]),num(s["hatch_width_m"])
    reasons=[]
    if loa is not None and loa>154: reasons.append("LOA > 154 m")
    if beam is not None and beam>39: reasons.append("Beam > 39 m")
    if draft is not None and draft>12: reasons.append("Draft > 12 m")
    if hL<L: reasons.append("Hold length short")
    if hW<W+1: reasons.append("Hold width < cargo + 1 m")
    if hH<H: reasons.append("Hold height short")
    if aL<L: reasons.append("Hatch length short")
    if aW<W+1: reasons.append("Hatch width < cargo + 1 m")
    if reasons:return "REJECT", "; ".join(reasons)+". Underdeck only; deck stowage not assessed."
    checks=["Shore crane and lifting study","Hatch entry geometry and clear height","Concentrated tanktop loading","Stability and rigging"]
    if draft is None:checks.append("Summer draft missing/invalid")
    elif draft>7:checks.append("Draft above caution threshold")
    if typ=="PP":checks.append("48 m contiguous clear bay and removable bulkheads")
    if typ=="GV":checks.append("580 t cargo support and loading sequence")
    return "CONDITIONAL","; ".join(checks)
def download_pdfs():
    failures=[]
    for s in rows:
        p=HERE/(s["slug"]+".pdf")
        if p.exists() and p.stat().st_size>1000 and p.read_bytes()[:4]==b"%PDF":
            print("Present:",p.name);continue
        req=urllib.request.Request(s["source_pdf_url"],headers={"User-Agent":"Mozilla/5.0 (compatible; EPR2 technical document importer)"})
        try:
            with urllib.request.urlopen(req,timeout=50) as resp:
                data=resp.read(15_000_000+1)
            if not data.startswith(b"%PDF") or len(data)>15_000_000:raise ValueError("Not a valid PDF or exceeds 15 MB")
            p.write_bytes(data)
            print("Saved",p.name,len(data),"bytes")
        except Exception as e:
            print("FAILED",s["slug"],str(e));failures.append((s["slug"],str(e)))
        time.sleep(0.4)
    return failures
def csv_file(path,data):
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.writer(f);w.writerows(data)
def excel_col(n):
    s=""
    while n:n,r=divmod(n-1,26);s=chr(65+r)+s
    return s
def cell(value,ref,sty=0):
    if value is None:return ""
    style=f' s="{sty}"' if sty else ""
    if isinstance(value,(float,int)) and not isinstance(value,bool):
        return f'<c r="{ref}"{style}><v>{value}</v></c>'
    return f'<c r="{ref}" t="inlineStr"{style}><is><t>{sax.escape(str(value))}</t></is></c>'
def xlsx(path,sheets):
    with zipfile.ZipFile(path,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml",'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'+''.join(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' for i in range(1,len(sheets)+1))+'</Types>')
        z.writestr("_rels/.rels",'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
        z.writestr("xl/workbook.xml",'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'+''.join(f'<sheet name="{sax.escape(n)}" sheetId="{i}" r:id="rId{i}"/>' for i,(n,_) in enumerate(sheets,1))+'</sheets></workbook>')
        z.writestr("xl/_rels/workbook.xml.rels",'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'+''.join(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>' for i in range(1,len(sheets)+1))+'<Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>')
        z.writestr("xl/styles.xml",'<?xml version="1.0" encoding="UTF-8"?><styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><fonts count="2"><font><sz val="10"/><name val="Aptos"/></font><font><b/><color rgb="FFFFFFFF"/><sz val="10"/><name val="Aptos"/></font></fonts><fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FF18334B"/><bgColor indexed="64"/></patternFill></fill></fills><borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="2"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/><xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFill="1" applyFont="1"/></cellXfs></styleSheet>')
        for i,(name,rs) in enumerate(sheets,1):
            ncols=max(len(r) for r in rs)
            widths='<cols>'+''.join(f'<col min="{j}" max="{j}" width="{60 if j>15 else 18}" customWidth="1"/>' for j in range(1,ncols+1))+'</cols>'
            rsxml=[]
            for ridx,r in enumerate(rs,1):
                body="".join(cell(v,f"{excel_col(j)}{ridx}",1 if ridx==1 else 0) for j,v in enumerate(r,1))
                rsxml.append(f'<row r="{ridx}"{" ht=\"30\" customHeight=\"1\"" if ridx==1 else ""}>{body}</row>')
            content='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>'+widths+'<sheetData>'+''.join(rsxml)+'</sheetData><autoFilter ref="A1:'+excel_col(ncols)+str(len(rs))+'"/></worksheet>'
            z.writestr(f"xl/worksheets/sheet{i}.xml",content)
def main():
    failures=download_pdfs()
    nav=[["Vessel","IMO","Year","LOA m","Beam m","Summer draft m","Hold L m","Hold W m","Hold H m","Hatch L m","Hatch W m","Tanktop t/m2","Crane status","Official technical PDF","GitHub local PDF"]]
    detail=[["Vessel","IMO","Cargo","Class","Weight t","Cargo L m","Cargo W m","Cargo H m","Hold L m","Hold W m","Hold H m","Hatch L m","Hatch W m","Summer draft m","Berth max LOA m","Berth max beam m","Berth max draft m","Status","Reason for status","PDF source"]]
    summary=[["Vessel","IMO","CE-NC","PP-NC","GV-NC","PDF source","Repository PDF","Note"]]
    families=[["Family","Vessels","Basis","Caution"],["A","Niklas / Helen Anna","87.90 m LOA; 56.55x10.02x8.10 m hold","Dimensionally similar; sister-ship relationship unverified"],["B","Vesper / Ventura / Verena / Helga G","Similar 88.6-89.7 m LOA and 8.43 m hold height","Dimensional family only, not a certified sister-ship grouping"],["C","Maras / Elena L","94.96 m LOA; 67.54x11.00x8.45 m hold","Verify identical design with operator"],["D","Vitality","61.50x12.65x7.90 m hold","CE fails underdeck height"],["E","Misje Rose","56.60x12.80x9.80 m hold","Separate group"]]
    method=[["Parameter","Value","Unit","Comment"],["Cargo CE", "20 x 9 x 8","m","110 t"],["Cargo PP","48 x 2.8 x 3.807","m","154 t"],["Cargo GV","24.9 x 6.46 x 6.60","m","580 t"],["Maximum LOA",154,"m","Berth restriction"],["Maximum beam",39,"m","Berth restriction"],["Maximum draft",12,"m","Berth restriction"],["Draft warning",7,"m","Above 7 m use caution"],["Clear extra width",1,"m","Hold and hatch must exceed cargo width by 1 m"],["Class NC","No verified onboard crane","","Use external shore/floating crane"],["Status CONDITIONAL","NOT APPROVED","","Verify hold entry, hatch clearance, tanktop loading, stability, and rigging"],["Status REJECT","Underdeck geometric failure","","Deck carriage not investigated"]]
    counts={c:[0,0] for c in ["CE-BG","CE-NC","PP-BG","PP-NC","GV-BG","GV-NC"]}
    sources=[["Vessel","IMO","GitHub PDF (after workflow success)","Original specification PDF"]]
    for s in rows:
        purl=s["source_pdf_url"];slug=s["slug"];name=s["vessel"]
        nav.append([name,s["imo"],"",num(s["loa_m"]),num(s["beam_m"]),num(s["summer_draft_m"]),num(s["hold_length_m"]),num(s["hold_width_m"]),num(s["hold_height_m"]),num(s["hatch_length_m"]),num(s["hatch_width_m"]),num(s["tanktop_t_per_m2"]),"Not documented (NC)",purl,f"casper_pdf/{slug}.pdf"])
        statuses=[]
        for c in CARGOS:
            status,reason=screening(s,c);statuses.append(status)
            counts[c[0]+"-NC"][0 if status=="CONDITIONAL" else 1]+=1
            detail.append([name,s["imo"],c[0],c[0]+"-NC",c[4],c[1],c[2],c[3],num(s["hold_length_m"]),num(s["hold_width_m"]),num(s["hold_height_m"]),num(s["hatch_length_m"]),num(s["hatch_width_m"]),num(s["summer_draft_m"]),154,39,12,status,reason,purl])
        gh=f"https://github.com/swatheeshkaran-max/edf-dechargement-colis/blob/main/casper_pdf/{slug}.pdf"
        summary.append([name,s["imo"],*statuses,purl,gh,"Draft/height/clearance and load checks required; see detail"])
        sources.append([name,s["imo"],gh,purl])
    classes=[["Class","Conditional","Reject","Total"]]+[[k,*v,sum(v)] for k,v in counts.items()]
    sheets=[("Navires",nav),("Classification",detail),("Vue classes",classes),("Synthèse",summary),("Méthode",method),("Familles",families),("Sources PDF",sources)]
    xlsx(ROOT/"casper_convois_epr2.xlsx",sheets)
    csv_file(HERE/"CASPER_CLASSIFICATION.csv",detail)
    csv_file(HERE/"CASPER_SYNTHESIS.csv",summary)
    csv_file(HERE/"CASPER_DOWNLOAD_FAILURES.csv",[["vessel","error"],*failures])
    print("Wrote workbook, CSV classifications and errors:",len(failures))
    if failures:raise SystemExit("PDF download incomplete: see CASPER_DOWNLOAD_FAILURES.csv")
if __name__=="__main__":main()
