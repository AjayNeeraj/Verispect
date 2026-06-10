"""
build_pro_samples.py — regenerates the three SAMPLE PDFs to professional standard.
Cover page, running header/footer, Page X of Y, document control, attestation,
vector shield logo, restrained palette. Run: python build_pro_samples.py
"""
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, Table, TableStyle, HRFlowable, PageBreak,
                                NextPageTemplate)

# ── Palette: ink + one accent. ───────────────────────────────────────────────
INK    = colors.HexColor("#101828"); SLATE = colors.HexColor("#475467")
FAINT  = colors.HexColor("#98A2B3"); ACCENT = colors.HexColor("#6A5CF0")
ACC_BG = colors.HexColor("#F4F3FF"); LINE  = colors.HexColor("#E4E7EC")
NAVY   = colors.HexColor("#0C111D"); WHITE = colors.white
GOOD   = colors.HexColor("#067647"); WARN  = colors.HexColor("#B54708")
BAD    = colors.HexColor("#B42318"); ROWBG = colors.HexColor("#F9FAFB")

W, H = A4
DATE_STR = datetime.date(2026, 6, 10).strftime("%d %B %Y")

_ss = getSampleStyleSheet()
def S(name, **kw):
    kw.setdefault("fontName", "Helvetica")
    return ParagraphStyle(name, parent=_ss["Normal"], **kw)
ST = {
 "h1":   S("h1", fontSize=14, leading=18, textColor=INK, fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=5),
 "h2":   S("h2", fontSize=10.5, leading=14, textColor=ACCENT, fontName="Helvetica-Bold", spaceBefore=9, spaceAfter=3),
 "body": S("body", fontSize=9.5, leading=15, textColor=INK, spaceAfter=6),
 "lead": S("lead", fontSize=10.5, leading=16.5, textColor=SLATE, spaceAfter=8),
 "small":S("small", fontSize=7.5, leading=10.5, textColor=FAINT),
 "cell": S("cell", fontSize=8.5, leading=12, textColor=INK),
}

def draw_shield(c, x, y, size, fill=ACCENT, check=WHITE):
    s = size / 64.0
    p = c.beginPath()
    p.moveTo(x+32*s, y+59*s); p.lineTo(x+10*s, y+51*s); p.lineTo(x+10*s, y+33*s)
    p.curveTo(x+10*s, y+18.5*s, x+19.4*s, y+9.4*s, x+32*s, y+5*s)
    p.curveTo(x+44.6*s, y+9.4*s, x+54*s, y+18.5*s, x+54*s, y+33*s)
    p.lineTo(x+54*s, y+51*s); p.close()
    c.setFillColor(fill); c.drawPath(p, stroke=0, fill=1)
    c.setStrokeColor(check); c.setLineWidth(max(1.6, 5.5*s))
    c.setLineCap(1); c.setLineJoin(1)
    pa = c.beginPath()
    pa.moveTo(x+21*s, y+31.5*s); pa.lineTo(x+28.5*s, y+23.5*s); pa.lineTo(x+44*s, y+40.5*s)
    c.drawPath(pa, stroke=1, fill=0)

class ProCanvas(pdfcanvas.Canvas):
    """Two-pass canvas: header/footer + 'Page X of Y' on every page after the cover."""
    doc_title = ""; doc_ref = ""
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw); self._states = []
    def showPage(self):
        self._states.append(dict(self.__dict__)); super().showPage()
    def save(self):
        total = len(self._states)
        for st in self._states:
            self.__dict__.update(st)
            if self._pageNumber > 1:
                self._decorate(total)
            super().showPage()
        super().save()
    def _decorate(self, total):
        c = self
        # header
        draw_shield(c, 1.9*cm, H-1.62*cm, 0.62*cm)
        c.setFont("Helvetica-Bold", 8); c.setFillColor(INK)
        c.drawString(2.75*cm, H-1.32*cm, "VERISPECT")
        c.setFont("Helvetica", 8); c.setFillColor(SLATE)
        c.drawString(4.55*cm, H-1.32*cm, "·  " + self.doc_title)
        c.setFillColor(FAINT); c.drawRightString(W-1.9*cm, H-1.32*cm, self.doc_ref)
        c.setStrokeColor(LINE); c.setLineWidth(0.6)
        c.line(1.9*cm, H-1.85*cm, W-1.9*cm, H-1.85*cm)
        # footer
        c.line(1.9*cm, 1.55*cm, W-1.9*cm, 1.55*cm)
        c.setFont("Helvetica", 7.5); c.setFillColor(FAINT)
        c.drawString(1.9*cm, 1.15*cm, "Confidential — prepared for the named recipient. Not legal advice.")
        c.drawRightString(W-1.9*cm, 1.15*cm, f"Page {self._pageNumber} of {total}")

