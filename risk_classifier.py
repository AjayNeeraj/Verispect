"""
risk_classifier.py — Verispect "Risk Classifier" agent (Module 1).

EU AI Act risk classification from a short dashboard questionnaire.
NO SDK, NO ML, NO external key — pure rules + the existing PDF engine.
Customer answers ~6 questions in the dashboard; we output:
  - risk level (high / limited / minimal / prohibited-flag)
  - matched Annex III category
  - the obligations + articles that apply
  - a "Risk Classification Record" PDF (Art. 9 wants this documented)

Wire into FastAPI:  app.include_router(risk_router)
"""
from fastapi import APIRouter, Request
import io

risk_router = APIRouter(prefix="/api/risk")

# ── Annex III high-risk categories (questionnaire keys -> category) ───────────
ANNEX_III = {
    "hiring":      ("Annex III §4 — Employment, recruitment, worker management",
                    "AI used to screen, rank, or evaluate candidates / workers."),
    "credit":      ("Annex III §5(b) — Creditworthiness / credit scoring",
                    "AI used to evaluate creditworthiness or set credit scores (excl. fraud detection)."),
    "insurance":   ("Annex III §5(c) — Life & health insurance risk/pricing",
                    "AI used for risk assessment / pricing in life & health insurance."),
    "essential_services": ("Annex III §5(a) — Access to essential public/private services",
                    "AI deciding access to benefits, services, or resources."),
    "education":   ("Annex III §3 — Education & vocational training",
                    "AI deciding admission, evaluation, or proctoring."),
    "biometrics":  ("Annex III §1 — Biometric identification / categorisation",
                    "AI performing biometric ID or categorisation."),
    "law_justice": ("Annex III §6/§8 — Law enforcement / justice",
                    "AI assisting legal decisions, risk of offending, evidence evaluation."),
    "critical_infra": ("Annex III §2 — Critical infrastructure",
                    "AI as a safety component of critical infrastructure."),
}

# Article 5 prohibited-practice flags (hard stop)
PROHIBITED = {
    "social_scoring": "Art. 5 — social scoring of individuals (PROHIBITED)",
    "manipulation":   "Art. 5 — subliminal/manipulative techniques causing harm (PROHIBITED)",
    "biometric_mass_surveillance": "Art. 5 — untargeted scraping / real-time remote biometric ID (PROHIBITED/restricted)",
}

# Obligations that attach to a high-risk system (article -> what + how Verispect helps)
HIGH_RISK_OBLIGATIONS = [
    ("Art. 9",  "Risk management system",            "Verispect: drift alerts + this classification record feed it"),
    ("Art. 10", "Data & bias governance",            "Verispect: 8 fairness auditors, per-characteristic evidence"),
    ("Art. 11", "Technical documentation (Annex IV)", "Verispect: DPIA/Tech-Doc generator (Module 2)"),
    ("Art. 12", "Record-keeping / logging",          "Verispect: timestamped audit log"),
    ("Art. 13", "Transparency to deployers",         "Verispect: exportable evidence + methodology"),
    ("Art. 14", "Human oversight",                   "Verispect: flagged events + oversight log (roadmap)"),
    ("Art. 15", "Accuracy, robustness, consistency", "Verispect: consistency probes + drift tracking"),
    ("Art. 72", "Post-market monitoring",            "Verispect: continuous probing = this, core"),
]


