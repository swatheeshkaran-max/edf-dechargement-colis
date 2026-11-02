#!/usr/bin/env python3
"""Casper EPR2 hierarchy: CONDITIONAL only, 0.50 m lateral / 0.05 m overhead."""
import csv, math
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.colors import HexColor as C
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
OUT=ROOT/'hierarchie_classification_casper.pdf'
BASE='https://github.com/swatheeshkaran-max/edf-dechargement-colis'
DATA=list(csv.DictReader((HERE/'CASPER_SOURCES.csv').open(encoding='utf-8-sig')))
DWCC={'9582855':3746.39,'9582867':3600,'9369514':3550,'9195731':3550,'9387322':3876,'1029053':3798,'9472012':3850,'9195834':4950,'9195901':4950,'9967548':5000}
CARGOS=[('CE','Enveloppe',20,9,8,110),('PP','Pont polaire',48,2.8,3.807,154),('GV','Générateur de vapeur',24.9,6.46,6.6,580)]
def f(row,k):
    try:return float(row[k])
    except (KeyError,ValueError,TypeError):return None
def count(s,cargo):
    _,_,L,B,H,M=cargo
    if f(s,'loa_m')>154 or f(s,'beam_m')>39:return 0
    draft=f(s,'summer_draft_m')
    if draft is not None and draft>12:return 0
    hl,hw,hh=f(s,'hold_length_m'),f(s,'hold_width_m'),f(s,'hold_height_m')
    al,aw=f(s,'hatch_length_m'),f(s,'hatch_width_m')
    if hh<H+.05 or hl<L+1 or hw<B+1 or al<L+1 or aw<B+1:return 0
    return min(math.floor(hl/(L+1))*math.floor(hw/(B+1)),math.floor(DWCC[s['imo']]/M))
groups={cargo[0]:sorted([(s['vessel'],count(s,cargo),s['slug']) for s in DATA if count(s,cargo)>0],key=lambda r:r[0].lower()) for cargo in CARGOS}
assert [len(groups[k]) for k in ('CE','PP','GV')]==[9,10,10]
F='/usr/share/fonts/truetype/dejavu/'
if Path(F+'DejaVuSans.ttf').exists():
    pdfmetrics.registerFont(TTFont('DV',F+'DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont('DVB',F+'DejaVuSans-Bold.ttf'))
    regular,bold='DV','DVB'
else:regular,bold='Helvetica','Helvetica-Bold'
NAVY=C('#2F5597');DARK=C('#153153');INK=C('#20364C');MID=C('#607084')
BORDER=C('#4B6175');PALE=C('#D5E8F7');CREAM=C('#FFF2CB');GREEN=C('#E6F3DE')
LIGHT=C('#F8FAFC');LINE=C('#D6DFE8');MUTED=C('#8B98A6');WHITE=C('#FFFFFF')
W,H=landscape(A3);p=canvas.Canvas(str(OUT),pagesize=(W,H))
p.setTitle('Hiérarchie de classification - Casper (CONDITIONAL seulement)')
p.setAuthor('EPR2 vessel screening')
def box(x,y,w,h,fill,border=BORDER,r=7):
    p.setFillColor(fill);p.setStrokeColor(border);p.setLineWidth(.8)
    p.roundRect(x,y,w,h,r,fill=1,stroke=1)
def text(s,x,y,sz=11,col=INK,boldface=False,align='left'):
    p.setFillColor(col);p.setFont(bold if boldface else regular,sz)
    if align=='center':p.drawCentredString(x,y,str(s))
    elif align=='right':p.drawRightString(x,y,str(s))
    else:p.drawString(x,y,str(s))
def dash(x1,y1,x2,y2):
    p.saveState();p.setDash(3,3);p.setStrokeColor(MUTED);p.setLineWidth(.9)
    p.line(x1,y1,x2,y2);p.restoreState()
text('Hiérarchie de classification — Casper',W/2,795,25,DARK,True,'center')
text('CE / PP / GV   →   NC (conventionnel) ou NB (navire bigué)',W/2,770,11.4,MID,False,'center')
text('Sélection : navires au statut CONDITIONAL exclusivement  •  tous les navires retenus sont affichés',W/2,749,10.4,MID,False,'center')
bx=(W-260)/2
box(bx,674,260,56,PALE);box(bx,702,260,28,NAVY,NAVY,6)
text('Casper',W/2,711,13.5,WHITE,True,'center')
text('Armateur / opérateur',bx+15,683,10.5)
colw=352;start=45;gap=(W-2*start-3*colw)/2
for i,(kind,title,_,_,_,_) in enumerate(CARGOS):
    x=start+i*(colw+gap)
    dash(W/2,674,x+colw/2,638)
    box(x,577,colw,61,CREAM);box(x,603,colw,35,NAVY,NAVY,6)
    text(kind+' — '+title,x+colw/2,615,13.4,WHITE,True,'center')
    text(str(len(groups[kind]))+' navires conditionnels',x+colw/2,585.5,10.3,INK,False,'center')
    a=x;cw=191;b=x+201;nbw=colw-201;y=142;h=381;header=36
    dash(x+colw/2,577,a+cw/2,y+h);dash(x+colw/2,577,b+nbw/2,y+h)
    box(a,y,cw,h,LIGHT);box(b,y,nbw,h,GREEN)
    box(a,y+h-header,cw,header,NAVY,NAVY,5);box(b,y+h-header,nbw,header,NAVY,NAVY,5)
    text(kind+'-NC',a+cw/2,y+h-24,13,WHITE,True,'center')
    text(kind+'-NB',b+nbw/2,y+h-24,13,WHITE,True,'center')
    top=y+h-header-15
    for j,(name,amount,slug) in enumerate(groups[kind]):
        yy=top-(j+.68)*30
        if j:
            p.setStrokeColor(LINE);p.setLineWidth(.7);p.line(a+10,yy+20.5,a+cw-10,yy+20.5)
        text(name,a+12,yy+6,10.7,INK,True)
        text(str(amount)+' colis',a+cw-11,yy+7,8.3,MID,False,'right')
        p.linkURL(BASE+'/blob/main/casper_pdf/'+slug+'.pdf',(a+8,yy+1,a+cw-6,yy+23))
    text('Aucune sélection',b+nbw/2,y+h-header-39,10,INK,False,'center')
    text('Grue de bord',b+nbw/2,y+h-header-60,9.1,MID,False,'center')
    text('non vérifiée',b+nbw/2,y+h-header-75,9.1,MID,False,'center')
    text('Cliquer sur un navire pour ouvrir son PDF GitHub',a+5,y-20,8.3,MID)
p.setStrokeColor(LINE);p.line(45,91,W-45,91)
text('HYPOTHÈSES DE CLASSEMENT',45,74,10.7,DARK,True)
text('0,50 m de dégagement à chaque côté horizontal du colis  •  0,05 m de dégagement vertical  •  1 seule couche en cale',45,56,9.5)
text('Les nombres de colis sont des maxima géométriques NOMINAUX. Vérifier : pont de cale, accès à l’écoutille, stabilité, levage et chargement.',45,39,9.1,MID)
text('NB : navire bigué (grue embarquée vérifiée). NC : navire conventionnel nécessitant un levage à quai.',45,22,9.0,MID)
p.showPage();p.save()
print('Wrote',OUT,OUT.stat().st_size)