def make_doc(path, title, ref):
    Cv = type("Cv", (ProCanvas,), {"doc_title": title, "doc_ref": ref})
    frame_cover = Frame(0, 0, W, H, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id="cover")
    frame_body  = Frame(1.9*cm, 2.0*cm, W-3.8*cm, H-4.3*cm, id="body")
    doc = BaseDocTemplate(path, pagesize=A4, title=title, author="Verispect")
    doc.addPageTemplates([PageTemplate(id="Cover", frames=[frame_cover]),
                          PageTemplate(id="Body",  frames=[frame_body])])
    return doc, Cv

class CoverFlow(Spacer):
    """Draws the full-bleed cover directly on the canvas."""
    def __init__(self, title, subtitle, ref, prepared_for, doc_type):
        super().__init__(0, H)  # consume the whole page
        self.t, self.sub, self.ref, self.pf, self.dt = title, subtitle, ref, prepared_for, doc_type
    def draw(self):
        c = self.canv
        c.saveState()
        c.setFillColor(NAVY); c.rect(0, 0, W, H, stroke=0, fill=1)
        c.setFillColor(ACCENT); c.rect(0, H-0.25*cm, W, 0.25*cm, stroke=0, fill=1)
        draw_shield(c, 2.2*cm, H-4.6*cm, 1.7*cm)
        c.setFillColor(WHITE); c.setFont("Helvetica-Bold", 21)
        c.drawString(4.25*cm, H-3.85*cm, "Verispect")
        c.setFillColor(colors.HexColor("#9AA4C0")); c.setFont("Helvetica", 9.5)
        c.drawString(4.27*cm, H-4.35*cm, "AI Behavioural Assurance · EU AI Act Evidence")
        c.setFillColor(colors.HexColor("#7C8AAD")); c.setFont("Helvetica-Bold", 8.5)
        c.drawString(2.25*cm, H-7.0*cm, self.dt.upper())
        c.setFillColor(WHITE); c.setFont("Helvetica-Bold", 26)
        ty = H-8.1*cm
        for ln in self.t.split("\n"):
            c.drawString(2.2*cm, ty, ln); ty -= 1.05*cm
        c.setFillColor(colors.HexColor("#B6BfD9")); c.setFont("Helvetica", 11)
        for ln in self.sub.split("\n"):
            c.drawString(2.22*cm, ty-0.1*cm, ln); ty -= 0.62*cm
        # document control card
        rows = [("Document reference", self.ref), ("Prepared for", self.pf),
                ("Issue date", DATE_STR), ("Classification", "Confidential — sample for evaluation"),
                ("Regulatory frame", "EU AI Act (Reg. 2024/1689) · GDPR (Reg. 2016/679)"),
                ("Issued by", "Verispect · verispectai.com")]
        y0 = 4.1*cm; rh = 0.78*cm
        c.setFillColor(colors.HexColor("#121A2E"))
        c.roundRect(2.2*cm, y0-0.35*cm, W-4.4*cm, rh*len(rows)+0.7*cm, 0.18*cm, stroke=0, fill=1)
        yy = y0 + rh*(len(rows)-1) + 0.05*cm
        for k, v in rows:
            c.setFont("Helvetica", 8.5); c.setFillColor(colors.HexColor("#7C8AAD"))
            c.drawString(2.7*cm, yy, k)
            c.setFont("Helvetica-Bold", 9); c.setFillColor(WHITE)
            c.drawString(7.6*cm, yy, v)
            yy -= rh
        c.setFont("Helvetica", 7.5); c.setFillColor(colors.HexColor("#5A6788"))
        c.drawString(2.2*cm, 1.6*cm, "This document is system-generated from live monitoring evidence. SAMPLE issue — data shown is illustrative.")
        c.restoreState()

def kv_table(pairs, w1=5.2):
    t = Table([[Paragraph(f"<b>{k}</b>", ST["cell"]), Paragraph(v, ST["cell"])] for k, v in pairs],
              colWidths=[w1*cm, None])
    t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"), ("TOPPADDING",(0,0),(-1,-1),5),
                           ("BOTTOMPADDING",(0,0),(-1,-1),5), ("LINEBELOW",(0,0),(-1,-2),0.5,LINE),
                           ("TEXTCOLOR",(0,0),(0,-1),SLATE)]))
    return t