def classify(answers: dict) -> dict:
    """
    answers: { "hiring": bool, "credit": bool, ..., "uses_llm_decision": bool,
               "eu_market": bool, "social_scoring": bool, ... }
    Returns full classification dict.
    """
    # 1) Prohibited check first (hard stop)
    prohibited_hits = [PROHIBITED[k] for k in PROHIBITED if answers.get(k)]
    if prohibited_hits:
        return {
            "risk_level": "PROHIBITED",
            "headline": "One or more practices may be banned under Art. 5.",
            "prohibited": prohibited_hits,
            "categories": [],
            "obligations": [],
            "note": "Stop and get legal advice — prohibited practices cannot be deployed in the EU.",
        }

    # 2) Annex III high-risk match
    matched = []
    for key, (cat, desc) in ANNEX_III.items():
        if answers.get(key):
            matched.append({"category": cat, "description": desc})

    in_eu = answers.get("eu_market", True)
    makes_decision = answers.get("uses_llm_decision", True)

    if matched and makes_decision:
        level = "HIGH-RISK"
        headline = ("Your AI system is HIGH-RISK under EU AI Act Annex III. "
                    "Full high-risk obligations apply (operative 2 Aug 2026).")
        obligations = [
            {"article": a, "requirement": r, "verispect": v} for a, r, v in HIGH_RISK_OBLIGATIONS
        ]
    elif matched and not makes_decision:
        level = "LIMITED-RISK"
        headline = ("Your AI touches a high-risk domain but only assists (no decision). "
                    "Transparency obligations likely; monitor scope creep.")
        obligations = [{"article": "Art. 50", "requirement": "Transparency to users",
                        "verispect": "Verispect: evidence + monitoring if scope grows"}]
    else:
        level = "MINIMAL-RISK"
        headline = "No Annex III high-risk category matched. Minimal obligations today."
        obligations = []

    if not in_eu:
        headline += " (Note: you indicated no EU/EEA market — re-check if any EU users exist.)"

    return {
        "risk_level": level,
        "headline": headline,
        "prohibited": [],
        "categories": matched,
        "obligations": obligations,
        "answers": answers,
    }


# ── Questionnaire definition (drives the dashboard wizard) ────────────────────
QUESTIONS = [
    ("hiring",            "Does your AI screen, rank, or evaluate job candidates or workers?"),
    ("credit",            "Does it assess creditworthiness or set credit scores?"),
    ("insurance",         "Does it do risk assessment or pricing for life/health insurance?"),
    ("essential_services","Does it decide access to benefits or essential services?"),
    ("education",         "Does it decide admissions, grading, or proctoring?"),
    ("biometrics",        "Does it perform biometric identification or categorisation?"),
    ("law_justice",       "Does it assist law-enforcement or legal/judicial decisions?"),
    ("critical_infra",    "Is it a safety component of critical infrastructure?"),
    ("uses_llm_decision", "Does the AI make or materially influence the final decision?"),
    ("eu_market",         "Do you have users or customers in the EU/EEA?"),
    ("social_scoring",    "Does it score/rank individuals' trustworthiness across contexts? (Art.5)"),
]


@risk_router.post("/classify")
async def classify_endpoint(request: Request):
    answers = await request.json()
    return classify(answers)


@risk_router.get("/questions")
async def questions_endpoint():
    return [{"key": k, "question": q} for k, q in QUESTIONS]


