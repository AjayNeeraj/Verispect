"""Generates Verispect-One-Pager.pdf — the leave-behind sales sheet."""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, HRFlowable)

PURPLE = colors.HexColor("#7c6eff"); PURPLE_LT = colors.HexColor("#ede9fe")
DARK = colors.HexColor("#111827"); GRAY = colors.HexColor("#6b7280")
GRAY_LT = colors.HexColor("#f9fafb"); BORDER = colors.HexColor("#e5e7eb")
GREEN = colors.HexColor("#10b981"); WHITE = colors.white

styles = getSampleStyleSheet()
def S(n, **k): return ParagraphStyle(n, parent=styles["Normal"], **k)
brand = S("b", fontSize=26, textColor=PURPLE, fontName="Helvetica-Bold", spaceAfter=1)
tag = S("t", fontSize=10.5, textColor=GRAY, spaceAfter=2)
h2 = S("h2", fontSize=12, textColor=DARK, fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=4)
body = S("body", fontSize=9, textColor=DARK, spaceAfter=4, leading=13)
small = S("s", fontSize=7.5, textColor=GRAY, leading=10)
white_b = S("wb", fontSize=9, textColor=WHITE, fontName="Helvetica-Bold")
big_p = S("bp", fontSize=9.5, textColor=DARK, leading=14)

doc = SimpleDocTemplate("Verispect-One-Pager.pdf", pagesize=A4,
                        leftMargin=1.8*cm, rightMargin=1.8*cm, topMargin=1.5*cm, bottomMargin=1.4*cm)
st = []
st.append(Paragraph("Verispect", brand))
st.append(Paragraph("Verify + Inspect. Every model. Every call. Every month.", tag))
st.append(HRFlowable(width="100%", thickness=2, color=PURPLE, spaceAfter=8))

st.append(Paragraph("Active AI bias &amp; drift detection — and the EU AI Act evidence to prove it.", h2))
st.append(Paragraph(
    "Logging tools tell you what your model said. They can't tell you it started behaving "
    "<b>differently</b> today. Verispect actively probes your production LLM for bias and drift, "
    "scores it deterministically, and produces the audit-ready report enterprises and regulators "
    "demand — in one line of code, with <b>zero access to your data</b>.", big_p))

# Problem / Solution two columns
ps = [[Paragraph("<b>THE PROBLEM</b>", white_b), Paragraph("<b>THE VERISPECT WAY</b>", white_b)],
      [Paragraph("Providers silently update models. Fine-tunes degrade. A fair hiring or credit "
                 "model quietly starts discriminating — and nothing in your code changed. "
                 "Observability can't see it; inputs/outputs still look normal.", body),
       Paragraph("Calibrated synthetic probes + replays of your own traffic test behaviour "
                 "continuously, catch change the moment it happens, and map findings article-by-article "
                 "to the EU AI Act. We receive only hashes + vectors — never your content.", body)]]
t = Table(ps, colWidths=[8.3*cm, 8.3*cm])
t.setStyle(TableStyle([("BACKGROUND",(0,0),(0,0),GRAY), ("BACKGROUND",(1,0),(1,0),PURPLE),
                       ("PADDING",(0,0),(-1,-1),8), ("VALIGN",(0,0),(-1,-1),"TOP"),
                       ("BACKGROUND",(0,1),(0,1),GRAY_LT), ("BACKGROUND",(1,1),(1,1),PURPLE_LT),
                       ("BOX",(0,0),(-1,-1),0.5,BORDER), ("INNERGRID",(0,0),(-1,-1),0.5,BORDER)]))
st.append(Spacer(1,6)); st.append(t)

