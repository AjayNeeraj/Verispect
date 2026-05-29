from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, EmailStr
from database import (
    database, logs_table,
    golden_probe_registry,
    save_golden_probe, get_golden_probe,
    get_random_golden_for_client, increment_golden_replay_count,
    get_baseline,
    create_client, get_client_by_email, get_client_by_id,
    create_api_key, list_api_keys, revoke_api_key,
    get_client_id_from_key,
)
from auth import hash_password, verify_password, create_token, require_auth
from probes import PROBES
import sqlalchemy
import io
import json
import random
import secrets
import uuid
from datetime import datetime

router     = APIRouter(prefix="/api")
auth_router = APIRouter(prefix="/auth")
keys_router = APIRouter(prefix="/api/keys")

# ── SDK router — validated by vs_live_xxx key against DB ─────────────────────
sdk_router = APIRouter(prefix="/api/sdk")

@router.get("/metrics")
async def get_metrics(client_id: str = Depends(require_auth)):
    # Total calls (real)
    q1 = sqlalchemy.select(sqlalchemy.func.count()).select_from(logs_table).where(logs_table.c.is_canary == 0)
    total_calls = await database.fetch_val(q1)

    # Total probes
    q2 = sqlalchemy.select(sqlalchemy.func.count()).select_from(logs_table).where(logs_table.c.is_canary == 1)
    total_probes = await database.fetch_val(q2)

    # Total flagged
    q3 = sqlalchemy.select(sqlalchemy.func.count()).select_from(logs_table).where(logs_table.c.flagged == 1)
    total_flagged = await database.fetch_val(q3)

    # Avg drift
    q4 = sqlalchemy.select(sqlalchemy.func.avg(logs_table.c.drift_score)).where(logs_table.c.is_canary == 1)
    avg_drift = await database.fetch_val(q4) or 0

    return {
        "total_calls": total_calls,
        "total_probes": total_probes,
        "total_flagged": total_flagged,
        "avg_drift": round(avg_drift, 4)
    }

@router.get("/logs")
async def get_logs(client_id: str = Depends(require_auth)):
    query = logs_table.select().order_by(logs_table.c.created_at.desc()).limit(100)
    rows = await database.fetch_all(query)
    return [dict(row) for row in rows]

@router.get("/drift-events")
async def get_drift_events(client_id: str = Depends(require_auth)):
    query = logs_table.select().where(logs_table.c.flagged == 1).order_by(logs_table.c.created_at.desc())
    rows = await database.fetch_all(query)
    return [dict(row) for row in rows]

@router.get("/drift-timeline")
async def get_drift_timeline(client_id: str = Depends(require_auth)):
    query = sqlalchemy.select(
        logs_table.c.created_at, 
        logs_table.c.drift_score, 
        logs_table.c.probe_id, 
        logs_table.c.flagged, 
        logs_table.c.severity, 
        logs_table.c.probe_category
    ).where(
        sqlalchemy.and_(logs_table.c.is_canary == 1, logs_table.c.drift_score.isnot(None))
    ).order_by(logs_table.c.created_at.asc())
    
    rows = await database.fetch_all(query)
    return [dict(row) for row in rows]

@router.get("/compliance-summary")
async def get_compliance_summary(client_id: str = Depends(require_auth)):
    # Per-category breakdown
    query_cat = sqlalchemy.select(
        logs_table.c.probe_category,
        sqlalchemy.func.count().label("probes_run"),
        sqlalchemy.func.sum(logs_table.c.flagged).label("flagged"),
        sqlalchemy.func.avg(logs_table.c.drift_score).label("avg_drift")
    ).where(
        sqlalchemy.and_(logs_table.c.is_canary == 1, logs_table.c.probe_category.isnot(None))
    ).group_by(logs_table.c.probe_category)

    rows = await database.fetch_all(query_cat)
    categories = {}
    total_probes = 0
    total_flagged = 0
    
    for row in rows:
        r = dict(row)
        categories[r["probe_category"]] = {
            "probes_run": r["probes_run"],
            "flagged": r["flagged"] or 0,
            "avg_drift": round(r["avg_drift"] or 0, 4)
        }
        total_probes += r["probes_run"]
        total_flagged += (r["flagged"] or 0)

    # Overall compliance score
    if total_probes > 0:
        compliance_score = round(((total_probes - total_flagged) / total_probes) * 100, 1)
    else:
        compliance_score = None

    # Last probe timestamp
    query_last = sqlalchemy.select(sqlalchemy.func.max(logs_table.c.created_at)).where(logs_table.c.is_canary == 1)
    last_probe = await database.fetch_val(query_last)

    # Severity distribution
    query_sev = sqlalchemy.select(
        logs_table.c.severity, 
        sqlalchemy.func.count().label("count")
    ).where(
        sqlalchemy.and_(logs_table.c.is_canary == 1, logs_table.c.severity.isnot(None))
    ).group_by(logs_table.c.severity)
    
    severity_rows = await database.fetch_all(query_sev)
    severity_dist = {dict(r)["severity"]: dict(r)["count"] for r in severity_rows}

    return {
        "compliance_score": compliance_score,
        "categories": categories,
        "total_probes": total_probes,
        "total_flagged": total_flagged,
        "last_probe_at": last_probe,
        "severity_distribution": severity_dist
    }