def build_pdf(result: dict, company: str = "Confidential") -> bytes:
    """Risk Classification Record PDF — reuses the brand styling of api.py reports."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

    PURPLE = colors.HexColor("#7c6eff"); DARK = colors.HexColor("#111827")
    GRAY = colors.HexColor("#6b7280"); BORDER = colors.HexColor("#e5e7eb")
    GRAY_LT = colors.HexColor("#f9fafb"); WHITE = colors.white
    RED = colors.HexColor("#ef4444"); GREEN = colors.HexColor("#10b981"); AMBER = colors.HexColor("#f59e0b")
    sty = getSampleStyleSheet()
    def S(n, **k): return ParagraphStyle(n, parent=sty["Normal"], **k)
    brand = S("b", fontSize=24, textColor=PURPLE, fontName="Helvetica-Bold")
    h2 = S("h2", fontSize=13, textColor=DARK, fontName="Helvetica-Bold", spaceBefore=12, spaceAfter=5)
    body = S("body", fontSize=9.5, textColor=DARK, leading=14, spaceAfter=4)
    small = S("s", fontSize=7.5, textColor=GRAY, leading=10)

    lvl = result["risk_level"]
    lvl_color = {"HIGH-RISK": RED, "PROHIBITED": RED, "LIMITED-RISK": AMBER, "MINIMAL-RISK": GREEN}.get(lvl, GRAY)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=1.8*cm, bottomMargin=1.8*cm)
    st = [Paragraph("Verispect", brand),
          Paragraph("AI Act Risk Classification Record", S("t", fontSize=11, textColor=GRAY)),
          HRFlowable(width="100%", thickness=2, color=PURPLE, spaceAfter=10)]
    st.append(Table([[Paragraph(f'<font size=22 color="{lvl_color.hexval()}"><b>{lvl}</b></font>', body),
                      Paragraph(result["headline"], body)]], colWidths=[4.5*cm, None],
                    style=TableStyle([("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                                      ("BACKGROUND", (0,0), (0,0), GRAY_LT),
                                      ("BOX", (0,0), (-1,-1), 0.5, BORDER), ("PADDING", (0,0), (-1,-1), 12)])))
    st.append(Paragraph(f"Prepared for: <b>{company}</b> · Regulation: EU AI Act (2024/1689)", small))

    if result.get("prohibited"):
        st.append(Paragraph("Prohibited-practice flags", h2))
        for p in result["prohibited"]:
            st.append(Paragraph("⛔ " + p, body))

    if result.get("categories"):
        st.append(Paragraph("Matched high-risk categories", h2))
        rows = [["Annex III category", "Why"]] + [[c["category"], c["description"]] for c in result["categories"]]
        t = Table(rows, colWidths=[6.5*cm, None])
        t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), DARK), ("TEXTCOLOR", (0,0), (-1,0), WHITE),
                               ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"), ("FONTSIZE", (0,0), (-1,-1), 8.5),
                               ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, GRAY_LT]),
                               ("GRID", (0,0), (-1,-1), 0.3, BORDER), ("VALIGN", (0,0), (-1,-1), "TOP"),
                               ("PADDING", (0,0), (-1,-1), 6)]))
        st.append(t)

    if result.get("obligations"):
        st.append(Paragraph("Obligations that apply — and how Verispect covers them", h2))
        rows = [["Article", "Requirement", "Verispect coverage"]] + \
               [[o["article"], o["requirement"], o["verispect"]] for o in result["obligations"]]
        t = Table(rows, colWidths=[2*cm, 5*cm, None])
        t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), PURPLE), ("TEXTCOLOR", (0,0), (-1,0), WHITE),
                               ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"), ("FONTSIZE", (0,0), (-1,-1), 8),
                               ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, GRAY_LT]),
                               ("GRID", (0,0), (-1,-1), 0.3, BORDER), ("VALIGN", (0,0), (-1,-1), "TOP"),
                               ("PADDING", (0,0), (-1,-1), 6)]))
        st.append(t)

    st.append(Spacer(1, 14))
    st.append(Paragraph("This record supports your Art. 9 risk-management documentation. It is decision-support, "
                        "not legal advice or certification; the operator remains responsible.", small))
    doc.build(st)
    buf.seek(0)
    return buf.read()


if __name__ == "__main__":
    # Demo: an HR-tech using an LLM to screen candidates, EU market.
    demo = {"hiring": True, "uses_llm_decision": True, "eu_market": True}
    r = classify(demo)
    print("RISK LEVEL:", r["risk_level"])
    print("HEADLINE:", r["headline"])
    print("CATEGORIES:", [c["category"] for c in r["categories"]])
    print("OBLIGATIONS:", len(r["obligations"]), "articles")
    pdf = build_pdf(r, company="Acme HR GmbH (DEMO)")
    with open("Risk-Classification-DEMO.pdf", "wb") as f:
        f.write(pdf)
    print("PDF bytes:", len(pdf), "-> Risk-Classification-DEMO.pdf")
