"""
build_invoice.py — generate a clean Verispect invoice PDF for a closed customer.
Turns a verbal 'yes' into a payable invoice in 30 seconds. Payoneer-ready (Pakistan).

Usage:
  python build_invoice.py --company "Acme HR GmbH" --email billing@acme.com \
      --plan founding-monthly --vat "DE123456789"
Plans: founding-monthly ($1,500) | founding-annual ($15,000) | starter ($490) | readiness-report ($2,900)
"""
import argparse, datetime, os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, Table, TableStyle, HRFlowable)

INK=colors.HexColor("#101828"); SLATE=colors.HexColor("#475467"); FAINT=colors.HexColor("#98A2B3")
ACCENT=colors.HexColor("#6A5CF0"); LINE=colors.HexColor("#E4E7EC"); NAVY=colors.HexColor("#0C111D")
ROWBG=colors.HexColor("#F9FAFB"); WHITE=colors.white
W,H=A4

PLANS = {
    "founding-monthly":   ("Verispect Founding — monthly", "AI Act monitoring + reports (Founding rate, locked for life)", 1500.0, "per month"),
    "founding-annual":    ("Verispect Founding — annual",  "AI Act monitoring + reports, 12 months (Founding rate, locked for life)", 15000.0, "per year"),
    "standard-monthly":   ("Verispect Standard — monthly", "AI Act monitoring + reports (standard rate)", 3000.0, "per month"),
    "readiness-report":   ("Verispect AI Act Readiness Report", "One-time risk classification + DPIA + monitoring report", 4900.0, "one-time"),
    "design-partner":     ("Verispect Design Partner — 6 months", "Design partnership: full monitoring + reports, EUR0, in exchange for logo + testimonial + reference + production traffic", 0.0, "6 months"),
}

# ── Your business details — FILL THESE ONCE ─────────────────────────────────
SELLER = {
    "name": "[Your registered name / Verispect]",
    "addr": "[Your address, City, Pakistan]",
    "email": "billing@verispectai.com",
    "tax": "[Your tax/NTN number if applicable]",
}
# Payment instructions shown on the invoice. Fill with your real Payoneer details.
PAY_INSTRUCTIONS = (
    "Pay by bank transfer to the Payoneer receiving account below (USD). "
    "Reference the invoice number. Or request a card payment link.\n"
    "Payoneer (USD): Bank [____]  ·  Account holder [____]  ·  Account no. [____]  ·  "
    "Routing/SWIFT [____]\nQuestions: billing@verispectai.com"
)

def make_doc(path):
    frame = Frame(1.9*cm, 2.2*cm, W-3.8*cm, H-4.6*cm, id="b")
    doc = BaseDocTemplate(path, pagesize=A4, title="Verispect Invoice", author="Verispect")
    doc.addPageTemplates([PageTemplate(id="Main", frames=[frame], onPage=_decorate)])
    return doc

def _shield(c,x,y,size,fill=ACCENT,check=WHITE):
    s=size/64.0; p=c.beginPath()
    p.moveTo(x+32*s,y+59*s); p.lineTo(x+10*s,y+51*s); p.lineTo(x+10*s,y+33*s)
    p.curveTo(x+10*s,y+18.5*s,x+19.4*s,y+9.4*s,x+32*s,y+5*s)
    p.curveTo(x+44.6*s,y+9.4*s,x+54*s,y+18.5*s,x+54*s,y+33*s)
    p.lineTo(x+54*s,y+51*s); p.close()
    c.setFillColor(fill); c.drawPath(p,stroke=0,fill=1)
    c.setStrokeColor(check); c.setLineWidth(5.5*s); c.setLineCap(1); c.setLineJoin(1)
    pa=c.beginPath(); pa.moveTo(x+21*s,y+31.5*s); pa.lineTo(x+28.5*s,y+23.5*s); pa.lineTo(x+44*s,y+40.5*s)
    c.drawPath(pa,stroke=1,fill=0)

def _decorate(c, doc):
    _shield(c, 1.9*cm, H-1.85*cm, 0.8*cm)
    c.setFont("Helvetica-Bold",13); c.setFillColor(INK); c.drawString(2.85*cm, H-1.6*cm, "Verispect")
    c.setFont("Helvetica",8); c.setFillColor(FAINT); c.drawRightString(W-1.9*cm, H-1.5*cm, "verispectai.com")
    c.setStrokeColor(LINE); c.setLineWidth(0.6); c.line(1.9*cm, H-2.05*cm, W-1.9*cm, H-2.05*cm)
    c.setFont("Helvetica",7.5); c.setFillColor(FAINT)
    c.drawString(1.9*cm, 1.35*cm, "Thank you. Verispect provides AI monitoring & compliance evidence, not legal advice.")

def S(n,**k):
    k.setdefault("fontName","Helvetica"); return ParagraphStyle(n,parent=getSampleStyleSheet()["Normal"],**k)