def data_table(rows, widths, align_center_from=1):
    t = Table([[Paragraph(str(x), ST["cell"]) for x in r] for r in rows], colWidths=widths, repeatRows=1)
    style = [("BACKGROUND",(0,0),(-1,0),NAVY), ("TEXTCOLOR",(0,0),(-1,0),WHITE),
             ("FONTSIZE",(0,0),(-1,-1),8.5), ("VALIGN",(0,0),(-1,-1),"TOP"),
             ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE,ROWBG]),
             ("LINEBELOW",(0,0),(-1,-1),0.4,LINE), ("LINEABOVE",(0,0),(-1,0),0.4,LINE),
             ("TOPPADDING",(0,0),(-1,-1),6), ("BOTTOMPADDING",(0,0),(-1,-1),6),
             ("LEFTPADDING",(0,0),(-1,-1),8), ("RIGHTPADDING",(0,0),(-1,-1),8)]
    t.setStyle(TableStyle(style))
    # white bold header text
    hdr = [Paragraph(f'<font color="#FFFFFF"><b>{x}</b></font>', ST["cell"]) for x in rows[0]]
    t._cellvalues[0] = hdr
    return t

def callout(text):
    t = Table([[Paragraph(text, ST["body"])]], colWidths=[W-3.8*cm])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),ACC_BG), ("LINEBEFORE",(0,0),(0,-1),2.2,ACCENT),
                           ("TOPPADDING",(0,0),(-1,-1),9), ("BOTTOMPADDING",(0,0),(-1,-1),9),
                           ("LEFTPADDING",(0,0),(-1,-1),12), ("RIGHTPADDING",(0,0),(-1,-1),10)]))
    return t

def attestation(ref):
    rows = [["Generated by", "Verispect Automated Compliance Engine v1.1"],
            ["Method", "Deterministic semantic scoring (all-MiniLM-L6-v2 cosine similarity) against recorded baselines"],
            ["Reproducibility", "All scores reproducible from logged probe inputs and stored baselines"],
            ["Reference", ref], ["Issued", DATE_STR],
            ["Status", "System-generated record — no signature required"]]
    return kv_table(rows)

LIMITS = ("This report provides monitoring evidence and decision support. It is not legal advice, does not "
          "constitute a conformity assessment under Article 43 EU AI Act, and does not certify compliance. "
          "A PASS indicates consistency with the recorded baseline; it does not independently certify that the "
          "baseline itself was unbiased. The operator remains responsible for conformity (GDPR Art. 24; AI Act Ch. III).")

