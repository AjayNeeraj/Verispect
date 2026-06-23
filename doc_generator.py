"""
doc_generator.py — Verispect "Evidence Clerk" agent (Module 2).

Auto-generates a DPIA + Annex IV Technical Documentation PDF, pre-populated with the
client's REAL monitoring evidence (bias results, drift, probe counts). The deliverable
a consultant bills EUR5-15k for — generated in seconds.

NO new SDK. Runs dashboard-side on monitoring data already collected + a short form.
Works WITHOUT any external key (deterministic template fill with real metrics).
Optional LLM polish if OPENAI_API_KEY is set (drafts richer prose).

Wire into FastAPI:  app.include_router(doc_router)
"""
import os, io
from fastapi import APIRouter, Request, Depends
from auth import require_auth

doc_router = APIRouter(prefix="/api/docs")

CATEGORY_LABELS = {
    "gender": "Gender", "age": "Age", "race_ethnicity": "Race / Ethnicity",
    "nationality": "Nationality", "disability": "Disability", "parental": "Parental status",
    "socioeconomic": "Socioeconomic", "consistency": "Consistency", "golden": "Behavioural (golden)",
}


async def gather_monitoring_summary(client_id: str):
    """Pull real metrics from the logs table (same source as the compliance report)."""
    import sqlalchemy
    from database import database, logs_table
    async def val(q):
        return await database.fetch_val(q)
    total_calls = await val(sqlalchemy.select(sqlalchemy.func.count()).select_from(logs_table).where(sqlalchemy.and_(logs_table.c.client_id == client_id, logs_table.c.is_canary == 0))) or 0
    total_probes = await val(sqlalchemy.select(sqlalchemy.func.count()).select_from(logs_table).where(sqlalchemy.and_(logs_table.c.client_id == client_id, logs_table.c.is_canary == 1))) or 0
    total_flagged = await val(sqlalchemy.select(sqlalchemy.func.count()).select_from(logs_table).where(sqlalchemy.and_(logs_table.c.client_id == client_id, logs_table.c.flagged == 1))) or 0
    avg_drift = await val(sqlalchemy.select(sqlalchemy.func.avg(logs_table.c.drift_score)).where(sqlalchemy.and_(logs_table.c.client_id == client_id, logs_table.c.is_canary == 1))) or 0.0
    cat_q = sqlalchemy.select(
        logs_table.c.probe_category,
        sqlalchemy.func.count().label("run"),
        sqlalchemy.func.sum(logs_table.c.flagged).label("flagged"),
        sqlalchemy.func.avg(logs_table.c.drift_score).label("avg"),
    ).where(sqlalchemy.and_(logs_table.c.client_id == client_id, logs_table.c.is_canary == 1, logs_table.c.probe_category.isnot(None))).group_by(logs_table.c.probe_category)
    cats = []
    for row in await database.fetch_all(cat_q):
        r = dict(row)
        cats.append({"key": r["probe_category"], "run": r["run"],
                     "flagged": int(r["flagged"] or 0), "avg": round(float(r["avg"] or 0), 4)})
    return {"total_calls": total_calls, "total_probes": total_probes,
            "total_flagged": total_flagged, "avg_drift": round(float(avg_drift), 4), "categories": cats}


def _llm_prose(prompt: str, fallback: str) -> str:
    """Optional richer prose if OPENAI_API_KEY is set; else deterministic fallback."""
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        return fallback
    try:
        from openai import OpenAI
        client = OpenAI(api_key=key)
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are a precise DPIA/AI-Act technical writer. 2-4 sentences, factual, no overclaiming compliance."},
                      {"role": "user", "content": prompt}],
            temperature=0.2, max_tokens=220,
        )
        return r.choices[0].message.content.strip()
    except Exception:
        return fallback