st.append(Paragraph("Why Verispect wins", h2))
pillars = [
    ["Active, not passive", "We test behaviour continuously — incl. silent provider model updates — instead of only logging it."],
    ["Audit-ready by default", "Branded report mapped to EU AI Act Art. 9/10/13/14/72 + Annex III. The document your buyer asks for."],
    ["Privacy by architecture", "Only SHA-256 hashes + embedding vectors leave your machine. We reduce your data-protection surface."],
    ["One line, zero latency", "wrap(OpenAI(...), verispect_key=...) — your calls return immediately; all probe work is async."],
]
pt = Table([[Paragraph(f"<b>{a}</b>", body), Paragraph(b, body)] for a,b in pillars],
           colWidths=[4.2*cm, 12.4*cm])
pt.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("PADDING",(0,0),(-1,-1),5),
                        ("ROWBACKGROUNDS",(0,0),(-1,-1),[WHITE,GRAY_LT]),
                        ("LINEBELOW",(0,0),(-1,-2),0.3,BORDER),("BOX",(0,0),(-1,-1),0.5,BORDER),
                        ("TEXTCOLOR",(0,0),(0,-1),PURPLE)]))
st.append(pt)

st.append(Paragraph("How it works", h2))
st.append(Paragraph("<b>1.</b> Add one line to your OpenAI client. &nbsp; "
                    "<b>2.</b> Verispect probes a sample of live traffic and scores drift vs your baseline. &nbsp; "
                    "<b>3.</b> Download a continuously-updated, audit-ready compliance report.", body))

# vs competitors
st.append(Paragraph("Verispect vs. observability tools", h2))
comp = [["", "Helicone", "LangSmith", "Braintrust", "Verispect"],
        ["Logs traffic", "Yes", "Yes", "Yes", "Yes (hashes)"],
        ["Active in-prod probing", "—", "—", "—", "Yes"],
        ["Protected-characteristic bias probes", "—", "—", "—", "Yes (8)"],
        ["EU AI Act report output", "—", "—", "—", "Yes"],
        ["Never sees your raw data", "—", "—", "—", "Yes"]]
ct = Table(comp, colWidths=[6.4*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.7*cm])
cstyle=[("BACKGROUND",(0,0),(-1,0),DARK),("TEXTCOLOR",(0,0),(-1,0),WHITE),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),7.8),
        ("ALIGN",(1,0),(-1,-1),"CENTER"),("PADDING",(0,0),(-1,-1),5),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE,GRAY_LT]),("GRID",(0,0),(-1,-1),0.3,BORDER),
        ("BACKGROUND",(4,1),(4,-1),PURPLE_LT),("TEXTCOLOR",(4,1),(4,-1),DARK),
        ("FONTNAME",(4,0),(4,-1),"Helvetica-Bold")]
ct.setStyle(TableStyle(cstyle)); st.append(ct)

# Pricing strip + CTA
st.append(Paragraph("Pricing", h2))
st.append(Paragraph("<b>Free AI Act snapshot</b> &nbsp;·&nbsp; <b>Verispect $1,500/mo</b> (zero config, everything) &nbsp;·&nbsp; "
                    "<b>Founding 20: $1,500 locked for life</b> before it rises to $2,500 &nbsp;·&nbsp; <b>Enterprise</b> (custom). "
                    "Start free, no card.", body))

st.append(Spacer(1,4))
cta=[[Paragraph("<b>Run a free snapshot — see your model's drift in 5 minutes.</b><br/>"
                "<font size=8>One line of code. We never see your data.</font>", white_b),
      Paragraph("<b>verispectai.com</b><br/><font size=8>hello@verispectai.com</font>", white_b)]]
cta_t=Table(cta,colWidths=[11*cm,5.6*cm])
cta_t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),PURPLE),("PADDING",(0,0),(-1,-1),12),
                           ("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
st.append(cta_t)
st.append(Spacer(1,4))
st.append(Paragraph("Verispect provides AI behaviour monitoring and compliance <i>evidence</i>. It does not "
                    "constitute legal advice or certify compliance; the operator remains responsible. "
                    "EU AI Act high-risk obligations apply from 2 Aug 2026 (standalone Annex III may move to "
                    "2 Dec 2027 if the Digital Omnibus is adopted).", small))
doc.build(st)
print("Saved Verispect-One-Pager.pdf")