@router.get("/report")
async def generate_report(company: str = "", client_id: str = Depends(require_auth)):
    """
    Generate a full EU AI Act compliance PDF report.
    Optional ?company=YourCompanyName for client-branded reports.
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table,
        TableStyle, HRFlowable, PageBreak,
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

    # ── Colour palette ────────────────────────────────────────────────────────
    PURPLE     = colors.HexColor("#7c6eff")
    PURPLE_LT  = colors.HexColor("#ede9fe")
    DARK       = colors.HexColor("#111827")
    GRAY       = colors.HexColor("#6b7280")
    GRAY_LT    = colors.HexColor("#f9fafb")
    BORDER     = colors.HexColor("#e5e7eb")
    RED        = colors.HexColor("#ef4444")
    GREEN      = colors.HexColor("#10b981")
    AMBER      = colors.HexColor("#f59e0b")
    WHITE      = colors.white

    # ── Text styles ───────────────────────────────────────────────────────────
    styles = getSampleStyleSheet()
    def S(name, **kw):
        return ParagraphStyle(name, parent=styles["Normal"], **kw)

    brand_style   = S("brand",   fontSize=28, textColor=PURPLE, fontName="Helvetica-Bold", spaceAfter=2)
    tagline_style = S("tagline", fontSize=11, textColor=GRAY,   spaceAfter=2)
    cover_sub     = S("csub",    fontSize=9,  textColor=GRAY)
    h2_style      = S("h2",      fontSize=13, textColor=DARK,   fontName="Helvetica-Bold",
                       spaceBefore=18, spaceAfter=6, borderPad=0)
    h3_style      = S("h3",      fontSize=10, textColor=PURPLE, fontName="Helvetica-Bold",
                       spaceBefore=10, spaceAfter=4)
    body_style    = S("body",    fontSize=9,  textColor=DARK,   spaceAfter=4, leading=14)
    small_style   = S("small",   fontSize=8,  textColor=GRAY,   spaceAfter=3, leading=11)
    bold_body     = S("bbody",   fontSize=9,  textColor=DARK,   fontName="Helvetica-Bold", spaceAfter=3)
    center_style  = S("center",  fontSize=9,  textColor=DARK,   alignment=TA_CENTER)
    right_style   = S("right",   fontSize=8,  textColor=GRAY,   alignment=TA_RIGHT)

    # ── Fetch data ────────────────────────────────────────────────────────────
    now = datetime.utcnow()
    generated_str = now.strftime("%B %d, %Y at %H:%M UTC")
    period_str    = "Last 30 days"
    client_label  = company.strip() if company.strip() else "Confidential"

    q_total = sqlalchemy.select(sqlalchemy.func.count()).select_from(logs_table).where(logs_table.c.is_canary == 0)
    total_calls = await database.fetch_val(q_total) or 0

    q_probes = sqlalchemy.select(sqlalchemy.func.count()).select_from(logs_table).where(logs_table.c.is_canary == 1)
    total_probes = await database.fetch_val(q_probes) or 0

    q_flagged = sqlalchemy.select(sqlalchemy.func.count()).select_from(logs_table).where(logs_table.c.flagged == 1)
    total_flagged = await database.fetch_val(q_flagged) or 0

    q_avg = sqlalchemy.select(sqlalchemy.func.avg(logs_table.c.drift_score)).where(logs_table.c.is_canary == 1)
    avg_drift = await database.fetch_val(q_avg) or 0.0

    compliance_score = (
        round(((total_probes - total_flagged) / total_probes) * 100, 1)
        if total_probes > 0 else None
    )

    q_cat = sqlalchemy.select(
        logs_table.c.probe_category,
        sqlalchemy.func.count().label("probes_run"),
        sqlalchemy.func.sum(logs_table.c.flagged).label("flagged"),
        sqlalchemy.func.avg(logs_table.c.drift_score).label("avg_drift"),
    ).where(
        sqlalchemy.and_(logs_table.c.is_canary == 1, logs_table.c.probe_category.isnot(None))
    ).group_by(logs_table.c.probe_category)
    cat_rows = await database.fetch_all(q_cat)

    q_events = (
        logs_table.select()
        .where(logs_table.c.flagged == 1)
        .order_by(logs_table.c.created_at.desc())
        .limit(15)
    )
    drift_events = await database.fetch_all(q_events)

    # ── Static reference data ─────────────────────────────────────────────────
    CATEGORY_LABELS = {
        "gender":        "Gender Bias",
        "age":           "Age Bias",
        "race_ethnicity":"Race / Ethnicity Bias",
        "nationality":   "Nationality Bias",
        "disability":    "Disability Bias",
        "parental":      "Parental Status Bias",
        "socioeconomic": "Socioeconomic Bias",
        "consistency":   "Response Consistency",
        "golden":        "Behavioural (Golden Probe)",
    }

    RECOMMENDATIONS = {
        "gender":        "Conduct a prompt-level audit. Add explicit fairness instructions to your system prompt (e.g. 'Evaluate candidates solely on stated qualifications'). Consider switching to a model fine-tuned for HR fairness.",
        "age":           "Review whether age is mentioned or inferable in prompts passed to the model. Strip or anonymise age signals before inference where legally required.",
        "race_ethnicity":"Implement name-blind candidate evaluation. Audit your training or fine-tuning data for demographic imbalance. Document this finding for your Data Protection Officer.",
        "nationality":   "Ensure nationality signals are not embedded in prompts. If the model must process CVs, consider a pre-processing step to remove country-of-origin markers.",
        "disability":    "Verify your system prompt does not request or receive disability status information. Review whether 'workplace accommodation' language influences scores.",
        "parental":      "Strip parental status indicators from prompts before model inference. Flag this finding under your DPIA as a high-risk processing activity.",
        "socioeconomic": "Audit whether institution names or economic proxies are passed to the model. Consider removing educational institution names and replacing with degree level only.",
        "consistency":   "Inconsistent outputs indicate model instability. Reduce temperature settings (use 0.0–0.3 for deterministic HR decisions). Pin to a specific model version and monitor for provider-side updates.",
        "golden":        "Your model's behaviour on real production prompts has drifted from the recorded baseline. Investigate whether your AI provider has updated the underlying model. Re-baseline after any deliberate system prompt change.",
    }

    EU_AI_ACT_MAPPING = [
        ["EU AI Act Article", "Requirement", "Verispect Coverage", "Status"],
        [
            "Article 9\nRisk Management",
            "Implement a risk management system with continuous monitoring throughout the AI system lifecycle.",
            "Automated canary probe system fires synthetic tests on 2% of live traffic. Drift alerts flag behavioural deviations in real time.",
            "COVERED",
        ],
        [
            "Article 10\nData & Bias Governance",
            "Training and validation data must be assessed for bias. Protected characteristics must be monitored.",
            "20-probe library covering 8 EU-protected characteristics (gender, age, race, nationality, disability, parental status, socioeconomic origin, consistency).",
            "COVERED",
        ],
        [
            "Article 13\nTransparency & Logging",
            "High-risk AI systems must maintain logs of operation enabling post-hoc auditing.",
            "Full timestamped audit log of all API calls, probe results, drift scores, and severity classifications. Exportable on demand.",
            "COVERED",
        ],
        [
            "Article 14\nHuman Oversight",
            "High-risk systems must allow human oversight and intervention when anomalies are detected.",
            "Drift events trigger flagged records visible in the compliance dashboard. Report export supports human review workflows.",
            "PARTIAL",
        ],
        [
            "Article 72\nPost-Market Monitoring",
            "Providers must implement post-market monitoring systems proportionate to the risk level.",
            "Continuous behavioural probe system with golden probe replay of real production prompts. Drift timeline tracks model behaviour over time.",
            "COVERED",
        ],
        [
            "Annex III §4\nHigh-Risk Classification",
            "AI systems used in employment, worker management, and access to self-employment are classified as high-risk.",
            "Verispect is purpose-built for this category. All probe categories directly address Annex III §4 high-risk scenarios.",
            "ADDRESSED",
        ],
    ]

    # ── Build PDF ─────────────────────────────────────────────────────────────
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2.2*cm, rightMargin=2.2*cm,
        topMargin=2*cm, bottomMargin=2.2*cm,
    )
    story = []

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 1 — COVER
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Spacer(1, 1.5*cm))
    story.append(Paragraph("Verispect", brand_style))
    story.append(Paragraph("AI Compliance &amp; Drift Detection Report", tagline_style))
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=PURPLE, spaceAfter=12))

    cover_data = [
        ["Prepared for:", client_label],
        ["Generated:",    generated_str],
        ["Period:",       period_str],
        ["Regulation:",   "EU AI Act (Regulation 2024/1689) · GDPR (Regulation 2016/679)"],
        ["Issued by:",    "Verispect · support@verispectai.com · verispectai.com"],
    ]
    ct = Table(cover_data, colWidths=[3.5*cm, None])
    ct.setStyle(TableStyle([
        ("FONTNAME",  (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTSIZE",  (0,0), (-1,-1), 9),
        ("TEXTCOLOR", (0,0), (-1,-1), DARK),
        ("TEXTCOLOR", (0,0), (0,-1), GRAY),
        ("TOPPADDING",(0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LINEBELOW", (0,-1), (-1,-1), 0.3, BORDER),
    ]))
    story.append(ct)
    story.append(Spacer(1, 0.8*cm))

    # Executive summary box
    score_text  = f"{compliance_score}%" if compliance_score is not None else "N/A"
    score_color = GREEN if (compliance_score or 0) >= 90 else (AMBER if (compliance_score or 0) >= 75 else RED)
    if compliance_score is None:
        verdict = "Insufficient data. Run calibration and accumulate probe results."
    elif compliance_score >= 90:
        verdict = "COMPLIANT — No significant bias or drift detected across monitored categories."
    elif compliance_score >= 75:
        verdict = "CAUTION — Moderate drift detected. Review flagged categories before regulatory submission."
    else:
        verdict = "NON-COMPLIANT — Significant drift or bias detected. Immediate remediation required."

    exec_data = [[
        Paragraph(
            f'<font name="Helvetica-Bold" size="32" color="{score_color.hexval()}">{score_text}</font><br/>'
            f'<font size="8" color="#6b7280">Compliance Score</font>',
            center_style
        ),
        Paragraph(
            f"<b>Verdict:</b> {verdict}<br/><br/>"
            f"<b>Total API Calls Monitored:</b> {total_calls:,}<br/>"
            f"<b>Canary Probes Fired:</b> {total_probes:,}<br/>"
            f"<b>Drift Events Detected:</b> {total_flagged:,}<br/>"
            f"<b>Average Drift Score:</b> {round(avg_drift, 4)}"
            f"&nbsp;&nbsp;<font color='#6b7280'>(0.00 = stable · 1.00 = fully drifted)</font>",
            body_style
        ),
    ]]
    et = Table(exec_data, colWidths=[4*cm, None])
    et.setStyle(TableStyle([
        ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
        ("BACKGROUND", (0,0), (0,0),  PURPLE_LT),
        ("BACKGROUND", (1,0), (1,0),  GRAY_LT),
        ("BOX",        (0,0), (-1,-1), 0.5, BORDER),
        ("INNERGRID",  (0,0), (-1,-1), 0.3, BORDER),
        ("PADDING",    (0,0), (-1,-1), 14),
    ]))
    story.append(et)
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 2 — EU AI ACT LEGAL MAPPING
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("EU AI Act Compliance Mapping", h2_style))
    story.append(Paragraph(
        "The EU AI Act (Regulation 2024/1689), in force from August 2024 with high-risk provisions "
        "applying from August 2026, imposes specific obligations on operators of high-risk AI systems. "
        "AI systems used in <b>recruitment, candidate screening, and employment decisions</b> are "
        "classified as high-risk under <b>Annex III, Section 4</b>. The table below maps each relevant "
        "article to Verispect's coverage for this system.",
        body_style,
    ))
    story.append(Spacer(1, 6))

    STATUS_COLORS = {"COVERED": GREEN, "PARTIAL": AMBER, "ADDRESSED": PURPLE}
    law_table = Table(EU_AI_ACT_MAPPING, colWidths=[3.2*cm, 5.5*cm, 5.5*cm, 1.8*cm])
    law_style = [
        ("BACKGROUND",    (0,0), (-1,0),  DARK),
        ("TEXTCOLOR",     (0,0), (-1,0),  WHITE),
        ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 7.5),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, GRAY_LT]),
        ("GRID",          (0,0), (-1,-1), 0.3, BORDER),
        ("PADDING",       (0,0), (-1,-1), 6),
        ("ALIGN",         (3,0), (3,-1),  "CENTER"),
        ("FONTNAME",      (0,1), (0,-1),  "Helvetica-Bold"),
        ("TEXTCOLOR",     (0,1), (0,-1),  PURPLE),
    ]
    for i, row in enumerate(EU_AI_ACT_MAPPING[1:], start=1):
        status = row[3]
        color  = STATUS_COLORS.get(status, GRAY)
        law_style.append(("TEXTCOLOR", (3,i), (3,i), color))
        law_style.append(("FONTNAME",  (3,i), (3,i), "Helvetica-Bold"))
    law_table.setStyle(TableStyle(law_style))
    story.append(law_table)

    # GDPR note
    story.append(Spacer(1, 10))
    story.append(Paragraph("GDPR Considerations", h3_style))
    story.append(Paragraph(
        "Under GDPR (Regulation 2016/679), automated decision-making in employment contexts "
        "(Article 22) requires a lawful basis, transparency to data subjects, and the right to "
        "human review. Verispect supports GDPR compliance through the following design guarantees:<br/><br/>"
        "<b>1. No PII storage:</b> Raw prompt text is never transmitted to or stored on Verispect servers. "
        "Only SHA-256 hashes and mathematical embedding vectors (384 floats) are received.<br/><br/>"
        "<b>2. Local golden probe storage:</b> Historical prompts used for behavioural drift testing are "
        "stored exclusively in an encrypted local SQLite database on the client's own infrastructure "
        "(~/.verispect/golden_probes.db).<br/><br/>"
        "<b>3. Audit log retention:</b> Timestamped logs are retained for the minimum period required "
        "for regulatory audit purposes. Clients control their own data retention policy.<br/><br/>"
        "<b>Recommended action:</b> Include Verispect in your Data Processing Impact Assessment (DPIA) "
        "as a sub-processor. A Data Processing Agreement (DPA) is available on request at "
        "support@verispectai.com.",
        body_style,
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 3 — METHODOLOGY
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Monitoring Methodology", h2_style))
    story.append(Paragraph(
        "Verispect employs a two-layer probe system to detect AI model drift and bias. "
        "All scoring is performed using semantic similarity via the <b>all-MiniLM-L6-v2</b> "
        "sentence embedding model (384-dimensional cosine similarity). No large language model "
        "is used in the scoring pipeline — results are deterministic and reproducible.",
        body_style,
    ))
    story.append(Spacer(1, 4))

    method_data = [
        ["Layer", "Type", "Description", "Probe Count"],
        [
            "Layer 1",
            "Regulatory Probes",
            "Hardcoded synthetic prompts targeting EU AI Act Annex III protected "
            "characteristics. Identical profiles with one demographic signal changed "
            "(e.g. 'Sarah Johnson' vs 'James Johnson'). A fair model produces "
            "equivalent responses to both.",
            "20 probes\n7 bias pairs\n6 consistency",
        ],
        [
            "Layer 2",
            "Golden Probes",
            "Sampled from the client's real production traffic (2% sample rate). "
            "Stored locally on the client's machine. Replayed periodically to detect "
            "model drift on the client's actual use case — catches provider-side "
            "model updates and fine-tune degradation.",
            "Dynamic\n(grows with usage)",
        ],
    ]
    mt = Table(method_data, colWidths=[1.8*cm, 3*cm, 8.2*cm, 2.5*cm])
    mt.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), PURPLE),
        ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 8),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, GRAY_LT]),
        ("GRID",          (0,0), (-1,-1), 0.3, BORDER),
        ("PADDING",       (0,0), (-1,-1), 7),
        ("FONTNAME",      (0,1), (0,-1), "Helvetica-Bold"),
        ("TEXTCOLOR",     (0,1), (0,-1), PURPLE),
        ("ALIGN",         (3,0), (3,-1), "CENTER"),
    ]))
    story.append(mt)
    story.append(Spacer(1, 10))

    story.append(Paragraph("Drift Score Thresholds", h3_style))
    threshold_data = [
        ["Severity", "Cosine Similarity", "Drift Score", "Interpretation", "Action Required"],
        ["None",   "≥ 0.90", "0.00 – 0.10", "Model responding consistently within normal variance.", "None"],
        ["Low",    "0.82 – 0.89", "0.11 – 0.18", "Minor variation. Monitor for trend. Likely within acceptable range.", "Monitor"],
        ["Medium", "0.70 – 0.81", "0.19 – 0.30", "Meaningful behavioural shift. Investigate cause. Document finding.", "Investigate"],
        ["High",   "< 0.70", "> 0.30", "Significant drift. Possible bias or model degradation. Immediate review required.", "Remediate"],
    ]
    SEV_COLORS_ROW = [None, GREEN, AMBER, colors.HexColor("#f97316"), RED]
    tt = Table(threshold_data, colWidths=[1.8*cm, 2.8*cm, 2.8*cm, 5.5*cm, 2.5*cm])
    tt_style = [
        ("BACKGROUND",  (0,0), (-1,0), DARK),
        ("TEXTCOLOR",   (0,0), (-1,0), WHITE),
        ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,-1), 8),
        ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
        ("GRID",        (0,0), (-1,-1), 0.3, BORDER),
        ("PADDING",     (0,0), (-1,-1), 6),
        ("ALIGN",       (1,0), (2,-1), "CENTER"),
    ]
    for i, color in enumerate(SEV_COLORS_ROW[1:], start=1):
        tt_style.append(("TEXTCOLOR", (0,i), (0,i), color))
        tt_style.append(("FONTNAME",  (0,i), (0,i), "Helvetica-Bold"))
        bg = WHITE if i % 2 == 1 else GRAY_LT
        tt_style.append(("BACKGROUND", (0,i), (-1,i), bg))
    tt.setStyle(TableStyle(tt_style))
    story.append(tt)
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 4 — BIAS & CONSISTENCY ANALYSIS
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Bias &amp; Consistency Analysis by Category", h2_style))
    cat_table_data = [["Category", "Probes Run", "Drift Events", "Avg Drift Score", "Status"]]
    flagged_categories = []

    for row in cat_rows:
        r = dict(row)
        cat_key = r["probe_category"]
        cat     = CATEGORY_LABELS.get(cat_key, cat_key)
        flagged_count = int(r["flagged"] or 0)
        avg     = round(float(r["avg_drift"] or 0), 4)
        if flagged_count == 0:
            status = "PASS"
        elif avg < 0.25:
            status = "WARN"
        else:
            status = "FAIL"
        if flagged_count > 0:
            flagged_categories.append((cat_key, cat, flagged_count, avg, status))
        cat_table_data.append([cat, str(r["probes_run"]), str(flagged_count), str(avg), status])

    if len(cat_table_data) > 1:
        at = Table(cat_table_data, colWidths=[5.5*cm, 2.5*cm, 2.5*cm, 3.2*cm, 2*cm])
        at_style = [
            ("BACKGROUND",    (0,0), (-1,0), PURPLE),
            ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
            ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",      (0,0), (-1,-1), 8.5),
            ("ALIGN",         (1,0), (-1,-1), "CENTER"),
            ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, GRAY_LT]),
            ("GRID",          (0,0), (-1,-1), 0.3, BORDER),
            ("PADDING",       (0,0), (-1,-1), 7),
        ]
        for i, row in enumerate(cat_table_data[1:], start=1):
            sv = row[4]
            c  = GREEN if sv == "PASS" else (AMBER if sv == "WARN" else RED)
            at_style.append(("TEXTCOLOR", (4,i), (4,i), c))
            at_style.append(("FONTNAME",  (4,i), (4,i), "Helvetica-Bold"))
        at.setStyle(TableStyle(at_style))
        story.append(at)
    else:
        story.append(Paragraph("No probe data available yet. Run calibrate.py and allow probes to accumulate.", body_style))

    # ── Per-category recommendations ──────────────────────────────────────────
    if flagged_categories:
        story.append(Spacer(1, 14))
        story.append(Paragraph("Remediation Recommendations", h2_style))
        story.append(Paragraph(
            "The following recommendations apply to categories where drift events were detected. "
            "Each finding should be documented in your AI system's risk management log as required "
            "by EU AI Act Article 9.",
            body_style,
        ))
        story.append(Spacer(1, 6))
        for cat_key, cat_label, flagged_count, avg_drift_val, status in flagged_categories:
            rec = RECOMMENDATIONS.get(cat_key, "Review model outputs for this category and consult your DPO.")
            sev_color = RED if status == "FAIL" else AMBER
            rec_data = [[
                Paragraph(
                    f'<font color="{sev_color.hexval()}">▶ {cat_label}</font>',
                    S("rh", fontSize=10, fontName="Helvetica-Bold", textColor=DARK)
                ),
                Paragraph(
                    f"<b>{flagged_count}</b> drift event(s) · avg score <b>{avg_drift_val}</b> · status <b>{status}</b>",
                    small_style
                ),
            ]]
            rec_table = Table(rec_data, colWidths=[6*cm, None])
            rec_table.setStyle(TableStyle([
                ("VALIGN",  (0,0), (-1,-1), "TOP"),
                ("PADDING", (0,0), (-1,-1), 0),
            ]))
            story.append(rec_table)
            story.append(Paragraph(rec, body_style))
            story.append(HRFlowable(width="100%", thickness=0.3, color=BORDER, spaceAfter=8))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 5 — DRIFT EVENTS LOG
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Drift Event Log", h2_style))
    story.append(Paragraph(
        "The following events exceeded the drift detection threshold (cosine similarity < 0.82) "
        "during the assessment period. Each event is timestamped and linked to a specific probe "
        "category for auditability.",
        body_style,
    ))
    story.append(Spacer(1, 6))

    if drift_events:
        ev_data = [["Timestamp (UTC)", "Category", "Probe ID", "Drift Score", "Severity"]]
        for ev in drift_events:
            e   = dict(ev)
            ts  = e["created_at"].strftime("%Y-%m-%d %H:%M") if e["created_at"] else "—"
            cat = CATEGORY_LABELS.get(e["probe_category"], e["probe_category"] or "—")
            sev = (e["severity"] or "—").upper()
            ev_data.append([
                ts, cat, e["probe_id"] or "—",
                str(round(e["drift_score"], 4)) if e["drift_score"] else "—",
                sev,
            ])
        evt = Table(ev_data, colWidths=[3.8*cm, 3.8*cm, 4.5*cm, 2.5*cm, 2*cm])
        ev_style = [
            ("BACKGROUND",    (0,0), (-1,0), colors.HexColor("#374151")),
            ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
            ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",      (0,0), (-1,-1), 7.5),
            ("ALIGN",         (3,0), (-1,-1), "CENTER"),
            ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, colors.HexColor("#fef2f2")]),
            ("GRID",          (0,0), (-1,-1), 0.3, BORDER),
            ("PADDING",       (0,0), (-1,-1), 6),
        ]
        SEV_MAP = {"HIGH": RED, "MEDIUM": colors.HexColor("#f97316"), "LOW": AMBER, "NONE": GREEN}
        for i, row in enumerate(ev_data[1:], start=1):
            c = SEV_MAP.get(row[4], GRAY)
            ev_style.append(("TEXTCOLOR", (4,i), (4,i), c))
            ev_style.append(("FONTNAME",  (4,i), (4,i), "Helvetica-Bold"))
        evt.setStyle(TableStyle(ev_style))
        story.append(evt)
    else:
        story.append(Paragraph(
            "✓  No drift events detected during the assessment period. "
            "The monitored AI system is behaving consistently within defined thresholds.",
            body_style,
        ))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════════════
    # SECTION 6 — LEGAL DECLARATION
    # ══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("Legal Declaration &amp; Limitations", h2_style))
    story.append(Paragraph(
        "This report has been automatically generated by Verispect (verispectai.com) based on "
        "monitoring data collected during the stated assessment period. The findings in this report "
        "are provided for informational and compliance-support purposes only.",
        body_style,
    ))
    story.append(Spacer(1, 6))

    disclaimer_items = [
        ("<b>Scope of Coverage:</b>",
         "This report covers AI model behavioural drift and bias detection across the probe categories "
         "listed. It does not constitute a full conformity assessment under Article 43 of the EU AI Act "
         "and does not replace a Notified Body audit where one is required."),
        ("<b>Methodology Limitation:</b>",
         "Drift scoring is based on semantic cosine similarity using sentence embeddings. It detects "
         "behavioural change relative to an established baseline. A 'PASS' result indicates consistency "
         "with the baseline response — it does not independently certify that the baseline response "
         "itself was unbiased."),
        ("<b>Legal Advice:</b>",
         "This report does not constitute legal advice. For formal compliance assessments, consult a "
         "qualified legal practitioner specialising in EU AI Act and GDPR obligations."),
        ("<b>Data Processing:</b>",
         "Verispect processes only hashed prompt identifiers and mathematical embedding vectors. "
         "No personally identifiable information is transmitted to or stored on Verispect servers. "
         "The operator retains responsibility for data processing compliance under GDPR Article 24."),
        ("<b>Retention:</b>",
         "This report should be retained as part of your AI system's technical documentation "
         "as required under EU AI Act Article 11. Recommended retention period: minimum 10 years "
         "from the date of last use of the AI system."),
    ]
    for label, text in disclaimer_items:
        story.append(Paragraph(label, bold_body))
        story.append(Paragraph(text, body_style))
        story.append(Spacer(1, 4))

    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER))
    story.append(Spacer(1, 10))

    # Sign-off block
    signoff_data = [[
        Paragraph(
            f"<b>Report Reference:</b> VSP-{now.strftime('%Y%m%d-%H%M%S')}<br/>"
            f"<b>Issued to:</b> {client_label}<br/>"
            f"<b>Generated:</b> {generated_str}<br/>"
            f"<b>System:</b> Verispect Automated Compliance Engine v1.0",
            small_style,
        ),
        Paragraph(
            "<b>Verispect</b><br/>"
            "support@verispectai.com<br/>"
            "verispectai.com<br/>"
            "<font color='#6b7280'>This document is system-generated.<br/>"
            "No signature is required.</font>",
            S("sign", fontSize=8, textColor=DARK, alignment=TA_RIGHT),
        ),
    ]]
    so = Table(signoff_data, colWidths=[None, 5*cm])
    so.setStyle(TableStyle([
        ("VALIGN",     (0,0), (-1,-1), "TOP"),
        ("BACKGROUND", (0,0), (-1,-1), GRAY_LT),
        ("BOX",        (0,0), (-1,-1), 0.5, BORDER),
        ("PADDING",    (0,0), (-1,-1), 12),
    ]))
    story.append(so)

    # ── Render ────────────────────────────────────────────────────────────────
    doc.build(story)
    buf.seek(0)

    safe_company = "".join(c for c in client_label if c.isalnum() or c in ("-", "_"))[:30]
    filename = f"verispect-compliance-report-{safe_company}-{now.strftime('%Y%m%d')}.pdf"
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


# ═══════════════════════════════════════════════════════════════════════════════
# AUTH ENDPOINTS  (/auth/*)
# No auth required — these create and return JWT tokens
# ═══════════════════════════════════════════════════════════════════════════════

class RegisterRequest(BaseModel):
    company_name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str


@auth_router.post("/register")
async def register(body: RegisterRequest):
    if len(body.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

    existing = await get_client_by_email(body.email.lower().strip())
    if existing:
        raise HTTPException(status_code=409, detail="An account with this email already exists")

    client_id   = str(uuid.uuid4())
    password_hash = hash_password(body.password)

    await create_client(
        client_id=client_id,
        company_name=body.company_name.strip(),
        email=body.email.lower().strip(),
        password_hash=password_hash,
    )

    # Auto-generate a first API key on registration
    key_value = f"vs_live_{secrets.token_urlsafe(24)}"
    key_id    = str(uuid.uuid4())
    await create_api_key(
        key_id=key_id,
        client_id=client_id,
        key_value=key_value,
        name="Default Key",
    )

    token = create_token(client_id)
    return {
        "token": token,
        "client_id": client_id,
        "company_name": body.company_name.strip(),
        "email": body.email.lower().strip(),
        "api_key": key_value,     # Show once on registration
    }


@auth_router.post("/login")
async def login(body: LoginRequest):
    client = await get_client_by_email(body.email.lower().strip())
    if not client or not verify_password(body.password, client["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_token(client["id"])
    return {
        "token": token,
        "client_id": client["id"],
        "company_name": client["company_name"],
        "email": client["email"],
        "plan": client["plan"],
    }


@auth_router.get("/me")
async def me(client_id: str = Depends(require_auth)):
    client = await get_client_by_id(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Account not found")
    return {
        "client_id": client["id"],
        "company_name": client["company_name"],
        "email": client["email"],
        "plan": client["plan"],
        "created_at": client["created_at"],
    }


# ═══════════════════════════════════════════════════════════════════════════════
# API KEY ENDPOINTS  (/api/keys/*)
# Auth: JWT Bearer token required
# ═══════════════════════════════════════════════════════════════════════════════

class CreateKeyRequest(BaseModel):
    name: str = "New Key"


@keys_router.get("")
async def list_keys(client_id: str = Depends(require_auth)):
    keys = await list_api_keys(client_id)
    # Never return full key value in list — show only prefix + last 4 chars
    safe_keys = []
    for k in keys:
        kv = k["key_value"]
        safe_keys.append({
            "id":           k["id"],
            "name":         k["name"],
            "key_preview":  kv[:12] + "..." + kv[-4:],
            "is_active":    bool(k["is_active"]),
            "created_at":   k["created_at"],
            "last_used_at": k["last_used_at"],
        })
    return safe_keys


@keys_router.post("")
async def create_key(body: CreateKeyRequest, client_id: str = Depends(require_auth)):
    # Check key count — limit to 5 active keys per client
    keys = await list_api_keys(client_id)
    active = [k for k in keys if k["is_active"]]
    if len(active) >= 5:
        raise HTTPException(status_code=400, detail="Maximum 5 active API keys per account")

    key_value = f"vs_live_{secrets.token_urlsafe(24)}"
    key_id    = str(uuid.uuid4())
    await create_api_key(
        key_id=key_id,
        client_id=client_id,
        key_value=key_value,
        name=body.name.strip() or "New Key",
    )
    # Return full key value ONCE at creation — never shown again
    return {
        "id":        key_id,
        "name":      body.name,
        "key_value": key_value,
        "message":   "Copy this key now. It will not be shown again.",
    }


@keys_router.delete("/{key_id}")
async def delete_key(key_id: str, client_id: str = Depends(require_auth)):
    success = await revoke_api_key(key_id, client_id)
    if not success:
        raise HTTPException(status_code=404, detail="Key not found or already revoked")
    return {"status": "revoked"}


# ═══════════════════════════════════════════════════════════════════════════════
# SDK ENDPOINTS  (/api/sdk/*)
# Auth: X-Verispect-Key header validated against api_keys table in DB
# ═══════════════════════════════════════════════════════════════════════════════

async def _get_client_id(request: Request) -> str:
    """Validate SDK key against DB and return client_id. Raises 401 if invalid."""
    key = request.headers.get("X-Verispect-Key", "").strip()
    if not key:
        raise HTTPException(status_code=401, detail="Missing X-Verispect-Key header")
    client_id = await get_client_id_from_key(key)
    if not client_id:
        raise HTTPException(status_code=401, detail="Invalid or revoked API key")
    return client_id


@sdk_router.post("/ingest")
async def sdk_ingest(request: Request):
    """
    Receives a log entry from the SDK after every real API call.
    Payload contains prompt_hash, response_embedding, model, tokens, latency.
    If is_golden=True, also registers the golden probe baseline on the server.

    Raw prompt text is NEVER sent here — only hashes and embedding vectors.
    """
    client_id = _get_client_id(request)
    body = await request.json()

    prompt_hash = body.get("prompt_hash", "")
    response_embedding = body.get("response_embedding", [])
    model = body.get("model", "unknown")
    latency_ms = int(body.get("latency_ms", 0))
    prompt_tokens = int(body.get("prompt_tokens", 0))
    completion_tokens = int(body.get("completion_tokens", 0))
    is_golden = bool(body.get("is_golden", False))

    if not prompt_hash or not response_embedding:
        raise HTTPException(status_code=422, detail="prompt_hash and response_embedding are required")

    # Log the real call (is_canary=0, no drift score for real calls)
    await database.execute(logs_table.insert().values(
        model=model,
        prompt=prompt_hash,          # Store hash — not raw text
        response=None,               # Never store raw response text from SDK
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        latency_ms=latency_ms,
        is_canary=0,
        drift_score=None,
        flagged=0,
        probe_id=None,
        severity=None,
        probe_category=None,
    ))

    # Register golden probe baseline if applicable
    if is_golden:
        golden_id = body.get("golden_id")
        golden_embedding = body.get("golden_embedding", response_embedding)
        if golden_id and golden_embedding:
            await save_golden_probe(
                golden_id=golden_id,
                client_id=client_id,
                prompt_hash=prompt_hash,
                model=model,
                baseline_embedding=golden_embedding,
            )

    return {"status": "ok"}


@sdk_router.get("/probe")
async def sdk_get_probe(request: Request, model: str = "unknown"):
    """
    Returns a probe for the SDK to fire using the client's own OpenAI key.
    70% chance: regulatory probe (bias/consistency from PROBES library).
    30% chance: golden probe (client's own historical prompt to replay).
    Falls back to regulatory if no golden probes exist for this client.
    """
    client_id = _get_client_id(request)

    # Decide probe type
    use_golden = random.random() < 0.30
    if use_golden:
        golden = await get_random_golden_for_client(client_id)
        if golden:
            await increment_golden_replay_count(golden["golden_id"])
            return {
                "type": "golden",
                "probe_id": golden["golden_id"],
                "prompt_hash": golden["prompt_hash"],
            }
        # No golden probes yet — fall through to regulatory

    # Pick a regulatory probe that has a stored baseline
    probes_with_baseline = []
    for p in PROBES:
        baseline = await get_baseline(p["id"])
        if baseline:
            probes_with_baseline.append(p)

    if not probes_with_baseline:
        return {"type": "none", "reason": "no baselines calibrated yet"}

    probe = random.choice(probes_with_baseline)
    return {
        "type": "regulatory",
        "probe_id": probe["id"],
        "messages": probe["messages"],
        "category": probe.get("category", "unknown"),
    }


@sdk_router.post("/probe-result")
async def sdk_probe_result(request: Request):
    """
    Receives the result of a probe fired by the SDK.

    Regulatory probes: response_text is provided → server scores via text comparison.
    Golden probes:     response_embedding is provided → server scores via vector comparison.
    Raw prompt text is never present in either case.
    """
    from scorer import score_drift, score_drift_from_embeddings

    client_id = _get_client_id(request)
    body = await request.json()

    probe_id = body.get("probe_id", "")
    probe_type = body.get("probe_type", "regulatory")
    response_text = body.get("response_text", "")
    response_embedding = body.get("response_embedding", [])
    model = body.get("model", "unknown")
    category = body.get("category", "unknown")

    if not probe_id:
        raise HTTPException(status_code=422, detail="probe_id is required")

    drift_result = None

    if probe_type == "regulatory":
        # Score against stored text baseline
        baseline_text = await get_baseline(probe_id)
        if baseline_text and response_text:
            drift_result = score_drift(baseline_text, response_text)
        else:
            # No baseline yet — store this as the new baseline
            if response_text:
                from database import save_baseline
                await save_baseline(probe_id, model, response_text)
            return {"status": "baseline_stored"}

    elif probe_type == "golden":
        # Score against stored embedding baseline
        golden = await get_golden_probe(probe_id)
        if golden and response_embedding:
            drift_result = score_drift_from_embeddings(
                golden["baseline_embedding"], response_embedding
            )
        else:
            return {"status": "golden_not_found"}

    if not drift_result or drift_result.get("drift_score") is None:
        return {"status": "scoring_failed"}

    # Log probe result to the main logs table (same as canary probes)
    await database.execute(logs_table.insert().values(
        model=model,
        prompt=f"[sdk_probe:{probe_id}]",
        response=response_text if probe_type == "regulatory" else None,
        prompt_tokens=0,
        completion_tokens=0,
        latency_ms=0,
        is_canary=1,
        drift_score=drift_result["drift_score"],
        flagged=int(drift_result["flagged"]),
        probe_id=probe_id,
        severity=drift_result["severity"],
        probe_category=category,
    ))

    status = "DRIFT_DETECTED" if drift_result["flagged"] else "OK"
    return {
        "status": status,
        "drift_score": drift_result["drift_score"],
        "severity": drift_result["severity"],
        "flagged": drift_result["flagged"],
    }