def build(args):
    title, desc, price, cadence = PLANS[args.plan]
    now = datetime.date.today() if not args.date else datetime.date.fromisoformat(args.date)
    inv_no = f"VSP-INV-{now.strftime('%Y%m%d')}-{args.seq:03d}"
    due = now + datetime.timedelta(days=args.net)
    out = args.out or f"Verispect-Invoice-{inv_no}.pdf"

    body=S("body",fontSize=9.5,leading=14,textColor=INK)
    h=S("h",fontSize=22,fontName="Helvetica-Bold",textColor=INK)
    lab=S("lab",fontSize=8,textColor=FAINT)
    val=S("val",fontSize=9.5,textColor=INK)
    cell=S("cell",fontSize=9.5,textColor=INK)
    doc=make_doc(out); s=[]
    s.append(Spacer(1,4)); s.append(Paragraph("INVOICE", h)); s.append(Spacer(1,8))

    meta=[[Paragraph("FROM",lab), Paragraph("BILL TO",lab), Paragraph("INVOICE",lab)],
          [Paragraph(f"<b>{SELLER['name']}</b><br/>{SELLER['addr']}<br/>{SELLER['email']}<br/>{SELLER['tax']}",val),
           Paragraph(f"<b>{args.company}</b><br/>{args.email}<br/>{('VAT: '+args.vat) if args.vat else ''}",val),
           Paragraph(f"<b>No.</b> {inv_no}<br/><b>Date.</b> {now:%d %b %Y}<br/><b>Due.</b> {due:%d %b %Y} (NET {args.net})",val)]]
    mt=Table(meta,colWidths=[6.0*cm,5.6*cm,None])
    mt.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("TOPPADDING",(0,1),(-1,1),4)]))
    s.append(mt); s.append(Spacer(1,14))

    qty=args.qty
    net=price*qty
    vat_rate = 0.0  # B2B cross-border to EU = reverse charge (0%); seller in PK. Adjust w/ accountant.
    vat_amt = net*vat_rate
    total = net+vat_amt
    rows=[["Description","Cadence","Qty","Amount (USD)"],
          [f"{title}\n{desc}", cadence, str(qty), f"${net:,.0f}"]]
    t=Table(rows,colWidths=[None,2.8*cm,1.4*cm,3.0*cm])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),NAVY),("TEXTCOLOR",(0,0),(-1,0),WHITE),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),9.5),
        ("ALIGN",(1,0),(-1,-1),"CENTER"),("ALIGN",(3,0),(3,-1),"RIGHT"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE,ROWBG]),("GRID",(0,0),(-1,-1),0.4,LINE),
        ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8)]))
    s.append(t); s.append(Spacer(1,6))

    tot=[["Subtotal",f"${net:,.0f}"],
         [f"VAT ({int(vat_rate*100)}% — reverse charge, B2B)" , f"${vat_amt:,.0f}"],
         ["TOTAL DUE", f"${total:,.0f}"]]
    tt=Table(tot,colWidths=[None,3.0*cm])
    tt.setStyle(TableStyle([("ALIGN",(0,0),(-1,-1),"RIGHT"),("FONTSIZE",(0,0),(-1,-1),9.5),
        ("TEXTCOLOR",(0,0),(-1,1),SLATE),("LINEABOVE",(0,2),(-1,2),0.6,LINE),
        ("FONTNAME",(0,2),(-1,2),"Helvetica-Bold"),("FONTSIZE",(0,2),(-1,2),12),("TEXTCOLOR",(0,2),(-1,2),INK),
        ("TOPPADDING",(0,0),(-1,-1),4)]))
    s.append(tt); s.append(Spacer(1,16))
    s.append(HRFlowable(width="100%",thickness=0.6,color=LINE)); s.append(Spacer(1,8))
    s.append(Paragraph("<b>Payment</b>",S("pb",fontSize=10,fontName="Helvetica-Bold",textColor=INK)))
    s.append(Paragraph(PAY_INSTRUCTIONS.replace("\n","<br/>"), body))
    if args.plan.startswith("founding"):
        s.append(Spacer(1,8))
        s.append(Paragraph("<b>Founding terms:</b> this rate is locked for life and will not increase. "
                           "Cancel anytime — no lock-in.", S("ft",fontSize=8.5,textColor=SLATE)))
    doc.build(s)
    print("Saved", out, f"(${total:,.0f} due {due:%d %b %Y})")

if __name__=="__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    ap=argparse.ArgumentParser()
    ap.add_argument("--company",required=True); ap.add_argument("--email",required=True)
    ap.add_argument("--plan",default="founding-monthly",choices=list(PLANS))
    ap.add_argument("--vat",default=""); ap.add_argument("--qty",type=int,default=1)
    ap.add_argument("--net",type=int,default=7); ap.add_argument("--seq",type=int,default=1)
    ap.add_argument("--date",default=""); ap.add_argument("--out",default="")
    build(ap.parse_args())