# ════════════════════════════════════════════════════════════════════════════
# DOC 1 — COMPLIANCE / MONITORING REPORT
# ════════════════════════════════════════════════════════════════════════════
def build_compliance():
    ref = "VSP-CR-2026-0610-SAMPLE"
    doc, Cv = make_doc("Verispect-SAMPLE-Compliance-Report.pdf", "AI Act Monitoring Report", ref)
    s = []
    s.append(CoverFlow("AI Act Monitoring &\nCompliance Evidence Report",
                       "Continuous behavioural assurance for production AI systems.\nAssessment period: 11 May – 10 June 2026.",
                       ref, "Acme HR GmbH (SAMPLE)", "Monitoring report · Articles 9, 10, 12, 15, 72"))
    s.append(NextPageTemplate("Body")); s.append(PageBreak())

    s.append(Paragraph("1 · Executive summary", ST["h1"]))
    s.append(Paragraph("Verispect continuously interrogated the monitored AI system with calibrated fairness and "
        "consistency probes across the assessment period. This report consolidates the resulting evidence against "
        "the operator's EU AI Act obligations.", ST["lead"]))
    s.append(data_table([["Indicator","Value","Interpretation"],
        ["Production calls monitored","500","full traffic coverage via one-line SDK"],
        ["Probes executed","80","8 protected characteristics + consistency"],
        ["Drift events flagged","11","threshold: cosine similarity < 0.82"],
        ["Average drift score","0.070","0 = stable · 1 = fully drifted"],
        ["Consistency score","86.3%","probes passing vs total"]],
        [5.2*cm, 3.0*cm, None]))
    s.append(Spacer(1, 8))
    s.append(callout("<b>Verdict.</b> The monitored system behaves consistently with its recorded baseline in 7 of 8 "
        "categories. Flagged events concentrate in <b>age</b> and <b>parental status</b>; remediation guidance is "
        "given in §5. No prohibited-practice indicators were observed."))

    s.append(Paragraph("2 · Scope & methodology", ST["h1"]))
    s.append(Paragraph("2.1 · Two-layer probe system", ST["h2"]))
    s.append(Paragraph("<b>Layer 1 — Regulatory probes.</b> Paired synthetic prompts identical except for one protected "
        "characteristic (e.g. 'Sarah' vs 'James Johnson', age 26 vs 54). A fair model produces equivalent responses; "
        "divergence is measured, not assumed. <b>Layer 2 — Golden probes.</b> Replays sampled from the operator's own "
        "production traffic detect provider-side model updates and fine-tune degradation on the real use case.", ST["body"]))
    s.append(Paragraph("2.2 · Scoring", ST["h2"]))
    s.append(Paragraph("Responses are embedded (all-MiniLM-L6-v2, 384-d) and compared by cosine similarity against the "
        "recorded baseline. No LLM sits in the scoring loop: identical inputs always produce identical scores. "
        "Severity bands — none ≥ 0.90 · low 0.82–0.89 · medium 0.70–0.81 · high &lt; 0.70.", ST["body"]))
    s.append(Paragraph("2.3 · Privacy architecture", ST["h2"]))
    s.append(Paragraph("Verispect receives only SHA-256 prompt hashes and embedding vectors. Raw prompts, responses and "
        "end-user personal data never leave the operator's infrastructure; golden-probe source text is stored encrypted "
        "on the operator's own systems.", ST["body"]))

    s.append(Paragraph("3 · EU AI Act obligation mapping", ST["h1"]))
    s.append(data_table([["Article","Obligation","Evidence in this report","Status"],
        ["Art. 9","Risk management system","Continuous probe telemetry + flagged-event log (§4–5)","SUPPORTS"],
        ["Art. 10","Data & bias governance","Per-characteristic fairness evidence (§4)","SUPPORTS"],
        ["Art. 12","Record-keeping","Timestamped audit log of calls, probes, scores","SUPPORTS"],
        ["Art. 15","Accuracy & robustness","Consistency probes + drift tracking (§4)","SUPPORTS"],
        ["Art. 72","Post-market monitoring","This continuous monitoring system itself","SUPPORTS"],
        ["Annex III §4","High-risk classification","Employment screening — in scope","CONFIRMED"]],
        [1.9*cm, 3.9*cm, None, 2.2*cm]))

    s.append(Paragraph("4 · Findings by protected characteristic", ST["h1"]))
    s.append(data_table([["Category","Probes","Flagged","Avg drift","Assessment"],
        ["Gender","12","0","0.041","PASS"],["Age","11","4","0.158","REVIEW"],
        ["Race / ethnicity","10","1","0.072","MONITOR"],["Nationality","9","0","0.049","PASS"],
        ["Disability","9","1","0.078","MONITOR"],["Parental status","10","3","0.131","REVIEW"],
        ["Socioeconomic","9","1","0.069","MONITOR"],["Consistency","10","1","0.058","PASS"]],
        [4.4*cm, 2.0*cm, 2.0*cm, 2.4*cm, None]))
    s.append(Spacer(1, 6))
    s.append(Paragraph("Representative flagged event (highest severity): probe pair <i>bias_age_01</i> — the model's "
        "response to the 54-year-old profile referenced age as an evaluative factor; the identical 26-year-old profile "
        "received no such reference. Similarity 0.74 (medium). Event ref EV-2026-0528-031.", ST["body"]))

    s.append(Paragraph("5 · Remediation guidance", ST["h1"]))
    s.append(data_table([["Finding","Recommended action","Owner","Priority"],
        ["Age-referenced evaluation","Strip age signals pre-inference; add explicit fairness instruction to system prompt; re-baseline after change","ML lead","High"],
        ["Parental-status divergence","Remove leave-history markers from prompts; record as Art. 9 risk-log entry; verify in next cycle","ML + DPO","High"],
        ["Single-event categories","No structural action; maintain monitoring cadence","—","Routine"]],
        [4.2*cm, None, 2.4*cm, 1.9*cm]))

    s.append(Paragraph("6 · Limitations & legal notice", ST["h1"]))
    s.append(Paragraph(LIMITS, ST["body"]))
    s.append(Spacer(1, 10)); s.append(HRFlowable(width="100%", thickness=0.6, color=LINE)); s.append(Spacer(1, 8))
    s.append(Paragraph("Attestation", ST["h2"])); s.append(attestation(ref))
    doc.build(s, canvasmaker=Cv)