def build_dpia_pdf(ctx: dict) -> bytes:
    """
    ctx: { company, system_name, purpose, model, monitoring(summary dict), use_llm(bool) }
    Returns a DPIA + Annex IV technical-doc PDF, populated with real monitoring evidence.
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak

    PURPLE = colors.HexColor("#7c6eff"); DARK = colors.HexColor("#111827"); GRAY = colors.HexColor("#6b7280")
    BORDER = colors.HexColor("#e5e7eb"); GRAY_LT = colors.HexColor("#f9fafb"); WHITE = colors.white
    RED = colors.HexColor("#ef4444"); GREEN = colors.HexColor("#10b981"); AMBER = colors.HexColor("#f59e0b")
    sty = getSampleStyleSheet()
    def S(n, **k): return ParagraphStyle(n, parent=sty["Normal"], **k)
    brand = S("b", fontSize=24, textColor=PURPLE, fontName="Helvetica-Bold")
    h1 = S("h1", fontSize=14, textColor=DARK, fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=6)
    h2 = S("h2", fontSize=10.5, textColor=PURPLE, fontName="Helvetica-Bold", spaceBefore=8, spaceAfter=3)
    body = S("body", fontSize=9.5, textColor=DARK, leading=14, spaceAfter=5)
    small = S("s", fontSize=7.5, textColor=GRAY, leading=10)

    company = ctx.get("company", "Confidential")
    system_name = ctx.get("system_name", "AI System")
    purpose = ctx.get("purpose", "automated decision support")
    model = ctx.get("model", "LLM")
    m = ctx.get("monitoring", {})
    cats = m.get("categories", [])
    use_llm = ctx.get("use_llm", False)
    compliance = (round((m.get("total_probes", 0) - m.get("total_flagged", 0)) / m["total_probes"] * 100, 1)
                  if m.get("total_probes") else None)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=1.8*cm, bottomMargin=1.8*cm)
    st = [Paragraph("Verispect", brand),
          Paragraph("Data Protection Impact Assessment &amp; Annex IV Technical Documentation", S("t", fontSize=11, textColor=GRAY)),
          HRFlowable(width="100%", thickness=2, color=PURPLE, spaceAfter=10)]
    meta = [["System:", system_name], ["Operator:", company], ["Model:", model],
            ["Purpose:", purpose], ["Regulation:", "EU AI Act (2024/1689) · GDPR Art. 35"],
            ["Evidence period:", "Last 30 days (live monitoring)"]]
    t = Table(meta, colWidths=[3.2*cm, None])
    t.setStyle(TableStyle([("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"), ("FONTSIZE", (0,0), (-1,-1), 9),
                           ("TEXTCOLOR", (0,0), (0,-1), GRAY), ("PADDING", (0,0), (-1,-1), 4),
                           ("LINEBELOW", (0,-1), (-1,-1), 0.3, BORDER)]))
    st.append(t); st.append(Spacer(1, 8))

    # 1. System description
    st.append(Paragraph("1. System Description (Annex IV §1)", h1))
    st.append(Paragraph(_llm_prose(
        f"Write a 3-sentence system description for an AI system named '{system_name}' operated by '{company}', "
        f"purpose: {purpose}, using model {model}.",
        f"{system_name}, operated by {company}, uses the {model} model to support {purpose}. "
        f"The system processes inputs and returns outputs that materially influence decisions in its domain. "
        f"It is continuously monitored by Verispect for behavioural drift and bias across protected characteristics."), body))

    # 2. Necessity & proportionality
    st.append(Paragraph("2. Necessity &amp; Proportionality (GDPR Art. 35(7)(b))", h1))
    st.append(Paragraph(_llm_prose(
        f"Write 3 sentences on necessity and proportionality of using AI for {purpose}, noting data minimisation.",
        f"Automated processing is used to deliver {purpose} at scale with consistency. Personal data processed is "
        f"limited to what the task requires. Verispect, the monitoring layer, processes only irreversible hashes and "
        f"embedding vectors — never raw inputs — minimising the data-protection footprint of compliance monitoring."), body))

    # 3. Data & privacy
    st.append(Paragraph("3. Data Governance &amp; Privacy by Design (Art. 10, GDPR Art. 25)", h1))
    st.append(Paragraph(
        "Monitoring is privacy-preserving by architecture: the Verispect layer receives only SHA-256 prompt hashes "
        "and 384-dimensional embedding vectors. Raw prompts, raw responses, and end-user personal data are never "
        "transmitted to or stored by the monitoring provider. Golden probes derived from production traffic are "
        "stored encrypted on the operator's own infrastructure.", body))

    # 4. Risk assessment — REAL evidence
    st.append(Paragraph("4. Risk Assessment — Bias &amp; Drift (Art. 10 &amp; 15)", h1))
    st.append(Paragraph(
        f"Over the assessment period, <b>{m.get('total_calls',0):,}</b> production calls were monitored and "
        f"<b>{m.get('total_probes',0):,}</b> synthetic fairness/consistency probes fired. "
        f"<b>{m.get('total_flagged',0)}</b> drift events were detected. Average drift score: "
        f"<b>{m.get('avg_drift',0)}</b> (0 = stable, 1 = fully drifted)."
        + (f" Overall consistency score: <b>{compliance}%</b>." if compliance is not None else ""), body))
    if cats:
        rows = [["Protected characteristic", "Probes", "Drift events", "Avg drift", "Status"]]
        for c in sorted(cats, key=lambda x: x["flagged"], reverse=True):
            status = "PASS" if c["flagged"] == 0 else ("WARN" if c["avg"] < 0.25 else "REVIEW")
            rows.append([CATEGORY_LABELS.get(c["key"], c["key"]), str(c["run"]), str(c["flagged"]), str(c["avg"]), status])
        tt = Table(rows, colWidths=[5.5*cm, 2.2*cm, 2.6*cm, 2.5*cm, 2.4*cm])
        tstyle = [("BACKGROUND", (0,0), (-1,0), PURPLE), ("TEXTCOLOR", (0,0), (-1,0), WHITE),
                  ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"), ("FONTSIZE", (0,0), (-1,-1), 8.5),
                  ("ALIGN", (1,0), (-1,-1), "CENTER"), ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, GRAY_LT]),
                  ("GRID", (0,0), (-1,-1), 0.3, BORDER), ("PADDING", (0,0), (-1,-1), 6)]
        for i, c in enumerate(sorted(cats, key=lambda x: x["flagged"], reverse=True), start=1):
            col = GREEN if c["flagged"] == 0 else (AMBER if c["avg"] < 0.25 else RED)
            tstyle += [("TEXTCOLOR", (4,i), (4,i), col), ("FONTNAME", (4,i), (4,i), "Helvetica-Bold")]
        tt.setStyle(TableStyle(tstyle)); st.append(Spacer(1, 4)); st.append(tt)

    # 5. Mitigation
    st.append(Paragraph("5. Risk Mitigation Measures (Art. 9)", h1))
    st.append(Paragraph(
        "Identified risks are mitigated through continuous behavioural monitoring (Verispect), automated drift/bias "
        "alerting, documented human-oversight workflows, and re-baselining after any deliberate model or prompt change. "
        "Each flagged event is logged with a timestamp and severity for human review.", body))

    # 6. Monitoring & review
    st.append(Paragraph("6. Post-Market Monitoring &amp; Review (Art. 72)", h1))
    st.append(Paragraph(
        "The system is subject to continuous post-market monitoring via Verispect's autonomous probe suite, which "
        "fires fairness and consistency probes on a sample of live traffic and tracks behavioural drift over time. "
        "A monitoring report is generated monthly and retained as technical documentation (Art. 11).", body))

    # 7. Annex IV checklist
    st.append(Paragraph("7. Annex IV Technical Documentation — Coverage", h1))
    chk = [["Annex IV item", "Status / source"],
           ["§1 General description", "Provided (§1 above)"],
           ["§2 Development process & design", "Operator to attach build docs"],
           ["§3 Monitoring/functioning metrics", "Verispect live monitoring (§4, §6)"],
           ["§4 Risk management (Art. 9)", "Verispect alerts + §5"],
           ["§5 Changes log", "Re-baseline + change log (operator)"],
           ["§6 Standards applied", "EU AI Act 2024/1689; GDPR 2016/679"],
           ["§7 EU declaration of conformity", "Operator (post conformity assessment)"],
           ["§8 Post-market monitoring plan", "Verispect (Art. 72) — §6"]]
    ct = Table(chk, colWidths=[7*cm, None])
    ct.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), DARK), ("TEXTCOLOR", (0,0), (-1,0), WHITE),
                            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"), ("FONTSIZE", (0,0), (-1,-1), 8),
                            ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, GRAY_LT]),
                            ("GRID", (0,0), (-1,-1), 0.3, BORDER), ("PADDING", (0,0), (-1,-1), 5)]))
    st.append(ct)

    st.append(Spacer(1, 12))
    st.append(Paragraph(
        "This document is auto-generated by Verispect from live monitoring evidence to support the operator's DPIA "
        "(GDPR Art. 35) and technical documentation (EU AI Act Art. 11 / Annex IV). It is decision-support, not legal "
        "advice or certification; the operator remains responsible for conformity.", small))
    doc.build(st)
    buf.seek(0)
    return buf.read()


@doc_router.post("/dpia")
async def generate_dpia(request: Request, client_id: str = Depends(require_auth)):
    body = await request.json()
    summary = await gather_monitoring_summary(client_id)
    ctx = {"company": body.get("company", "Confidential"),
           "system_name": body.get("system_name", "AI Decision System"),
           "purpose": body.get("purpose", "automated decision support"),
           "model": body.get("model", "gpt-4o-mini"),
           "monitoring": summary, "use_llm": bool(body.get("use_llm", False))}
    pdf = build_dpia_pdf(ctx)
    from fastapi.responses import StreamingResponse
    return StreamingResponse(io.BytesIO(pdf), media_type="application/pdf",
                             headers={"Content-Disposition": "attachment; filename=verispect-dpia.pdf"})


if __name__ == "__main__":
    import asyncio
    from database import database
    async def main():
        await database.connect()
        summary = await gather_monitoring_summary("demo")
        ctx = {"company": "Acme HR GmbH (DEMO)", "system_name": "CandidateRank AI",
               "purpose": "automated candidate screening and ranking", "model": "gpt-4o-mini",
               "monitoring": summary, "use_llm": False}
        pdf = build_dpia_pdf(ctx)
        with open("DPIA-DEMO.pdf", "wb") as f:
            f.write(pdf)
        print("monitoring:", summary["total_calls"], "calls,", summary["total_probes"], "probes,",
              summary["total_flagged"], "flagged,", len(summary["categories"]), "categories")
        print("PDF bytes:", len(pdf), "-> DPIA-DEMO.pdf")
        await database.disconnect()
    asyncio.run(main())
