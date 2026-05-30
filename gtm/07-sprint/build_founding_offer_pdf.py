"""Generates Verispect-Founding-20-Offer.pdf — the close-the-deal leave-behind."""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable)

PURPLE=colors.HexColor("#7c6eff"); PURPLE_LT=colors.HexColor("#ede9fe"); DARK=colors.HexColor("#111827")
GRAY=colors.HexColor("#6b7280"); GRAY_LT=colors.HexColor("#f9fafb"); BORDER=colors.HexColor("#e5e7eb")
GREEN=colors.HexColor("#10b981"); AMBER=colors.HexColor("#f59e0b"); WHITE=colors.white
st_=getSampleStyleSheet()
def S(n,**k): return ParagraphStyle(n,parent=st_["Normal"],**k)
brand=S("b",fontSize=24,textColor=PURPLE,fontName="Helvetica-Bold")
eyebrow=S("e",fontSize=10,textColor=AMBER,fontName="Helvetica-Bold",spaceAfter=2)
h1=S("h1",fontSize=17,textColor=DARK,fontName="Helvetica-Bold",spaceBefore=6,spaceAfter=4,leading=20)
h2=S("h2",fontSize=12,textColor=DARK,fontName="Helvetica-Bold",spaceBefore=10,spaceAfter=4)
body=S("body",fontSize=9.5,textColor=DARK,spaceAfter=4,leading=14)
small=S("s",fontSize=7.5,textColor=GRAY,leading=10)
wb=S("wb",fontSize=10,textColor=WHITE,fontName="Helvetica-Bold")
incl=S("incl",fontSize=10,textColor=DARK,leading=15)

doc=SimpleDocTemplate("Verispect-Founding-20-Offer.pdf",pagesize=A4,leftMargin=1.9*cm,rightMargin=1.9*cm,topMargin=1.4*cm,bottomMargin=1.3*cm)
s=[]
s.append(Paragraph("Verispect",brand))
s.append(Paragraph("THE FOUNDING 20  ·  EU AI ACT · HIGH-RISK RULES FROM 2 AUGUST 2026",eyebrow))
s.append(HRFlowable(width="100%",thickness=2,color=PURPLE,spaceAfter=8))
s.append(Paragraph("Get your AI audit-ready before the deadline. In one day.",h1))
s.append(Paragraph("The EU AI Act requires high-risk AI — hiring, credit, insurance, legal — to <b>prove</b> it isn't "
    "drifting or discriminating. Verispect generates that proof automatically, in one line of code. "
    "We never see your data — only hashes and vectors.",body))

s.append(Paragraph("What every Founding Customer gets",h2))
incl_rows=[
    ["✓","AI Act Readiness Report","Branded, article-mapped compliance PDF, generated on your real model."],
    ["✓","Continuous monitoring","Active bias & drift probes + automatic monthly report."],
    ["✓","White-glove setup","We integrate the one line with you on a 30-min call. Zero effort."],
    ["✓","“Monitoring Active” badge","Verispect Verified badge for your site & security page."],
    ["✓","Founding price, locked for life","€79/mo or €790/yr — public price is €99. Never increases."],
    ["✓","Direct founder line","Private Slack with Ajay, whenever you need him."],
]
t=Table([[Paragraph(f'<font color="#10b981"><b>{a}</b></font>',incl),Paragraph(f"<b>{b}</b>",incl),Paragraph(c,body)] for a,b,c in incl_rows],
        colWidths=[0.7*cm,5.0*cm,11.0*cm])
t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("PADDING",(0,0),(-1,-1),6),
                       ("ROWBACKGROUNDS",(0,0),(-1,-1),[WHITE,GRAY_LT]),("BOX",(0,0),(-1,-1),0.5,BORDER),
                       ("LINEBELOW",(0,0),(-1,-2),0.3,BORDER)]))
s.append(t)

# Risk reversal band
s.append(Spacer(1,8))
rr=[[Paragraph("<b>Zero risk to look.</b>  Run the free 5-minute snapshot first — see your model's real drift score. "
               "Only join if it shows you something worth fixing. Cancel anytime, no lock-in.",wb)]]
rt=Table(rr,colWidths=[16.7*cm]); rt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),PURPLE),("PADDING",(0,0),(-1,-1),11)]))
s.append(rt)

s.append(Paragraph("Why now",h2))
s.append(Paragraph("From <b>2 August 2026</b>, continuous monitoring (Art. 72), logging (Art. 13) and bias governance "
    "(Art. 10) become mandatory for high-risk AI. Employment & credit AI are explicitly high-risk (Annex III §4). "
    "Enterprise buyers are already asking for this evidence — ahead of the law. "
    "<i>(A pending Digital Omnibus may move standalone Annex III to Dec 2027 — but procurement isn't waiting.)</i>",body))

s.append(Paragraph("Why Verispect, not a logging tool",h2))
comp=[["","Observability tools","Verispect"],
      ["Logs what your model said","Yes","Yes"],
      ["Actively tests for drift & bias in production","—","Yes"],
      ["Protected-characteristic bias probes (8)","—","Yes"],
      ["EU AI Act readiness report","—","Yes"],
      ["Never sees your raw data","—","Yes"]]
ct=Table(comp,colWidths=[9.0*cm,3.8*cm,3.9*cm])
ct.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),DARK),("TEXTCOLOR",(0,0),(-1,0),WHITE),
    ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),8.5),("ALIGN",(1,0),(-1,-1),"CENTER"),
    ("PADDING",(0,0),(-1,-1),5),("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE,GRAY_LT]),("GRID",(0,0),(-1,-1),0.3,BORDER),
    ("BACKGROUND",(2,1),(2,-1),PURPLE_LT),("FONTNAME",(2,0),(2,-1),"Helvetica-Bold")]))
s.append(ct)

s.append(Spacer(1,10))
cta=[[Paragraph("<b>Claim one of 20 Founding spots.</b><br/><font size=8.5>Run your free snapshot in 5 minutes — one line, no card, we never see your data.</font>",wb),
      Paragraph("<b>verispectai.com/founding</b><br/><font size=8.5>hello@verispectai.com</font>",wb)]]
cta_t=Table(cta,colWidths=[11.2*cm,5.5*cm]); cta_t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),DARK),("PADDING",(0,0),(-1,-1),12),("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
s.append(cta_t)
s.append(Spacer(1,4))
s.append(Paragraph("Verispect provides AI behaviour monitoring and compliance <i>evidence</i>. It does not constitute legal advice "
    "or certify compliance; the operator remains responsible. Founding pricing is limited to the first 20 customers.",small))
doc.build(s)
print("Saved Verispect-Founding-20-Offer.pdf")