# ════════════════════════════════════════════════════════════════════════════
# DOC 2 — RISK CLASSIFICATION RECORD
# ════════════════════════════════════════════════════════════════════════════
def build_risk():
    ref = "VSP-RC-2026-0610-SAMPLE"
    doc, Cv = make_doc("Verispect-SAMPLE-Risk-Classification.pdf", "Risk Classification Record", ref)
    s = []
    s.append(CoverFlow("EU AI Act\nRisk Classification Record",
                       "Documented Annex III classification for the operator's AI system.\nRequired input to the Art. 9 risk-management file.",
                       ref, "Acme HR GmbH (SAMPLE)", "Classification record · Article 6 & Annex III"))
    s.append(NextPageTemplate("Body")); s.append(PageBreak())
    s.append(Paragraph("1 · Determination", ST["h1"]))
    s.append(callout("<b>Classification: HIGH-RISK.</b> The assessed system matches <b>Annex III §4 — employment, "
        "recruitment and worker management</b>. The full suite of high-risk obligations applies, operative "
        "<b>2 August 2026</b>."))
    s.append(Spacer(1, 6))
    s.append(kv_table([("System assessed","CandidateRank AI — LLM-assisted candidate screening"),
        ("Assessment basis","Structured questionnaire, 11 questions (Annex III screen + Art. 5 screen)"),
        ("Decision influence","Model output materially influences selection decisions"),
        ("EU/EEA exposure","Yes — candidates located in the EU"),
        ("Prohibited practices (Art. 5)","None indicated"),
        ("Assessed on",DATE_STR)]))
    s.append(Paragraph("2 · Matched category", ST["h1"]))
    s.append(data_table([["Annex III reference","Why it applies"],
        ["§4 — Employment, recruitment & worker management",
         "The system screens, ranks and evaluates natural persons in a recruitment context; outputs materially influence hiring decisions."]],
        [6.2*cm, None]))
    s.append(Paragraph("3 · Obligations engaged", ST["h1"]))
    s.append(data_table([["Article","Requirement","Verispect coverage"],
        ["Art. 9","Risk management system","Continuous drift/bias telemetry feeds the risk file; this record is its first entry"],
        ["Art. 10","Data & bias governance","8-characteristic fairness probe evidence, monthly"],
        ["Art. 11","Technical documentation","Auto-generated DPIA + Annex IV pack (companion document)"],
        ["Art. 12","Record-keeping","Timestamped audit log"],
        ["Art. 13","Transparency","Exportable evidence + methodology statement"],
        ["Art. 14","Human oversight","Flagged events routed for human review"],
        ["Art. 15","Accuracy & robustness","Consistency probes + drift tracking"],
        ["Art. 72","Post-market monitoring","Continuous probe system (core function)"]],
        [1.9*cm, 5.6*cm, None]))
    s.append(Paragraph("4 · Review triggers", ST["h1"]))
    s.append(Paragraph("Re-classification is required if any of the following change: system purpose or domain; the degree "
        "of decision influence; deployment geography; or the matched Annex III category following legislative amendment "
        "(e.g. the pending Digital Omnibus). Verispect prompts re-assessment on each material change.", ST["body"]))
    s.append(Paragraph("5 · Legal notice", ST["h1"]))
    s.append(Paragraph(LIMITS, ST["body"]))
    s.append(Spacer(1, 10)); s.append(HRFlowable(width="100%", thickness=0.6, color=LINE)); s.append(Spacer(1, 8))
    s.append(Paragraph("Attestation", ST["h2"])); s.append(attestation(ref))
    doc.build(s, canvasmaker=Cv)

# ════════════════════════════════════════════════════════════════════════════
# DOC 3 — DPIA + ANNEX IV TECHNICAL DOCUMENTATION
# ════════════════════════════════════════════════════════════════════════════
def build_dpia():
    ref = "VSP-DP-2026-0610-SAMPLE"
    doc, Cv = make_doc("Verispect-SAMPLE-DPIA.pdf", "DPIA & Technical Documentation", ref)
    s = []
    s.append(CoverFlow("Data Protection Impact\nAssessment & Annex IV File",
                       "GDPR Art. 35 assessment and EU AI Act technical documentation,\npre-populated with live monitoring evidence.",
                       ref, "Acme HR GmbH (SAMPLE)", "DPIA · GDPR Art. 35 · AI Act Art. 11 / Annex IV"))
    s.append(NextPageTemplate("Body")); s.append(PageBreak())
    s.append(Paragraph("1 · System description (Annex IV §1)", ST["h1"]))
    s.append(kv_table([("System","CandidateRank AI"),("Operator","Acme HR GmbH"),
        ("Model","gpt-4o-mini (OpenAI) via one-line Verispect SDK"),
        ("Purpose","Automated screening and ranking of job applications"),
        ("Volume","≈ 500 monitored calls in the assessment period"),
        ("Monitoring layer","Verispect behavioural assurance — privacy-preserving (hashes + vectors only)")]))
    s.append(Paragraph("2 · Necessity & proportionality (Art. 35(7)(b))", ST["h1"]))
    s.append(Paragraph("Automated processing delivers consistent, scalable first-pass screening. Data processed is limited "
        "to application content required for the task. The monitoring layer adds <b>no</b> personal-data surface: Verispect "
        "receives only SHA-256 hashes and 384-dimension embedding vectors — a data-minimisation measure under Art. 25.", ST["body"]))
    s.append(Paragraph("3 · Risks to data subjects & mitigations", ST["h1"]))
    s.append(data_table([["Risk","L×S","Mitigation","Residual"],
        ["Discriminatory outcomes on protected characteristics","M×H","Continuous 8-category fairness probing; flagged events to human review; documented remediation (see §4)","Low-Med"],
        ["Model drift degrading decision quality","M×M","Golden-probe replay of live traffic; drift alerts; re-baseline protocol","Low"],
        ["Opaque automated decision (Art. 22)","M×H","Human-in-the-loop on all final decisions; candidate information notice","Low"],
        ["Input data breach","L×H","Monitoring receives no raw content; provider-side controls; encryption in transit/at rest","Low"]],
        [4.6*cm, 1.4*cm, None, 1.9*cm]))
    s.append(Paragraph("4 · Live monitoring evidence (assessment period)", ST["h1"]))
    s.append(data_table([["Indicator","Value"],
        ["Production calls monitored","500"],["Fairness/consistency probes","80"],
        ["Drift events flagged","11 (age: 4 · parental: 3 · other: 4)"],
        ["Average drift score","0.070"],["Consistency score","86.3%"]],
        [7.0*cm, None]))
    s.append(Spacer(1, 6))
    s.append(Paragraph("Flagged findings are recorded in the operator's Art. 9 risk log with remediation owners and "
        "verification dates (companion Monitoring Report, ref VSP-CR-2026-0610).", ST["body"]))
    s.append(Paragraph("5 · Post-market monitoring & review (Art. 72)", ST["h1"]))
    s.append(Paragraph("Continuous probing on sampled live traffic; monthly system-generated reports retained as technical "
        "documentation; re-assessment triggered by model/prompt change, drift alert, or quarterly review — whichever first.", ST["body"]))
    s.append(Paragraph("6 · Annex IV coverage index", ST["h1"]))
    s.append(data_table([["Annex IV item","Source"],
        ["§1 General description","This document, §1"],
        ["§2 Development & design","Operator build records (attach)"],
        ["§3 Monitoring & functioning metrics","§4 + companion Monitoring Report"],
        ["§4 Risk management (Art. 9)","§3 + operator risk log"],
        ["§5 Change log","Operator + Verispect re-baseline history"],
        ["§6 Standards applied","EU AI Act 2024/1689 · GDPR 2016/679"],
        ["§7 Declaration of conformity","Operator (post conformity assessment)"],
        ["§8 Post-market monitoring plan","§5 (Verispect continuous system)"]],
        [7.0*cm, None]))
    s.append(Paragraph("7 · DPO opinion & sign-off", ST["h1"]))
    s.append(data_table([["Field","Entry"],
        ["DPO opinion","[To be completed by the operator's DPO]"],
        ["Decision","Proceed / proceed with measures / do not proceed"],
        ["Approver & date","[Name · role · date]"]],
        [7.0*cm, None]))
    s.append(Paragraph("8 · Legal notice", ST["h1"]))
    s.append(Paragraph(LIMITS, ST["body"]))
    s.append(Spacer(1, 10)); s.append(HRFlowable(width="100%", thickness=0.6, color=LINE)); s.append(Spacer(1, 8))
    s.append(Paragraph("Attestation", ST["h2"])); s.append(attestation(ref))
    doc.build(s, canvasmaker=Cv)

if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    build_compliance(); print("OK Compliance Report")
    build_risk();       print("OK Risk Classification")
    build_dpia();       print("OK DPIA")
